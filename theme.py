#!/usr/bin/env python3
"""theme.py: 글옷(geulot) 글쓰기 테마 엔진. 문서 종류와 독자로 축마다 쓸 규칙을 골라 AI 에게 줄 지침 하나로 조립한다.

글의 모양과 말투를 축 열두 가지로 나누고, 축마다 값을 하나 고른다. 값은 themes/<축>/<값>.md 규칙 문서
하나를 가리킨다. 기본 프리셋(대학생)과 독자, 문서 종류는 themes/defaults.yaml 에 있고, 개인 설정은
~/.config/geulot/themes.yaml 이다. 표준 라이브러리만 쓴다(python3 3.9 이상).

값을 정하는 순서 (위가 이긴다)
  1. 문서 종류가 고정한 축          defaults.yaml 의 kinds
  2. 명령 인자                      --set 축=값
  3. 개인 설정의 독자 프로필         themes.yaml 의 audiences
  4. 문서 종류가 권하는 값           defaults.yaml 의 prefer
  5. 개인 설정의 기본값              themes.yaml 의 defaults
  6. 독자 프로필                    defaults.yaml 의 audiences
  7. 기본 프리셋 (대학생)            defaults.yaml 의 defaults
독자를 주지 않으면 문서 종류의 기본 독자를 쓴다. 독자가 여럿이면 공개 범위는 가장 좁은 쪽,
용어 수준은 가장 풀어 쓴 쪽, 나머지 축은 값을 가진 첫 독자를 따른다.
공개 범위(exposure)는 안전 축이다. 1, 6, 7 단계가 정한 값이 출발점이고, 인자와 개인 설정은 더 좁힐 때만 이긴다.
값 template 은 문서 종류만 고정할 수 있다. 그 축은 themes/kinds/<종류>.md 가 정한다.

사용
  python3 theme.py list [--json]
  python3 theme.py get     [--kind K] [--audience A[,B]] [--set 축=값]... [--json]
  python3 theme.py compose [--kind K] [--audience A[,B]] [--set 축=값]... [--chars N]
                           [--format prompt|output-style] [--html] [-o 파일]
  python3 theme.py set <축> <값> [--audience A]      개인 설정에 쓴다
  python3 theme.py set <축> --unset [--audience A]
  python3 theme.py bundle                            웹 고르개용 docs/themes.json 을 만든다
  python3 theme.py selftest

종료 코드: 0 성공, 3 모르는 종류·독자·축·값, 1 그 밖의 오류.
환경 변수: GEULOT_THEMES_DIR 는 테마 폴더를, GEULOT_PERSONAL 은 개인 설정 파일을 바꾼다.
"""
import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
AXES_ORDER = ("visual-doc", "visual-deck", "voice", "register", "terms", "skeleton", "length",
              "emphasis", "diagram", "sources", "exposure", "ai-disclosure")
# compose 가 규칙을 싣는 순서. 앞에 나온 규칙이 이긴다고 지침 머리에 적는다.
COMPOSE_ORDER = ("exposure", "skeleton", "voice", "register", "terms", "length", "sources",
                 "ai-disclosure", "diagram", "emphasis", "visual-deck", "visual-doc")
EXPOSURE_STRICT = ("public", "submit", "team")   # 앞이 가장 좁다
TERMS_PLAIN = ("everyday", "explained", "major")  # 앞이 가장 풀어 쓴다
TEMPLATE = "template"
PERSONAL_DEFAULT = "~/.config/geulot/themes.yaml"


class Missing(Exception):
    """모르는 종류·독자·축·값. 종료 코드 3."""


# ---------------------------------------------------------------- YAML 부분집합
def _scalar(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        return s[1:-1]
    return s


def _split_top(s):
    parts, depth, cur, quote = [], 0, "", None
    for ch in s:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
            continue
        if ch in "'\"":
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def _value(s):
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        return [_scalar(x) for x in _split_top(s[1:-1])]
    if s.startswith("{") and s.endswith("}"):
        out = {}
        for item in _split_top(s[1:-1]):
            k, _, v = item.partition(":")
            out[_scalar(k)] = _value(v)
        return out
    return _scalar(s)


def _strip_comment(line):
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
    return line


def parse_yaml(text):
    """맨 앞 칸에 절 이름, 들여 쓴 줄에 `키: 값` 하나인 두 단계 YAML 만 읽는다."""
    data, section = {}, None
    for n, raw in enumerate(text.splitlines(), 1):
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        if not line[0].isspace():
            key, _, rest = line.partition(":")
            if rest.strip():
                raise ValueError(f"{n}행: 절 이름 뒤에는 값을 쓰지 않는다")
            section = key.strip()
            data[section] = {}
            continue
        if section is None:
            raise ValueError(f"{n}행: 절 이름보다 들여 쓴 줄이 먼저 나왔다")
        key, sep, rest = line.strip().partition(":")
        if not sep:
            raise ValueError(f"{n}행: `키: 값` 꼴이 아니다")
        data[section][key.strip()] = _value(rest)
    return data


def dump_yaml(data):
    def one(v):
        if isinstance(v, list):
            return "[" + ", ".join(v) + "]"
        if isinstance(v, dict):
            return "{" + ", ".join(f"{k}: {one(x)}" for k, x in v.items()) + "}"
        return str(v)
    lines = []
    for section, body in data.items():
        if not body:
            continue
        lines.append(f"{section}:")
        lines.extend(f"  {k}: {one(v)}" for k, v in body.items())
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- 테마 모음
class Themes:
    def __init__(self, root):
        self.root = Path(root)
        axes = parse_yaml((self.root / "axes.yaml").read_text(encoding="utf-8"))
        conf = parse_yaml((self.root / "defaults.yaml").read_text(encoding="utf-8"))
        self.axes = {}
        for axis in AXES_ORDER:
            body = dict(axes.get(axis, {}))
            label = body.pop("label", axis)
            self.axes[axis] = {"label": label, "values": body}
        self.defaults = conf.get("defaults", {})
        self.audiences = conf.get("audiences", {})
        self.kinds = conf.get("kinds", {})
        self.prefer = conf.get("prefer", {})

    def rule_path(self, axis, value):
        if value == TEMPLATE:
            return None
        return self.root / axis / f"{value}.md"

    def kind_path(self, kind):
        return self.root / "kinds" / f"{kind}.md"

    def known(self, axis, value, allow_template=False):
        if axis not in self.axes:
            raise Missing(f"모르는 축: {axis}")
        if value == TEMPLATE:
            if allow_template:
                return
            raise Missing(f"{axis}=template 은 문서 종류만 고정할 수 있다")
        if value not in self.axes[axis]["values"]:
            raise Missing(f"모르는 값: {axis}={value}. 고를 수 있는 값은 {', '.join(self.axes[axis]['values'])}")

    def label(self, axis, value):
        if value == TEMPLATE:
            return "문서 종류의 틀"
        return self.axes[axis]["values"].get(value, value)


def personal_path():
    return Path(os.path.expanduser(os.environ.get("GEULOT_PERSONAL", PERSONAL_DEFAULT)))


def load_personal(warn):
    p = personal_path()
    if not p.exists():
        return {}
    try:
        return parse_yaml(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        warn(f"개인 설정을 읽지 못해 무시한다: {p}: {e}")
        return {}


# ---------------------------------------------------------------- 값 정하기
def _from_audiences(axis, auds, table):
    vals = [table[a][axis] for a in auds if a in table and axis in table[a]]
    if not vals:
        return None
    if axis == "exposure":
        return min(vals, key=EXPOSURE_STRICT.index)
    if axis == "terms":
        return min(vals, key=TERMS_PLAIN.index)
    return vals[0]


def resolve(th, kind=None, audiences=None, sets=None, personal=None, warn=lambda m: None):
    """축마다 (값, 출처) 를 돌려준다. 출처: kind · arg · personal-audience · prefer · personal · audience · default."""
    sets = sets or {}
    personal = personal or {}
    if kind is not None and kind not in th.kinds:
        raise Missing(f"모르는 문서 종류: {kind}. 고를 수 있는 종류는 {', '.join(th.kinds)}")
    kspec = th.kinds.get(kind, {}) if kind else {}
    auds = list(audiences or kspec.get("audience", []) or [])
    for a in auds:
        if a not in th.audiences:
            raise Missing(f"모르는 독자: {a}. 고를 수 있는 독자는 {', '.join(th.audiences)}")
    for axis, value in sets.items():
        th.known(axis, value)

    p_defaults = personal.get("defaults", {})
    p_auds = personal.get("audiences", {})
    prefer = th.prefer.get(kind, {}) if kind else {}
    out = {}
    for axis in AXES_ORDER:
        fixed = kspec.get(axis)
        if axis == "exposure":
            base, src = None, None
            for cand, s in ((fixed, "kind"), (_from_audiences(axis, auds, th.audiences), "audience"),
                            (th.defaults.get(axis), "default")):
                if cand:
                    base, src = cand, s
                    break
            for cand, s in ((sets.get(axis), "arg"), (_from_audiences(axis, auds, p_auds), "personal-audience"),
                            (p_defaults.get(axis), "personal")):
                if not cand or cand not in EXPOSURE_STRICT:
                    continue
                if EXPOSURE_STRICT.index(cand) < EXPOSURE_STRICT.index(base):
                    base, src = cand, s
                elif cand != base:
                    warn(f"공개 범위는 넓힐 수 없어 {s} 의 {cand} 를 버리고 {base} 를 쓴다")
            out[axis] = (base, src)
            continue
        if fixed:
            if axis in sets and sets[axis] != fixed:
                warn(f"{axis} 는 문서 종류가 {fixed} 로 고정해 인자 {sets[axis]} 를 쓰지 않는다")
            out[axis] = (fixed, "kind")
            continue
        chain = (
            (sets.get(axis), "arg"),
            (_from_audiences(axis, auds, p_auds), "personal-audience"),
            (prefer.get(axis), "prefer"),
            (p_defaults.get(axis), "personal"),
            (_from_audiences(axis, auds, th.audiences), "audience"),
            (th.defaults.get(axis), "default"),
        )
        for cand, src in chain:
            if not cand:
                continue
            if src.startswith("personal") and (cand == TEMPLATE or cand not in th.axes[axis]["values"]):
                warn(f"개인 설정의 {axis}={cand} 는 모르는 값이라 건너뛴다")
                continue
            out[axis] = (cand, src)
            break
        else:
            raise Missing(f"{axis} 의 값을 정하지 못했다. defaults.yaml 의 defaults 를 확인한다")
    return out, auds


# ---------------------------------------------------------------- 조립
SAMPLE_HEAD = "\n## 보기\n"


def _split(path):
    text = path.read_text(encoding="utf-8").strip() + "\n"
    rule, _, sample = text.partition(SAMPLE_HEAD)
    return rule.strip(), sample.strip()


def _sample(path):
    return _split(path)[1]


def _body(path):
    """규칙 문서에서 첫 머리말과 `## 보기` 절을 뺀 규칙 본문. 보기는 웹 고르개만 쓴다."""
    lines = _split(path)[0].splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(lines).strip()


def compose(th, kind=None, audiences=None, sets=None, personal=None, chars=None, fmt="prompt",
            html=False, warn=lambda m: None):
    vals, auds = resolve(th, kind, audiences, sets, personal, warn)
    kind_label = th.kinds[kind]["label"] if kind else "일반 글"
    aud_label = ", ".join(th.audiences[a]["label"] for a in auds) or "정하지 않음"
    parts = [
        f"# 글쓰기 테마 · {kind_label} · 독자 {aud_label}",
        "이 대화에서 쓰는 글에 아래 규칙을 적용한다. 규칙끼리 부딪치면 앞에 나온 규칙을 따른다. "
        "이 지침은 geulot 로 조립했다.",
        "## 공통 바닥\n\n" + _body(th.root / "base.md"),
    ]
    if kind:
        parts.append(f"## 문서 종류 · {kind_label}\n\n" + _body(th.kind_path(kind)))
    for axis in COMPOSE_ORDER:
        value, _ = vals[axis]
        if value == TEMPLATE:
            continue
        if axis == "visual-deck" and kind != "slides":
            continue
        if axis == "visual-doc" and not html:
            continue
        head = f"## {th.axes[axis]['label']} · {th.label(axis, value)}"
        parts.append(head + "\n\n" + _body(th.rule_path(axis, value)))
        if axis == "length" and chars:
            parts.append(
                f"## 글자수 · 공백 포함 {chars}자 이내\n\n"
                f"- 본문은 공백 포함 {chars}자를 넘기지 않는다. 넘치면 근거가 약한 문장부터 뺀다.\n"
                "- 다 쓴 뒤 끝에 `(공백 포함 n자)` 로 센 값을 적는다.\n"
                "- AI 가 센 글자수는 틀리기 쉽다. 제출 전에 글자수 세기 도구로 다시 잰다.")
    text = "\n\n".join(parts) + "\n"
    if fmt == "output-style":
        name = f"{kind_label} ({aud_label})"
        text = ("---\n"
                f"name: {name}\n"
                f"description: geulot 로 조립한 글쓰기 테마. {kind_label}, 독자 {aud_label}\n"
                "keep-coding-instructions: true\n"
                "---\n\n") + text
    return text, vals


# ---------------------------------------------------------------- 웹 묶음
def bundle_data(th):
    rules, samples, css = {}, {}, {}
    for axis in AXES_ORDER:
        for value in th.axes[axis]["values"]:
            rules[f"{axis}/{value}"] = _body(th.rule_path(axis, value))
            samples[f"{axis}/{value}"] = _sample(th.rule_path(axis, value))
    for value in th.axes["visual-doc"]["values"]:
        f = th.root / "visual-doc" / value / "theme.css"
        if f.exists():
            css[value] = f.read_text(encoding="utf-8")
    return {
        "axesOrder": list(AXES_ORDER),
        "composeOrder": list(COMPOSE_ORDER),
        "exposureStrict": list(EXPOSURE_STRICT),
        "termsPlain": list(TERMS_PLAIN),
        "axes": th.axes,
        "defaults": th.defaults,
        "audiences": th.audiences,
        "kinds": th.kinds,
        "prefer": th.prefer,
        "base": _body(th.root / "base.md"),
        "kindText": {k: _body(th.kind_path(k)) for k in th.kinds},
        "rules": rules,
        "samples": samples,
        "css": css,
    }


def bundle_text(th):
    return json.dumps(bundle_data(th), ensure_ascii=False, indent=1) + "\n"


# ---------------------------------------------------------------- 명령
def themes_root():
    return Path(os.environ.get("GEULOT_THEMES_DIR", HERE / "themes"))


def _sets(items):
    out = {}
    for it in items or []:
        axis, sep, value = it.partition("=")
        if not sep:
            raise Missing(f"--set 은 축=값 꼴이다: {it}")
        out[axis.strip()] = value.strip()
    return out


def _auds(s):
    return [a.strip() for a in s.split(",") if a.strip()] if s else None


def warn_stderr(msg):
    print(f"경고: {msg}", file=sys.stderr)


def cmd_list(a, th):
    if a.json:
        print(json.dumps({"axes": th.axes, "audiences": th.audiences, "kinds": th.kinds,
                          "defaults": th.defaults}, ensure_ascii=False, indent=1))
        return 0
    print("문서 종류")
    for k, v in th.kinds.items():
        print(f"  {k:<10} {v.get('label', k)}")
    print("독자")
    for k, v in th.audiences.items():
        print(f"  {k:<10} {v.get('label', k)}")
    print("축과 값 (* 는 기본 프리셋 값)")
    for axis in AXES_ORDER:
        vals = ", ".join(("*" if th.defaults.get(axis) == v else "") + f"{v}={lab}"
                         for v, lab in th.axes[axis]["values"].items())
        print(f"  {axis:<14} {th.axes[axis]['label']}: {vals}")
    return 0


def cmd_get(a, th):
    vals, auds = resolve(th, a.kind, _auds(a.audience), _sets(a.set), load_personal(warn_stderr), warn_stderr)
    if a.json:
        print(json.dumps({"kind": a.kind, "audiences": auds, "axes": {
            ax: {"value": v, "label": th.label(ax, v), "source": s,
                 "rule": str(th.rule_path(ax, v)) if th.rule_path(ax, v) else None}
            for ax, (v, s) in vals.items()}}, ensure_ascii=False, indent=1))
        return 0
    for ax, (v, s) in vals.items():
        print(f"{ax}\t{v}\t{s}\t{th.label(ax, v)}")
    return 0


def cmd_compose(a, th):
    text, _ = compose(th, a.kind, _auds(a.audience), _sets(a.set), load_personal(warn_stderr),
                      a.chars, a.format, a.html, warn_stderr)
    if a.output:
        Path(a.output).expanduser().write_text(text, encoding="utf-8")
        print(f"썼다: {a.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


def cmd_set(a, th):
    if a.unset == (a.value is not None):
        raise Missing("값을 주거나 --unset 중 하나만 쓴다")
    if a.value is not None:
        th.known(a.axis, a.value)
    elif a.axis not in th.axes:
        raise Missing(f"모르는 축: {a.axis}")
    if a.audience and a.audience not in th.audiences:
        raise Missing(f"모르는 독자: {a.audience}")
    p = personal_path()
    data = load_personal(warn_stderr)
    data.setdefault("defaults", {})
    data.setdefault("audiences", {})
    if a.audience:
        prof = data["audiences"].setdefault(a.audience, {})
        target = prof if isinstance(prof, dict) else {}
        data["audiences"][a.audience] = target
    else:
        target = data["defaults"]
    if a.unset:
        target.pop(a.axis, None)
        if a.audience and not target:
            data["audiences"].pop(a.audience)
    else:
        target[a.axis] = a.value
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dump_yaml(data), encoding="utf-8")
    where = f"독자 {a.audience}" if a.audience else "기본값"
    print(f"개인 설정 {p} 의 {where} 에 {a.axis}={'(지움)' if a.unset else a.value}")
    return 0


def cmd_bundle(a, th):
    out = HERE / "docs" / "themes.json"
    out.write_text(bundle_text(th), encoding="utf-8")
    print(f"썼다: {out}")
    return 0


def selftest(th):
    problems = []

    def check(cond, msg):
        if not cond:
            problems.append(msg)

    for axis in AXES_ORDER:
        check(th.axes[axis]["values"], f"{axis} 에 값이 없다")
        for v in th.axes[axis]["values"]:
            check(th.rule_path(axis, v).exists(), f"규칙 문서가 없다: {axis}/{v}.md")
        d = th.root / axis
        if d.is_dir():
            for f in d.glob("*.md"):
                check(f.stem in th.axes[axis]["values"], f"axes.yaml 에 없는 규칙 문서: {axis}/{f.name}")
        check(th.defaults.get(axis) in th.axes[axis]["values"], f"defaults 의 {axis} 값이 없거나 모르는 값이다")
    check((th.root / "base.md").exists(), "base.md 가 없다")
    for axis in AXES_ORDER:
        for v in th.axes[axis]["values"]:
            p = th.rule_path(axis, v)
            if not p.exists():
                continue
            sample = _sample(p)
            check(sample, f"보기 절이 없다: {axis}/{v}.md")
            check("## 보기" not in _body(p), f"규칙 본문에 보기가 섞였다: {axis}/{v}.md")
            if axis == "visual-deck":
                m = re.search(r"```json\n(.*?)\n```", sample, re.S)
                try:
                    tok = json.loads(m.group(1)) if m else {}
                except ValueError:
                    tok = {}
                check({"bg", "ink", "accent"} <= set(tok), f"발표 디자인 보기에 bg, ink, accent 색이 없다: {v}.md")
        if axis == "visual-doc":
            for v in th.axes[axis]["values"]:
                check((th.root / axis / v / "theme.css").exists(), f"CSS 가 없다: visual-doc/{v}/theme.css")

    def check_profile(name, prof, allow_template):
        for k, v in prof.items():
            if k in ("label", "audience"):
                continue
            try:
                th.known(k, v, allow_template)
            except Missing as e:
                problems.append(f"{name}: {e}")

    for k, v in th.audiences.items():
        check("label" in v, f"독자 {k} 에 label 이 없다")
        check_profile(f"독자 {k}", v, False)
    for k, v in th.kinds.items():
        check("label" in v, f"종류 {k} 에 label 이 없다")
        check(th.kind_path(k).exists(), f"종류 문서가 없다: kinds/{k}.md")
        for a in v.get("audience", []):
            check(a in th.audiences, f"종류 {k} 의 기본 독자 {a} 를 모른다")
        check_profile(f"종류 {k}", v, True)
    for k, v in th.prefer.items():
        check(k in th.kinds, f"prefer 의 {k} 는 모르는 종류다")
        check_profile(f"prefer {k}", v, False)

    # 동작 계약
    try:
        for k in th.kinds:
            text, vals = compose(th, kind=k)
            check(text.startswith("# 글쓰기 테마"), f"{k} 조립 결과의 머리가 다르다")
            check("[확인 필요" in text, f"{k} 조립 결과에 공통 바닥이 빠졌다")
        vals, _ = resolve(th, kind="report", sets={"skeleton": "chrono"})
        check(vals["skeleton"] == ("chrono", "arg"), "인자가 권하는 값을 이기지 못한다")
        vals, _ = resolve(th, kind="resume", sets={"skeleton": "bluf"})
        check(vals["skeleton"] == ("template", "kind"), "인자가 종류가 고정한 축을 바꿨다")
        vals, _ = resolve(th, kind="teamwork", sets={"exposure": "public"})
        check(vals["exposure"][0] == "public", "공개 범위를 좁히는 인자가 졌다")
        vals, _ = resolve(th, kind="report", sets={"exposure": "team"})
        check(vals["exposure"][0] == "submit", "공개 범위를 넓히는 인자가 이겼다")
        vals, _ = resolve(th, kind="report", personal={"defaults": {"skeleton": "chrono"}})
        check(vals["skeleton"] == ("imrad", "prefer"), "개인 기본값이 종류가 권하는 값을 이겼다")
        vals, _ = resolve(th, kind="report", personal={"audiences": {"professor": {"skeleton": "pcs"}}})
        check(vals["skeleton"] == ("pcs", "personal-audience"), "개인 독자 프로필이 권하는 값을 이기지 못한다")
        vals, _ = resolve(th, audiences=["teammate", "professor"])
        check(vals["exposure"][0] == "submit" and vals["terms"][0] == "explained", "독자 여럿의 합치기가 다르다")
        text, _ = compose(th, kind="report", chars=1000, fmt="output-style")
        check(text.startswith("---\nname:") and "공백 포함 1000자" in text, "output-style 이나 글자수 조립이 다르다")
        for bad in ({"skeleton": "template"}, {"nope": "x"}, {"voice": "nope"}):
            try:
                resolve(th, sets=bad)
                problems.append(f"잘못된 인자 {bad} 를 받았다")
            except Missing:
                pass
    except Missing as e:
        problems.append(f"동작 계약 중 오류: {e}")

    # 개인 설정 쓰기와 읽기
    with tempfile.TemporaryDirectory() as td:
        old = os.environ.get("GEULOT_PERSONAL")
        os.environ["GEULOT_PERSONAL"] = str(Path(td) / "themes.yaml")
        try:
            ns = argparse.Namespace(axis="register", value="haeyo", unset=False, audience="professor")
            sys_stdout, sys.stdout = sys.stdout, open(os.devnull, "w")
            try:
                cmd_set(ns, th)
            finally:
                sys.stdout.close()
                sys.stdout = sys_stdout
            vals, _ = resolve(th, kind="report", personal=load_personal(lambda m: None))
            check(vals["register"] == ("haeyo", "personal-audience"), "set 으로 쓴 개인 설정을 읽지 못한다")
        finally:
            if old is None:
                os.environ.pop("GEULOT_PERSONAL", None)
            else:
                os.environ["GEULOT_PERSONAL"] = old

    web = HERE / "docs" / "themes.json"
    if (HERE / "docs").is_dir() and th.root.resolve() == (HERE / "themes").resolve():
        check(web.exists() and web.read_text(encoding="utf-8") == bundle_text(th),
              "docs/themes.json 이 테마와 다르다. python3 theme.py bundle 을 돌린다")

    for p in problems:
        print(f"✗ {p}")
    print("selftest 통과" if not problems else f"selftest 실패 {len(problems)}건")
    return 0 if not problems else 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="theme.py", description="글옷: AI 글쓰기 테마 엔진")
    sub = ap.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list")
    li.add_argument("--json", action="store_true")
    for name in ("get", "compose"):
        p = sub.add_parser(name)
        p.add_argument("--kind")
        p.add_argument("--audience")
        p.add_argument("--set", action="append", metavar="축=값")
        if name == "get":
            p.add_argument("--json", action="store_true")
        else:
            p.add_argument("--chars", type=int)
            p.add_argument("--format", choices=("prompt", "output-style"), default="prompt")
            p.add_argument("--html", action="store_true", help="문서 디자인 규칙도 싣는다")
            p.add_argument("-o", "--output")
    s = sub.add_parser("set")
    s.add_argument("axis")
    s.add_argument("value", nargs="?")
    s.add_argument("--unset", action="store_true")
    s.add_argument("--audience")
    sub.add_parser("bundle")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    try:
        th = Themes(themes_root())
        if a.cmd == "selftest":
            return selftest(th)
        return {"list": cmd_list, "get": cmd_get, "compose": cmd_compose,
                "set": cmd_set, "bundle": cmd_bundle}[a.cmd](a, th)
    except Missing as e:
        print(f"오류: {e}", file=sys.stderr)
        return 3
    except (OSError, ValueError) as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
