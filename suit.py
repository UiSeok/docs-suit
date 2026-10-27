#!/usr/bin/env python3
"""suit.py: docs-suit 글쓰기 테마 엔진. 문서에 입힐 옷(테마)을 골라 AI 에게 줄 지침 한 장으로 조립한다.

글의 모양과 말투를 축 열두 가지로 나누고, 축마다 값을 하나 고른다. 값은 themes/<언어>/<축>/<값>.md 규칙 문서
하나를 가리킨다. 처음 받으면 bootstrap 으로 클래스(직업)와 페르소나를 정해 프로필을 만든다. 프로필은
~/.config/docs-suit/profile.yaml 에 있고 저장소 밖이라 커밋되지 않는다. 표준 라이브러리만 쓴다(python3 3.9 이상).

값을 정하는 순서 (위가 이긴다)
  1. 문서 종류가 고정한 축          defaults.yaml 의 kinds
  2. 명령 인자                      --set 축=값
  3. 프로필의 독자별 값              profile.yaml 의 audiences
  4. 문서 종류가 권하는 값           defaults.yaml 의 prefer
  5. 프로필의 기본값                 profile.yaml 의 defaults
  6. 독자 프로필                    defaults.yaml 의 audiences
  7. 클래스 기본값                  classes/<클래스>.yaml 의 defaults
  8. 중립 기본값                    defaults.yaml 의 defaults
클래스는 --class 인자가 있으면 그것을, 없으면 프로필의 클래스를 쓴다. 독자를 주지 않으면 문서 종류의 기본 독자를 쓴다.
독자가 여럿이면 공개 범위는 가장 좁은 쪽, 용어 수준은 가장 풀어 쓴 쪽, 나머지 축은 값을 가진 첫 독자를 따른다.
공개 범위(exposure)는 안전 축이다. 1, 6, 7, 8 단계가 정한 값이 출발점이고, 인자와 프로필은 더 좁힐 때만 이긴다.
값 template 은 문서 종류만 고정할 수 있다. 그 축은 themes/<언어>/kinds/<종류>.md 의 틀이 정한다.

사용
  python3 suit.py bootstrap                             처음 세팅. 클래스와 페르소나를 묻고 프로필을 만든다
  python3 suit.py bootstrap --class C [--call …] [--affiliation …] [--goal …] [--docs a,b]
                            [--facts …] [--dislikes …] [--agents a,b] --yes [--force]
  python3 suit.py bootstrap --questions                 에이전트가 대신 물을 때 쓸 질문 목록
  python3 suit.py profile                               프로필 보기
  python3 suit.py list [--classes] [--json]
  python3 suit.py get     [--class C] [--kind K] [--audience A[,B]] [--set 축=값]... [--json]
  python3 suit.py compose [--class C] [--kind K] [--audience A[,B]] [--set 축=값]... [--chars N]
                          [--format prompt|output-style] [--html] [-o 파일]
  python3 suit.py set <축> <값> [--audience A]       프로필에 쓴다
  python3 suit.py set <축> --unset [--audience A]
  python3 suit.py export --agent claude,agents,gemini,cursor,grok,web|all [--dest 폴더] [--dry-run]
  python3 suit.py bundle                            웹 고르개용 docs/themes.json 을 만든다
  python3 suit.py selftest

종료 코드: 0 성공, 3 모르는 클래스·종류·독자·축·값, 1 그 밖의 오류.
환경 변수: DOCS_SUIT_THEMES 는 테마 폴더를, DOCS_SUIT_PROFILE 은 프로필 파일을 바꾼다.
"""
import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_LANG = "ko"
AXES_ORDER = ("visual-doc", "visual-deck", "voice", "register", "terms", "skeleton", "length",
              "emphasis", "diagram", "sources", "exposure", "ai-disclosure")
# compose 가 규칙을 싣는 순서. 앞에 나온 규칙이 이긴다고 지침 머리에 적는다.
COMPOSE_ORDER = ("exposure", "skeleton", "voice", "register", "terms", "length", "sources",
                 "ai-disclosure", "diagram", "emphasis", "visual-deck", "visual-doc")
EXPOSURE_STRICT = ("public", "submit", "team")   # 앞이 가장 좁다
TERMS_PLAIN = ("everyday", "explained", "major")  # 앞이 가장 풀어 쓴다
TEMPLATE = "template"
PROFILE_DEFAULT = "~/.config/docs-suit/profile.yaml"
PERSONA_IN_PROMPT = ("call", "affiliation", "goal", "facts", "dislikes")  # docs 는 싣지 않는다
EXPORT_MARK = "<!-- docs-suit export 가 만든 파일이다."
# 에이전트마다 SKILL.md 를 놓는 자리. checked 가 False 인 자리는 2차 자료 기준이라 쓰기 전에 안내한다.
AGENT_TARGETS = {
    "claude": {"label": "Claude Code", "path": "~/.claude/skills/docs-suit/SKILL.md", "checked": True},
    "agents": {"label": "Agent Skills 공용 자리 (Codex 등)", "path": "~/.agents/skills/docs-suit/SKILL.md", "checked": False},
    "gemini": {"label": "Gemini CLI", "path": "~/.gemini/skills/docs-suit/SKILL.md", "checked": False},
    "cursor": {"label": "Cursor", "path": "~/.cursor/skills/docs-suit/SKILL.md", "checked": False},
    "web": {"label": "웹 채팅에 붙여 넣을 지침", "path": "~/.config/docs-suit/prompt.md", "checked": True},
}
AGENT_ALIASES = {"grok": ["claude", "agents"], "codex": ["agents"], "all": list(AGENT_TARGETS)}


class Missing(Exception):
    """모르는 클래스·종류·독자·축·값. 종료 코드 3."""


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


def _quote(v):
    v = str(v)
    if v == "" or v != v.strip() or any(c in v for c in ",:#[]{}'\""):
        return '"' + v.replace('"', "”") + '"'
    return v


def dump_yaml(data):
    def one(v):
        if isinstance(v, list):
            return "[" + ", ".join(_quote(x) for x in v) + "]"
        if isinstance(v, dict):
            return "{" + ", ".join(f"{k}: {one(x)}" for k, x in v.items()) + "}"
        return _quote(v)
    lines = ["# docs-suit 프로필. suit.py bootstrap 과 set 이 쓴다. 손으로 고쳐도 된다.", ""]
    for section, body in data.items():
        if not body:
            continue
        lines.append(f"{section}:")
        lines.extend(f"  {k}: {one(v)}" for k, v in body.items())
        lines.append("")
    return "\n".join(lines)


def clean_text(s):
    """프로필에 남길 한 줄 답. 줄바꿈을 걷고 큰따옴표를 바꿔 YAML 부분집합이 깨지지 않게 한다."""
    return " ".join(str(s).replace('"', "”").split())


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
        self.classes = {}
        found = []
        for f in (self.root / "classes").glob("*.yaml"):
            c = parse_yaml(f.read_text(encoding="utf-8"))
            found.append((int(c.get("class", {}).get("order", 99)), f.stem, c))
        for _, stem, c in sorted(found):
            f = Path(stem)
            meta = c.get("class", {})
            self.classes[f.stem] = {"label": meta.get("label", f.stem), "desc": meta.get("desc", ""),
                                    "kinds": meta.get("kinds", []), "defaults": c.get("defaults", {})}
        pq = self.root / "persona.yaml"
        self.persona = parse_yaml(pq.read_text(encoding="utf-8")).get("questions", {}) if pq.exists() else {}

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

    def known_class(self, cls):
        if cls not in self.classes:
            raise Missing(f"모르는 클래스: {cls}. 고를 수 있는 클래스는 {', '.join(self.classes)}")

    def label(self, axis, value):
        if value == TEMPLATE:
            return "문서 종류의 틀"
        return self.axes[axis]["values"].get(value, value)


def profile_path():
    return Path(os.path.expanduser(os.environ.get("DOCS_SUIT_PROFILE", PROFILE_DEFAULT)))


def load_profile(warn=lambda m: None):
    p = profile_path()
    if not p.exists():
        return {}
    try:
        return parse_yaml(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        warn(f"프로필을 읽지 못해 무시한다: {p}: {e}")
        return {}


def write_profile(data):
    p = profile_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dump_yaml(data), encoding="utf-8")
    return p


# ---------------------------------------------------------------- 값 정하기
def _from_audiences(axis, auds, table):
    vals = [table[a][axis] for a in auds if a in table and isinstance(table[a], dict) and axis in table[a]]
    if not vals:
        return None
    if axis == "exposure":
        return min(vals, key=EXPOSURE_STRICT.index)
    if axis == "terms":
        return min(vals, key=TERMS_PLAIN.index)
    return vals[0]


def resolve(th, kind=None, audiences=None, sets=None, profile=None, cls=None, warn=lambda m: None):
    """축마다 (값, 출처) 와 쓴 독자, 쓴 클래스를 돌려준다.
    출처: kind · arg · profile-audience · prefer · profile · audience · class · default."""
    sets = sets or {}
    profile = profile or {}
    cls = cls or profile.get("profile", {}).get("class") or None
    if cls:
        th.known_class(cls)
    if kind is not None and kind not in th.kinds:
        raise Missing(f"모르는 문서 종류: {kind}. 고를 수 있는 종류는 {', '.join(th.kinds)}")
    kspec = th.kinds.get(kind, {}) if kind else {}
    auds = list(audiences or kspec.get("audience", []) or [])
    for a in auds:
        if a not in th.audiences:
            raise Missing(f"모르는 독자: {a}. 고를 수 있는 독자는 {', '.join(th.audiences)}")
    for axis, value in sets.items():
        th.known(axis, value)

    p_defaults = profile.get("defaults", {})
    p_auds = profile.get("audiences", {})
    prefer = th.prefer.get(kind, {}) if kind else {}
    cdef = th.classes[cls]["defaults"] if cls else {}
    out = {}
    for axis in AXES_ORDER:
        fixed = kspec.get(axis)
        if axis == "exposure":
            base, src = None, None
            for cand, s in ((fixed, "kind"), (_from_audiences(axis, auds, th.audiences), "audience"),
                            (cdef.get(axis), "class"), (th.defaults.get(axis), "default")):
                if cand:
                    base, src = cand, s
                    break
            for cand, s in ((sets.get(axis), "arg"), (_from_audiences(axis, auds, p_auds), "profile-audience"),
                            (p_defaults.get(axis), "profile")):
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
            (_from_audiences(axis, auds, p_auds), "profile-audience"),
            (prefer.get(axis), "prefer"),
            (p_defaults.get(axis), "profile"),
            (_from_audiences(axis, auds, th.audiences), "audience"),
            (cdef.get(axis), "class"),
            (th.defaults.get(axis), "default"),
        )
        for cand, src in chain:
            if not cand:
                continue
            if src.startswith("profile") and (cand == TEMPLATE or cand not in th.axes[axis]["values"]):
                warn(f"프로필의 {axis}={cand} 는 모르는 값이라 건너뛴다")
                continue
            out[axis] = (cand, src)
            break
        else:
            raise Missing(f"{axis} 의 값을 정하지 못했다. defaults.yaml 의 defaults 를 확인한다")
    return out, auds, cls


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


def persona_section(th, cls, persona):
    """쓰는 사람 절. 클래스도 페르소나도 없으면 빈 문자열."""
    persona = persona or {}
    rows = []
    if cls:
        rows.append(f"- 클래스: {th.classes[cls]['label']}")
    for key in PERSONA_IN_PROMPT:
        val = persona.get(key)
        if val:
            label = th.persona.get(key, {}).get("label", key)
            rows.append(f"- {label}: {val}")
    if not rows:
        return ""
    return ("## 쓰는 사람\n\n"
            "이 글을 쓰는 사람에 대한 맥락이다. 관점과 예시, 말투를 고르는 데만 쓰고, "
            "사용자가 넣으라고 하지 않는 한 본문에 옮겨 적지 않는다.\n\n" + "\n".join(rows))


def compose(th, kind=None, audiences=None, sets=None, profile=None, cls=None, chars=None, fmt="prompt",
            html=False, warn=lambda m: None):
    profile = profile or {}
    vals, auds, cls = resolve(th, kind, audiences, sets, profile, cls, warn)
    kind_label = th.kinds[kind]["label"] if kind else "일반 글"
    aud_label = ", ".join(th.audiences[a]["label"] for a in auds) or "정하지 않음"
    parts = [
        f"# 글쓰기 테마 · {kind_label} · 독자 {aud_label}",
        "이 대화에서 쓰는 글에 아래 규칙을 적용한다. 규칙끼리 부딪치면 앞에 나온 규칙을 따른다. "
        "이 지침은 docs-suit 로 조립했다.",
        "## 공통 바닥\n\n" + _body(th.root / "base.md"),
    ]
    who = persona_section(th, cls, profile.get("persona"))
    if who:
        parts.append(who)
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
        text = ("---\n"
                f"name: {kind_label} ({aud_label})\n"
                f"description: docs-suit 로 조립한 글쓰기 테마. {kind_label}, 독자 {aud_label}\n"
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
        "personaInPrompt": list(PERSONA_IN_PROMPT),
        "axes": th.axes,
        "defaults": th.defaults,
        "audiences": th.audiences,
        "kinds": th.kinds,
        "prefer": th.prefer,
        "classes": th.classes,
        "persona": th.persona,
        "base": _body(th.root / "base.md"),
        "kindText": {k: _body(th.kind_path(k)) for k in th.kinds},
        "rules": rules,
        "samples": samples,
        "css": css,
    }


def bundle_text(th):
    return json.dumps(bundle_data(th), ensure_ascii=False, indent=1) + "\n"


# ---------------------------------------------------------------- 내보내기
def skill_text(th):
    suit = HERE / "suit.py"
    run = f"python3 {suit}"
    kinds = ", ".join(f"`{k}` {v['label']}" for k, v in th.kinds.items())
    return f"""---
name: docs-suit
description: 문서를 쓰거나 다듬을 때 docs-suit 테마를 입힌다. 보고서, 발표 자료, 회의록, 메일, 이력서, 자기소개서, 포트폴리오, 논문 초록, 설계 문서, PR 설명, 기획서, 업무 보고, 블로그, 뉴스레터, SNS 글을 써 달라는 요청을 받으면 쓰기 전에 이 스킬로 규칙을 조립해 따른다.
---
{EXPORT_MARK} 다시 만들려면 `{run} export` 를 돌린다. -->

# docs-suit

엔진은 `{run}` 이다. 출력은 마크다운 지침 한 장이고, 어떤 에이전트든 그대로 따르면 된다.

1. `{run} profile` 로 프로필이 있는지 본다. 없으면 사용자와 bootstrap 을 대신 진행한다.
   - `{run} list --classes` 로 클래스 일곱 가지를 보여 주고 하나 고르게 한다.
   - `{run} bootstrap --questions` 가 내는 페르소나 질문을 차례로 묻는다. 답하기 싫은 질문은 비워 둔다.
   - `{run} bootstrap --class <클래스> --call … --affiliation … --goal … --docs <종류,종류> --facts … --dislikes … --yes` 로 저장한다.
2. 요청에서 문서 종류를 정한다. 종류는 {kinds} 이다. 맞는 것이 없으면 종류 없이 조립한다. 독자가 분명하면 `--audience` 로 넘긴다.
3. 사용자가 문체, 어법, 분량, 글자수, 공개 범위를 말했으면 `--set 축=값` 과 `--chars` 로 넘긴다. 축과 값은 `{run} list` 로 본다.
4. `{run} compose --kind <종류> [--audience …] [--set …] [--chars N]` 의 출력 전체를 이번 문서의 규칙으로 따른다. 지침의 공통 바닥이 시키는 대로, 쓰기 전에 틀리면 결과가 쓸모없어지는 것만 두세 개 묻는다.
5. 다 쓴 뒤 `[확인 필요: …]` 표시가 남았으면 모아서 보여 준다.
6. 사용자가 말투나 모양이 마음에 안 든다고 하면 어느 축의 문제인지 짚고, 그 축의 다른 값으로 다시 조립해 대표 문단 하나를 견줘 보인다. 계속 쓰고 싶어 하면 `{run} set <축> <값> [--audience <독자>]` 로 프로필에 남긴다.
"""


def expand_agents(names):
    out = []
    for n in names:
        for a in AGENT_ALIASES.get(n, [n]):
            if a not in AGENT_TARGETS:
                raise Missing(f"모르는 에이전트: {n}. 고를 수 있는 것은 {', '.join(list(AGENT_TARGETS) + list(AGENT_ALIASES))}")
            if a not in out:
                out.append(a)
    return out


def export(th, agents, dest=None, dry_run=False, profile=None, say=print):
    """에이전트마다 SKILL.md 나 붙여 넣을 지침을 쓴다. 손으로 만든 파일은 덮어쓰지 않는다."""
    written = []
    for a in expand_agents(agents):
        t = AGENT_TARGETS[a]
        path = Path(os.path.expanduser(t["path"]))
        if dest:
            path = Path(dest) / a / path.name
        text = compose(th, profile=profile)[0] if a == "web" else skill_text(th)
        note = "" if t["checked"] else " (이 자리는 2차 자료 기준이다. 도구 문서로 확인한다)"
        if path.exists() and a != "web" and EXPORT_MARK not in path.read_text(encoding="utf-8"):
            say(f"건너뜀: {t['label']} → {path} 에 docs-suit 가 만들지 않은 파일이 있다")
            continue
        if dry_run:
            say(f"쓸 예정: {t['label']} → {path}{note}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(path)
        say(f"썼다: {t['label']} → {path}{note}")
    return written


# ---------------------------------------------------------------- bootstrap
def _ask(prompt, default=""):
    try:
        ans = input(prompt)
    except EOFError:
        return default
    return ans.strip() or default


def _pick_numbers(ans, items):
    out = []
    for tok in re.split(r"[,\s]+", ans.strip()):
        if not tok:
            continue
        if tok.isdigit() and 1 <= int(tok) <= len(items):
            out.append(items[int(tok) - 1])
        elif tok in items:
            out.append(tok)
    return list(dict.fromkeys(out))


def bootstrap_interactive(th):
    print("\n=== docs-suit 캐릭터 만들기 ===\n")
    print("1단계. 클래스(직업)를 고른다. 클래스가 기본 말투와 주력 문서를 정한다.\n")
    ids = list(th.classes)
    for i, cid in enumerate(ids, 1):
        c = th.classes[cid]
        kinds = ", ".join(th.kinds[k]["label"] for k in c["kinds"])
        print(f"  {i}. {c['label']:<10} {c['desc']}")
        print(f"     주력 문서: {kinds}")
    cls = None
    while cls is None:
        picked = _pick_numbers(_ask("\n번호를 고른다: "), ids)
        cls = picked[0] if picked else None
    c = th.classes[cls]
    print(f"\n→ {c['label']} 클래스를 골랐다.\n")
    print("2단계. 페르소나. 답하기 싫으면 Enter 로 넘어간다.\n")
    persona = {}
    for key, q in th.persona.items():
        if key == "docs":
            print(f"\n{q.get('ask')}")
            order = c["kinds"] + [k for k in th.kinds if k not in c["kinds"]]
            for i, k in enumerate(order, 1):
                print(f"  {i}. {th.kinds[k]['label']}" + ("  (주력)" if k in c["kinds"] else ""))
            docs = _pick_numbers(_ask(f"  {q.get('hint', '')}\n> "), order)
            if docs:
                persona["docs"] = docs
            continue
        ans = _ask(f"\n{q.get('ask')}\n  {q.get('hint', '')}\n> ")
        if ans:
            persona[key] = clean_text(ans)
    print("\n3단계. 쓰는 AI 도구. 고른 도구에 docs-suit 스킬을 설치한다. Enter 면 건너뛴다.\n")
    names = ["claude", "codex", "gemini", "cursor", "grok", "web"]
    labels = {"claude": "Claude Code", "codex": "Codex CLI", "gemini": "Gemini CLI", "cursor": "Cursor",
              "grok": "Grok Build", "web": "웹 채팅 (ChatGPT, Claude, Gemini, Grok 에 붙여 넣기)"}
    for i, n in enumerate(names, 1):
        print(f"  {i}. {labels[n]}")
    agents = _pick_numbers(_ask("\n번호를 쉼표로 이어 고른다: "), names)
    return cls, persona, agents


def cmd_bootstrap(a, th):
    if a.questions:
        print(json.dumps({"classes": {k: {"label": v["label"], "desc": v["desc"], "kinds": v["kinds"]}
                                      for k, v in th.classes.items()},
                          "questions": th.persona}, ensure_ascii=False, indent=1))
        return 0
    p = profile_path()
    if p.exists() and not a.force:
        print(f"이미 프로필이 있다: {p}\n다시 만들려면 --force 를 붙인다. 지금 프로필은 `suit.py profile` 로 본다.")
        return 1
    flags = {k: getattr(a, k) for k in PERSONA_IN_PROMPT}
    if a.cls or a.yes:
        if not a.cls:
            raise Missing("--yes 로 진행할 때는 --class 가 필요하다")
        th.known_class(a.cls)
        cls = a.cls
        persona = {k: clean_text(v) for k, v in flags.items() if v}
        if a.docs:
            docs = [d.strip() for d in a.docs.split(",") if d.strip()]
            for d in docs:
                if d not in th.kinds:
                    raise Missing(f"모르는 문서 종류: {d}")
            persona["docs"] = docs
        agents = [x.strip() for x in a.agents.split(",") if x.strip()] if a.agents else []
    else:
        if not sys.stdin.isatty():
            raise Missing("대화형 입력을 받을 수 없다. --class 와 --yes 로 진행한다")
        cls, persona, agents = bootstrap_interactive(th)
    expand_agents(agents)
    data = {"profile": {"class": cls, "lang": DEFAULT_LANG}, "persona": persona}
    if agents:
        data["profile"]["agents"] = agents
    if p.exists():
        p.with_name(p.name + ".bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"\n프로필을 저장했다: {write_profile(data)}")
    if agents:
        if not a.yes and _ask("고른 도구에 스킬을 설치할까? [Y/n] ", "y").lower() not in ("y", "yes", "ㅛ"):
            print("설치를 건너뛰었다. 나중에 `suit.py export --agent …` 로 설치한다.")
        else:
            export(th, agents, profile=load_profile())
    print("\n이제 `python3 suit.py compose --kind <종류>` 로 지침을 조립한다. 종류는 `python3 suit.py list` 로 본다.")
    return 0


# ---------------------------------------------------------------- 명령
def themes_root(lang=DEFAULT_LANG):
    return Path(os.environ.get("DOCS_SUIT_THEMES", HERE / "themes" / lang))


def _sets(items):
    out = {}
    for it in items or []:
        axis, sep, value = it.partition("=")
        if not sep:
            raise Missing(f"--set 은 축=값 꼴이다: {it}")
        out[axis.strip()] = value.strip()
    return out


def _auds(s):
    return [x.strip() for x in s.split(",") if x.strip()] if s else None


def warn_stderr(msg):
    print(f"경고: {msg}", file=sys.stderr)


def cmd_list(a, th):
    if a.json:
        print(json.dumps({"classes": th.classes, "axes": th.axes, "audiences": th.audiences, "kinds": th.kinds,
                          "defaults": th.defaults}, ensure_ascii=False, indent=1))
        return 0
    print("클래스")
    for k, v in th.classes.items():
        kinds = ", ".join(th.kinds[x]["label"] for x in v["kinds"])
        print(f"  {k:<12} {v['label']}: {v['desc']}")
        print(f"  {'':<12} 주력 문서 {kinds}")
    if a.classes:
        return 0
    print("문서 종류")
    for k, v in th.kinds.items():
        print(f"  {k:<12} {v.get('label', k)}")
    print("독자")
    for k, v in th.audiences.items():
        print(f"  {k:<12} {v.get('label', k)}")
    print("축과 값 (* 는 중립 기본값)")
    for axis in AXES_ORDER:
        vals = ", ".join(("*" if th.defaults.get(axis) == v else "") + f"{v}={lab}"
                         for v, lab in th.axes[axis]["values"].items())
        print(f"  {axis:<14} {th.axes[axis]['label']}: {vals}")
    return 0


def cmd_profile(a, th):
    p = profile_path()
    if not p.exists():
        print(f"프로필이 없다: {p}\n`python3 suit.py bootstrap` 으로 만든다.")
        return 3
    print(f"# {p}\n")
    print(p.read_text(encoding="utf-8"))
    return 0


def cmd_get(a, th):
    vals, auds, cls = resolve(th, a.kind, _auds(a.audience), _sets(a.set), load_profile(warn_stderr), a.cls,
                              warn_stderr)
    if a.json:
        print(json.dumps({"class": cls, "kind": a.kind, "audiences": auds, "axes": {
            ax: {"value": v, "label": th.label(ax, v), "source": s,
                 "rule": str(th.rule_path(ax, v)) if th.rule_path(ax, v) else None}
            for ax, (v, s) in vals.items()}}, ensure_ascii=False, indent=1))
        return 0
    print(f"클래스\t{cls or '-'}")
    for ax, (v, s) in vals.items():
        print(f"{ax}\t{v}\t{s}\t{th.label(ax, v)}")
    return 0


def cmd_compose(a, th):
    text, _ = compose(th, a.kind, _auds(a.audience), _sets(a.set), load_profile(warn_stderr), a.cls,
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
    data = load_profile(warn_stderr)
    data.setdefault("defaults", {})
    data.setdefault("audiences", {})
    if a.audience:
        prof = data["audiences"].get(a.audience)
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
    p = write_profile(data)
    where = f"독자 {a.audience}" if a.audience else "기본값"
    print(f"프로필 {p} 의 {where} 에 {a.axis}={'(지움)' if a.unset else a.value}")
    return 0


def cmd_export(a, th):
    agents = [x.strip() for x in a.agent.split(",") if x.strip()]
    export(th, agents, a.dest, a.dry_run, load_profile(warn_stderr))
    return 0


def cmd_bundle(a, th):
    out = HERE / "docs" / "themes.json"
    out.write_text(bundle_text(th), encoding="utf-8")
    print(f"썼다: {out}")
    return 0


# ---------------------------------------------------------------- 자체 검사
def selftest(th):
    problems = []

    def check(cond, msg):
        if not cond:
            problems.append(msg)

    def quiet(fn, *args):
        old, sys.stdout = sys.stdout, open(os.devnull, "w")
        try:
            return fn(*args)
        finally:
            sys.stdout.close()
            sys.stdout = old

    # 데이터 정합
    for axis in AXES_ORDER:
        check(th.axes[axis]["values"], f"{axis} 에 값이 없다")
        for v in th.axes[axis]["values"]:
            p = th.rule_path(axis, v)
            check(p.exists(), f"규칙 문서가 없다: {axis}/{v}.md")
            if not p.exists():
                continue
            sample = _sample(p)
            check(sample, f"보기 절이 없다: {axis}/{v}.md")
            if axis == "visual-deck":
                m = re.search(r"```json\n(.*?)\n```", sample, re.S)
                try:
                    tok = json.loads(m.group(1)) if m else {}
                except ValueError:
                    tok = {}
                check({"bg", "ink", "accent"} <= set(tok), f"발표 디자인 보기에 bg, ink, accent 색이 없다: {v}.md")
            if axis == "visual-doc":
                check((th.root / axis / v / "theme.css").exists(), f"CSS 가 없다: visual-doc/{v}/theme.css")
        d = th.root / axis
        if d.is_dir():
            for f in d.glob("*.md"):
                check(f.stem in th.axes[axis]["values"], f"axes.yaml 에 없는 규칙 문서: {axis}/{f.name}")
        check(th.defaults.get(axis) in th.axes[axis]["values"], f"중립 기본값의 {axis} 값이 없거나 모르는 값이다")
    check((th.root / "base.md").exists(), "base.md 가 없다")

    def check_profile(name, prof, allow_template):
        for k, v in prof.items():
            if k in ("label", "audience", "desc", "kinds", "order"):
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
        for x in v.get("audience", []):
            check(x in th.audiences, f"종류 {k} 의 기본 독자 {x} 를 모른다")
        check_profile(f"종류 {k}", v, True)
    for f in (th.root / "kinds").glob("*.md"):
        check(f.stem in th.kinds, f"defaults.yaml 에 없는 종류 문서: kinds/{f.name}")
    for k, v in th.prefer.items():
        check(k in th.kinds, f"prefer 의 {k} 는 모르는 종류다")
        check_profile(f"prefer {k}", v, False)
    check(th.classes, "클래스가 하나도 없다")
    for k, v in th.classes.items():
        check(v["desc"] and v["kinds"], f"클래스 {k} 에 desc 나 kinds 가 없다")
        for x in v["kinds"]:
            check(x in th.kinds, f"클래스 {k} 의 주력 문서 {x} 를 모른다")
        check_profile(f"클래스 {k}", v["defaults"], False)
    covered = {x for v in th.classes.values() for x in v["kinds"]}
    check(covered == set(th.kinds), f"어느 클래스의 주력에도 없는 종류: {sorted(set(th.kinds) - covered)}")
    for key in PERSONA_IN_PROMPT + ("docs",):
        check(key in th.persona, f"persona.yaml 에 질문 {key} 가 없다")

    # 값 정하기 계약
    try:
        for k in th.kinds:
            text, _ = compose(th, kind=k)
            check(text.startswith("# 글쓰기 테마") and "[확인 필요" in text, f"{k} 조립 결과가 다르다")
        vals, _, _ = resolve(th, kind="report", sets={"skeleton": "chrono"})
        check(vals["skeleton"] == ("chrono", "arg"), "인자가 권하는 값을 이기지 못한다")
        vals, _, _ = resolve(th, kind="resume", sets={"skeleton": "bluf"})
        check(vals["skeleton"] == ("template", "kind"), "인자가 종류가 고정한 축을 바꿨다")
        vals, _, _ = resolve(th, kind="minutes", sets={"exposure": "public"})
        check(vals["exposure"] == ("public", "arg"), "공개 범위를 좁히는 인자가 졌다")
        vals, _, _ = resolve(th, kind="report", sets={"exposure": "team"})
        check(vals["exposure"][0] == "submit", "공개 범위를 넓히는 인자가 이겼다")
        vals, _, _ = resolve(th, kind="report", profile={"defaults": {"skeleton": "chrono"}})
        check(vals["skeleton"] == ("imrad", "prefer"), "프로필 기본값이 종류가 권하는 값을 이겼다")
        vals, _, _ = resolve(th, kind="report", profile={"audiences": {"professor": {"skeleton": "pcs"}}})
        check(vals["skeleton"] == ("pcs", "profile-audience"), "프로필의 독자별 값이 권하는 값을 이기지 못한다")
        vals, _, _ = resolve(th, audiences=["teammate", "professor"])
        check(vals["exposure"][0] == "submit" and vals["terms"][0] == "explained", "독자 여럿의 합치기가 다르다")
        vals, _, cls = resolve(th, cls="developer")
        check(cls == "developer" and vals["diagram"] == ("mermaid", "class"), "클래스 기본값이 중립 기본값을 이기지 못한다")
        vals, _, _ = resolve(th, kind="report", cls="developer")
        check(vals["terms"] == ("major", "audience"), "독자가 클래스를 이기지 못한다")
        vals, _, cls = resolve(th, profile={"profile": {"class": "creator"}})
        check(cls == "creator" and vals["register"] == ("haeyo", "class"), "프로필의 클래스를 쓰지 않는다")
        vals, _, cls = resolve(th, profile={"profile": {"class": "creator"}}, cls="student")
        check(cls == "student", "--class 가 프로필 클래스를 이기지 못한다")
        text, _ = compose(th, kind="report", cls="student", chars=1000, fmt="output-style",
                          profile={"persona": {"call": "민수 님", "docs": ["report"]}})
        check(text.startswith("---\nname:") and "공백 포함 1000자" in text, "output-style 이나 글자수 조립이 다르다")
        check("- 호칭: 민수 님" in text and "- 클래스: 대학생" in text and "report" not in text.split("## 쓰는 사람")[1][:200],
              "쓰는 사람 절이 다르다")
        for bad in ({"skeleton": "template"}, {"nope": "x"}, {"voice": "nope"}):
            try:
                resolve(th, sets=bad)
                problems.append(f"잘못된 인자 {bad} 를 받았다")
            except Missing:
                pass
        try:
            resolve(th, cls="wizard")
            problems.append("모르는 클래스를 받았다")
        except Missing:
            pass
    except Missing as e:
        problems.append(f"값 정하기 계약 중 오류: {e}")

    # 프로필과 bootstrap, export
    with tempfile.TemporaryDirectory() as td:
        old = os.environ.get("DOCS_SUIT_PROFILE")
        os.environ["DOCS_SUIT_PROFILE"] = str(Path(td) / "profile.yaml")
        try:
            ns = argparse.Namespace(questions=False, force=False, cls="developer", yes=True,
                                    call='민수 "님"', affiliation="백엔드, 2년 차: 결제", goal=None,
                                    facts="#1 은 지도 시각화", dislikes=None, docs="pr,design-doc", agents="")
            quiet(cmd_bootstrap, ns, th)
            prof = load_profile()
            check(prof.get("profile", {}).get("class") == "developer", "bootstrap 이 클래스를 남기지 않았다")
            per = prof.get("persona", {})
            check(per.get("affiliation") == "백엔드, 2년 차: 결제" and per.get("facts") == "#1 은 지도 시각화"
                  and per.get("docs") == ["pr", "design-doc"] and "”" in per.get("call", ""),
                  f"페르소나가 그대로 읽히지 않는다: {per}")
            check(quiet(cmd_bootstrap, ns, th) == 1, "프로필이 있는데 --force 없이 덮어썼다")
            quiet(cmd_set, argparse.Namespace(axis="register", value="haeyo", unset=False, audience="peer-dev"), th)
            vals, _, _ = resolve(th, kind="pr", profile=load_profile())
            check(vals["register"] == ("haeyo", "profile-audience"), "set 으로 쓴 프로필 값을 읽지 못한다")
            check(load_profile().get("persona", {}).get("affiliation") == "백엔드, 2년 차: 결제", "set 이 페르소나를 망가뜨렸다")
            out = Path(td) / "export"
            paths = quiet(export, th, ["all"], str(out), False, load_profile())
            check(len(paths) == len(AGENT_TARGETS), "export 가 모든 자리에 쓰지 않았다")
            skill = (out / "claude" / "SKILL.md").read_text(encoding="utf-8")
            check(skill.startswith("---\nname: docs-suit") and EXPORT_MARK in skill and str(HERE / "suit.py") in skill,
                  "SKILL.md 머리나 엔진 경로가 다르다")
            web = (out / "web" / "prompt.md").read_text(encoding="utf-8")
            check("- 클래스: 개발자" in web, "웹 지침에 쓰는 사람 절이 없다")
            (out / "gemini" / "SKILL.md").write_text("내가 만든 스킬", encoding="utf-8")
            quiet(export, th, ["gemini"], str(out), False, None)
            check((out / "gemini" / "SKILL.md").read_text(encoding="utf-8") == "내가 만든 스킬",
                  "export 가 손으로 만든 SKILL.md 를 덮어썼다")
        finally:
            if old is None:
                os.environ.pop("DOCS_SUIT_PROFILE", None)
            else:
                os.environ["DOCS_SUIT_PROFILE"] = old

    web = HERE / "docs" / "themes.json"
    if (HERE / "docs").is_dir() and th.root.resolve() == (HERE / "themes" / DEFAULT_LANG).resolve():
        check(web.exists() and web.read_text(encoding="utf-8") == bundle_text(th),
              "docs/themes.json 이 테마와 다르다. python3 suit.py bundle 을 돌린다")

    for p in problems:
        print(f"✗ {p}")
    print("selftest 통과" if not problems else f"selftest 실패 {len(problems)}건")
    return 0 if not problems else 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="suit.py", description="docs-suit: 문서에 옷을 입히는 AI 글쓰기 테마 엔진")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bootstrap")
    b.add_argument("--class", dest="cls")
    for k in PERSONA_IN_PROMPT:
        b.add_argument(f"--{k}")
    b.add_argument("--docs", help="자주 쓰는 문서 종류. 쉼표로 잇는다")
    b.add_argument("--agents", help="스킬을 설치할 도구. 쉼표로 잇는다")
    b.add_argument("--yes", action="store_true", help="묻지 않고 진행한다")
    b.add_argument("--force", action="store_true", help="있는 프로필을 .bak 으로 남기고 새로 만든다")
    b.add_argument("--questions", action="store_true", help="클래스와 페르소나 질문 목록을 JSON 으로 낸다")
    sub.add_parser("profile")
    li = sub.add_parser("list")
    li.add_argument("--classes", action="store_true")
    li.add_argument("--json", action="store_true")
    for name in ("get", "compose"):
        p = sub.add_parser(name)
        p.add_argument("--class", dest="cls")
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
    e = sub.add_parser("export")
    e.add_argument("--agent", required=True, help="claude, agents, codex, gemini, cursor, grok, web, all")
    e.add_argument("--dest", help="에이전트별 하위 폴더로 이 폴더 아래에 쓴다. 시험용")
    e.add_argument("--dry-run", action="store_true")
    sub.add_parser("bundle")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    try:
        th = Themes(themes_root())
        if a.cmd == "selftest":
            return selftest(th)
        return {"bootstrap": cmd_bootstrap, "profile": cmd_profile, "list": cmd_list, "get": cmd_get,
                "compose": cmd_compose, "set": cmd_set, "export": cmd_export, "bundle": cmd_bundle}[a.cmd](a, th)
    except Missing as e:
        print(f"오류: {e}", file=sys.stderr)
        return 3
    except (OSError, ValueError) as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
