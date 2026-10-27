#!/usr/bin/env python3
"""suit.py: docs-suit 글쓰기 테마 엔진. 문서에 입힐 옷(테마)을 골라 AI 에게 줄 지침 한 장으로 조립한다.

글의 모양과 말투를 축 열두 가지로 나누고, 축마다 값을 하나 고른다. 값은 themes/<언어>/<축>/<값>.md 규칙 문서
하나를 가리킨다. 처음 받으면 bootstrap 으로 클래스(직업)와 페르소나를 정해 프로필을 만든다. 프로필은
~/.config/docs-suit/ 에 슬롯으로 두고 저장소 밖이라 커밋되지 않는다. 기본 슬롯은 profile.yaml, 이름 붙은 슬롯은
profiles/<이름>.yaml 이다. 폴더의 .docs-suit.yaml 은 쓸 슬롯과 그 폴더의 축 값을 정하고, 위쪽 폴더부터 겹쳐 읽어
가까운 폴더가 이긴다. 슬롯은 환경 변수, --profile, 폴더 파일, profile use, 기본 슬롯 순으로 정한다.
표준 라이브러리만 쓴다(python3 3.9 이상).

값을 정하는 순서 (위가 이긴다)
  1. 문서 종류가 고정한 축          defaults.yaml 의 kinds
  2. 명령 인자                      --set 축=값
  3. 프로필의 독자별 값              슬롯과 폴더 파일의 audiences. 폴더 파일이 앞선다
  4. 문서 종류가 권하는 값           defaults.yaml 의 prefer
  5. 프로필의 기본값                 슬롯과 폴더 파일의 defaults. 폴더 파일이 앞선다
  6. 독자 프로필                    defaults.yaml 의 audiences
  7. 클래스 기본값                  classes/<클래스>.yaml 의 defaults
  8. 중립 기본값                    defaults.yaml 의 defaults
클래스는 --class 인자가 있으면 그것을, 없으면 프로필의 클래스를 쓴다. 독자를 주지 않으면 문서 종류의 기본 독자를 쓴다.
독자가 여럿이면 공개 범위는 가장 좁은 쪽, 용어 수준은 가장 풀어 쓴 쪽, 나머지 축은 값을 가진 첫 독자를 따른다.
공개 범위(exposure)는 안전 축이다. 1, 6, 7, 8 단계가 정한 값이 출발점이고, 인자와 프로필은 더 조심하는 쪽으로 바꿀 때만 이긴다.
값 template 은 문서 종류만 고정할 수 있다. 그 축은 themes/<언어>/kinds/<종류>.md 의 틀이 정한다.

사용
  python3 suit.py bootstrap                             처음 세팅. 클래스와 페르소나를 묻고 프로필을 만든다
  python3 suit.py bootstrap --class C [--call …] [--affiliation …] [--goal …] [--docs a,b]
                            [--facts …] [--dislikes …] [--agents a,b] [--look a|b] [--preset 이름] --yes [--force]
  python3 suit.py bootstrap --questions                 에이전트가 대신 물을 때 쓸 질문 목록
  python3 suit.py profile [show|list]                   지금 쓰는 프로필 보기, 슬롯 목록
  python3 suit.py profile use <슬롯> [--here]           기본 슬롯을 바꾼다. --here 는 지금 폴더에 적는다
  python3 suit.py list [--classes] [--json]
  python3 suit.py get     [--class C] [--kind K] [--audience A[,B]] [--set 축=값]... [--json]
  python3 suit.py compose [--class C] [--kind K] [--audience A[,B]] [--set 축=값]... [--chars N]
                          [--format prompt|output-style] [--html] [-o 파일]
  python3 suit.py set <축> <값> [--audience A] [--here]   프로필에 쓴다. --here 는 지금 폴더의 폴더 파일에 쓴다
  python3 suit.py set <축> --unset [--audience A] [--here]
  python3 suit.py export --agent claude,agents,antigravity,cursor,grok,web|all [--dest 폴더] [--dry-run]
  python3 suit.py check <파일|-> [--kind K] [--audience A] [--set 축=값]... [--chars N] [--no-record] [--json]
                                                    다 쓴 본문을 조립한 값대로 재고 성장 기록에 남긴다
  python3 suit.py card [--json] [--color auto|always|never]   캐릭터 카드
  python3 suit.py look [<부위> <값>] [--json]        꾸미기. 부위는 base, color, hair, prop, top
  python3 suit.py promote [<키>]                    기여하고 받은 승급 키를 넣는다. 3차와 4차 전직에 쓴다
  python3 suit.py preset list|show|use|export [<이름>] [--here] [--by 아이디] [--label …] [--desc …]
                                                    테마 조합. 남의 조합을 입히거나 내 조합을 기여용 파일로 낸다
  python3 suit.py growth on|off                     캐릭터 키우기를 켜고 끈다. 기록은 지우지 않는다
  python3 suit.py status [--size face|full|line]    상태 줄에 캐릭터를 그린다. 표준 입력의 JSON 에서 작업 폴더를 읽는다
  python3 suit.py widget [--cwd 폴더] [--split] [--once]  터미널 옆 칸의 캐릭터 창. 기록이 바뀌면 다시 그린다
  python3 suit.py bundle                            웹 고르개용 docs/themes.json 을 만든다
  python3 suit.py selftest

종료 코드: 0 성공, 3 모르는 클래스·종류·독자·축·값, 1 그 밖의 오류.
bootstrap, profile, get, compose, set, export, check, card, look, preset, promote, growth, status 에는 --profile <슬롯> 을 붙일 수 있다.
캐릭터 성장 기록은 ~/.config/docs-suit/growth/<슬롯>.jsonl 에 남는다. 본문과 파일 경로는 남기지 않는다.
환경 변수: DOCS_SUIT_THEMES 는 테마 폴더를, DOCS_SUIT_PROFILE 은 프로필 파일을, DOCS_SUIT_HOME 은 설정 폴더를 바꾼다.
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unicodedata
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_LANG = "ko"
AXES_ORDER = ("visual-doc", "visual-deck", "voice", "register", "terms", "skeleton", "length",
              "emphasis", "diagram", "sources", "exposure", "ai-disclosure")
# compose 가 규칙을 싣는 순서. 앞에 나온 규칙이 이긴다고 지침 머리에 적는다.
COMPOSE_ORDER = ("exposure", "skeleton", "voice", "register", "terms", "length", "sources",
                 "ai-disclosure", "diagram", "emphasis", "visual-deck", "visual-doc")
EXPOSURE_STRICT = ("public", "submit", "team")   # 앞이 가장 조심하는 쪽이다
TERMS_PLAIN = ("everyday", "explained", "major")  # 앞이 가장 풀어 쓴다
TEMPLATE = "template"
CONFIG_DEFAULT = "~/.config/docs-suit"  # 기본 슬롯은 profile.yaml, 이름 붙은 슬롯은 profiles/<이름>.yaml
FOLDER_FILE = ".docs-suit.yaml"
FOLDER_KEYS = ("profile", "defaults", "audiences")
PRESET_HEAD = ("# docs-suit 테마 조합. suit.py preset use <이름> 으로 내 슬롯에 입힌다.\n"
               "# 공개 저장소에 올라가므로 페르소나와 회사, 사람 이름은 넣지 않는다.")
SLOT_RE = re.compile(r"^[\w-]+$")
PROFILE_HEAD = "# docs-suit 프로필. suit.py bootstrap 과 set 이 쓴다. 손으로 고쳐도 된다."
FOLDER_HEAD = ("# docs-suit 폴더 설정. 이 폴더와 아래 폴더에 적용된다. profile 은 쓸 슬롯 이름이고,\n"
               "# defaults 와 audiences 는 슬롯의 값보다 앞선다. 저장소에 올라갈 수 있어 페르소나는 넣지 않는다.")
PERSONA_IN_PROMPT = ("call", "affiliation", "goal", "facts", "dislikes")  # docs 는 싣지 않는다
EXPORT_MARK = "<!-- docs-suit export 가 만든 파일이다."
# 에이전트마다 SKILL.md 를 놓는 자리. checked 가 False 인 자리는 2차 자료 기준이라 쓰기 전에 안내한다.
AGENT_TARGETS = {
    "claude": {"label": "Claude Code", "path": "~/.claude/skills/docs-suit/SKILL.md", "checked": True},
    "agents": {"label": "Agent Skills 공용 자리 (Codex 등)", "path": "~/.agents/skills/docs-suit/SKILL.md", "checked": True},
    "antigravity": {"label": "Antigravity CLI", "path": "~/.gemini/config/skills/docs-suit/SKILL.md", "checked": False},
    "cursor": {"label": "Cursor", "path": "~/.cursor/skills/docs-suit/SKILL.md", "checked": False},
    "web": {"label": "웹 채팅에 붙여 넣을 지침", "path": "~/.config/docs-suit/prompt.md", "checked": True},
}
AGENT_ALIASES = {"grok": ["claude", "agents"], "codex": ["agents"], "gemini": ["antigravity"], "all": list(AGENT_TARGETS)}
# 승급 키를 확인하는 공개 키. 개인 키는 저장소 관리자만 갖고 저장소 밖에 둔다. tools/issue-key.py 가 키를 만든다.
# 키를 바꿔도 지난 키가 계속 먹도록 kid 마다 남겨 둔다.
PROMOTE_KEYS = {
    "dodokim-2026": (int(
        "a9845486fb250b2495f25710aac8a18456b0d9ccbd281632477982c58f6c1547b5e8e663c6c9b15982e29cbd8292b000"
        "651cdf8880a8abca999759ef7927bacbcb7081a2013a7ee86f7ceb5224e89d768ed8c49ac0ec8111c7448542ff74c3b4"
        "950ffc4622f92b54d033349220f4f0e16acbd97e2e3dd1ea55557a40a276806427e9b8bb6e8a781f902b6c9e1bb923f4"
        "9dae7ac3548b65a880601511757e26d676b837539e6b9c5e01ce6c503522b462c6d6ddbc22628fa8eee167da4411b33d"
        "83062bca017225847b157f283c12782987aba2cddcf6cb7286f4cb54c22d79a35a18b1a01e923a0c3b8025e0d6aa81dc"
        "8f4e4de5ae8e597b83701790bfebecdd"
        , 16), 65537),
}
SHA256_INFO = bytes.fromhex("3031300d060960864801650304020105000420")  # PKCS#1 v1.5 의 SHA-256 머리


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
    """맨 앞 칸에 절 이름, 들여 쓴 줄에 `키: 값` 하나인 두 단계 YAML 만 읽는다. 맨 앞 칸의 `키: 값` 도 받는다."""
    data, section = {}, None
    for n, raw in enumerate(text.splitlines(), 1):
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        if not line[0].isspace():
            key, _, rest = line.partition(":")
            if rest.strip():
                data[key.strip()] = _value(rest)
                section = None
                continue
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


def dump_yaml(data, head=PROFILE_HEAD):
    def one(v):
        if isinstance(v, list):
            return "[" + ", ".join(_quote(x) for x in v) + "]"
        if isinstance(v, dict):
            return "{" + ", ".join(f"{k}: {one(x)}" for k, x in v.items()) + "}"
        return _quote(v)
    lines = [head, ""]
    for section, body in data.items():
        if not body:
            continue
        if not isinstance(body, dict):
            lines += [f"{section}: {one(body)}", ""]
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
                                    "kinds": meta.get("kinds", []), "titles": meta.get("titles", []),
                                    "defaults": c.get("defaults", {})}
        pq = self.root / "persona.yaml"
        self.persona = parse_yaml(pq.read_text(encoding="utf-8")).get("questions", {}) if pq.exists() else {}
        gr = self.root / "growth.yaml"
        self.growth = parse_yaml(gr.read_text(encoding="utf-8")) if gr.exists() else {}
        lk = self.root / "look.yaml"
        self.look = parse_yaml(lk.read_text(encoding="utf-8")) if lk.exists() else {}
        self.presets = {}
        for f in sorted((self.root / "presets").glob("*.yaml")):
            d = parse_yaml(f.read_text(encoding="utf-8"))
            self.presets[f.stem] = {**d.get("preset", {}), "defaults": d.get("defaults", {}),
                                    "audiences": d.get("audiences", {})}

    def part_path(self, part, name):
        """캐릭터 그림 한 장. part 는 base, top, hair, prop 이다."""
        return self.root / "sprites" / part / f"{name}.txt"

    def rule_path(self, axis, value):
        if value == TEMPLATE:
            return None
        return self.root / axis / f"{value}.md"

    def kind_path(self, kind):
        return self.root / "kinds" / f"{kind}.md"

    def known(self, axis, value, allow_template=False):
        if axis not in self.axes:
            raise Missing(f"모르는 축: {axis}. 고를 수 있는 축은 {', '.join(self.axes)}")
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


# ---------------------------------------------------------------- 프로필, 슬롯, 폴더 파일
def config_dir():
    return Path(os.path.expanduser(os.environ.get("DOCS_SUIT_HOME", CONFIG_DEFAULT)))


def slot_path(name):
    if not SLOT_RE.match(name or ""):
        raise Missing(f"슬롯 이름은 글자, 숫자, -, _ 로 쓴다: {name}")
    return config_dir() / ("profile.yaml" if name == "default" else f"profiles/{name}.yaml")


def find_folder_files(start=None):
    """지금 폴더부터 위로 홈 폴더까지 있는 .docs-suit.yaml 을 가까운 것부터 돌려준다."""
    here = Path(start or os.getcwd()).resolve()
    home = Path.home().resolve()
    found = []
    for d in (here, *here.parents):
        if (d / FOLDER_FILE).is_file():
            found.append(d / FOLDER_FILE)
        if d == home:
            break
    return found


def read_folder(path, warn=lambda m: None):
    """폴더 파일은 저장소에 올라갈 수 있어서 슬롯 이름과 축 값만 읽고 페르소나는 버린다."""
    if not path or not path.exists():
        return {}
    try:
        data = parse_yaml(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        warn(f"폴더 파일을 읽지 못해 무시한다: {path}: {e}")
        return {}
    for k in [k for k in data if k not in FOLDER_KEYS]:
        warn(f"폴더 파일의 {k} 는 쓰지 않는다. 페르소나는 슬롯 프로필에 둔다: {path}")
        data.pop(k)
    return data


def folder_settings(start=None, warn=lambda m: None):
    """폴더 파일을 먼 것부터 겹쳐 읽는다. 가까운 폴더의 값이 이긴다. (합친 값, 폴더 파일들)"""
    files = find_folder_files(start)
    merged = {}
    for f in reversed(files):
        data = read_folder(f, warn)
        merged = merge_folder(merged, data)
        if data.get("profile"):
            merged["profile"] = data["profile"]
    return merged, files


def profile_source(name=None, start=None):
    """(프로필 파일, 슬롯 이름, 폴더 파일들, 정한 까닭). 까닭은 env · arg · folder · current · default 순으로 이긴다."""
    settings, folder = folder_settings(start)
    env = os.environ.get("DOCS_SUIT_PROFILE")
    if env:
        return Path(os.path.expanduser(env)), None, folder, "env"
    if name:
        return slot_path(name), name, folder, "arg"
    slot = settings.get("profile")
    if slot:
        return slot_path(slot), slot, folder, "folder"
    current = config_dir() / "current"
    slot = current.read_text(encoding="utf-8").strip() if current.exists() else ""
    if slot:
        return slot_path(slot), slot, folder, "current"
    return slot_path("default"), "default", folder, "default"


def profile_path(name=None):
    return profile_source(name)[0]


def read_slot(path, warn=lambda m: None):
    if not path.exists():
        return {}
    try:
        return parse_yaml(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        warn(f"프로필을 읽지 못해 무시한다: {path}: {e}")
        return {}


def merge_folder(profile, folder):
    """폴더 파일의 축 값을 슬롯 프로필 위에 얹는다. 같은 축이면 폴더가 이긴다."""
    out = dict(profile)
    defaults = dict(profile.get("defaults") or {})
    defaults.update(folder.get("defaults") or {})
    auds = {k: dict(v) for k, v in (profile.get("audiences") or {}).items() if isinstance(v, dict)}
    for k, v in (folder.get("audiences") or {}).items():
        if isinstance(v, dict):
            auds.setdefault(k, {}).update(v)
    if defaults:
        out["defaults"] = defaults
    if auds:
        out["audiences"] = auds
    return out


def load_profile(warn=lambda m: None, name=None, start=None):
    """적용되는 슬롯 프로필에 폴더 파일의 축 값을 얹어 돌려준다."""
    path = profile_source(name, start)[0]
    return merge_folder(read_slot(path, warn), folder_settings(start, warn)[0])


def write_profile(data, name=None):
    p = profile_path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dump_yaml(data), encoding="utf-8")
    return p


def write_folder(data, where=None):
    p = Path(where or os.getcwd()) / FOLDER_FILE
    p.write_text(dump_yaml(data, FOLDER_HEAD), encoding="utf-8")
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
                    warn(f"공개 범위는 더 조심하는 쪽으로만 바뀌어 {s} 의 {cand} 대신 {base} 를 쓴다. "
                         "팀 안에서만 볼 글이면 --audience 를 teammate 나 peer-dev 로 넘긴다")
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


# ---------------------------------------------------------------- 본문 검사
# 조립된 값대로 썼는지 어림 기준으로 잰다. 기준은 대략값이라 틀림이 나오면 본문을 직접 읽어 확인한다.
LENGTH_LIMIT = {"brief": 1500, "page": 3500}
ENDING = (("polite", "합쇼체", ("니다", "니까", "십시오")), ("haeyo", "해요체", ("요",)),
          ("plain", "평어체", ("다", "까", "라")))
# 백틱 안의 `[확인 필요]` 는 표시 방식을 설명한 말일 수 있어 빼되, 내용이 든 `[확인 필요: 영향 범위]` 는 표시로 센다.
UNRESOLVED = re.compile(r"(?<!`)\[확인 필요|`\[확인 필요:\s*[^\]`…\s][^\]`]*\]`")
CHECK_HINT = {"register": "{want} 로 맞춘다", "voice": {"bullet": "줄글을 목록으로 나눈다", "prose": "목록을 줄글로 푼다"},
              "length": "한도 안으로 줄인다", "emphasis": "굵은 글씨를 뺀다"}


def body_lines(doc):
    return [ln.strip() for ln in doc.splitlines()
            if ln.strip() and not ln.lstrip().startswith(("#", "|", "```", "---", ">"))]


def endings(lines):
    count = {k: 0 for k, _, _ in ENDING}
    for ln in lines:
        for sent in re.split(r"(?<=[.!?])\s+", re.sub(r"^([-*+]|\d+[.)])\s+", "", ln)):
            if sent.rstrip(" *`\"'”’)").endswith("?"):
                continue  # 질문 문장은 본문에 실린 예상 질문일 수 있어 어법을 세지 않는다
            tail = re.sub(r"(\[[^\]]*\]|\([^)]*\)|[\s.!?\"'”’*`:])+$", "", sent)
            if tail.endswith("세요"):
                continue  # "알려 주세요", "안녕하세요" 는 합쇼체 글에도 들어가서 어법을 가르지 못한다
            for name, _, ends in ENDING:
                if tail.endswith(ends):
                    count[name] += 1
                    break
    return count


def check_doc(doc, vals, chars, kind=None):
    """[(축, 맞았나, 잰 값)]. 잴 거리가 모자라면 그 축은 빼고 낸다."""
    out = []
    lines = body_lines(doc)
    count = endings(lines)
    total = sum(count.values())
    want = vals["register"][0]
    if total >= 3:
        out.append(("register", count[want] >= 0.6 * total,
                    " · ".join(f"{label} {count[k]}" for k, label, _ in ENDING if count[k])))
    # 틀이 정한 문서는 골격 규칙이 문체 규칙보다 앞서서 문체를 재지 않는다.
    if len(lines) >= 4 and vals["skeleton"][0] != TEMPLATE:
        ratio = sum(1 for ln in lines if re.match(r"([-*+]|\d+[.)])\s", ln)) / len(lines)
        ok = ratio >= 0.3 if vals["voice"][0] == "bullet" else ratio <= 0.5
        out.append(("voice", ok, f"목록 줄 {ratio:.0%}"))
    size = len("\n".join(lines))
    limit = int(chars * 1.1) if chars else None if kind == "slides" else LENGTH_LIMIT.get(vals["length"][0])
    if limit:
        out.append(("length", size <= limit, f"{size}자, 한도 {limit}자"))
    if vals["emphasis"][0] == "none":
        out.append(("emphasis", "**" not in doc, "굵은 글씨 있음" if "**" in doc else "없음"))
    return out


def check_hint(th, axis, vals):
    hint = CHECK_HINT[axis]
    if isinstance(hint, dict):
        return hint[vals[axis][0]]
    return hint.format(want=th.label(axis, vals[axis][0]))


# ---------------------------------------------------------------- 캐릭터와 성장
# 슬롯이 캐릭터다. check 가 문서 한 건마다 기록 한 줄을 남기고, 경험치와 레벨은 기록에서 매번 다시 계산한다.
def growth_path(name=None, start=None):
    """슬롯의 성장 기록 파일. 환경 변수로 프로필 파일을 정했으면 그 파일 옆에 둔다."""
    path, slot, _, _ = profile_source(name, start)
    if slot is None:
        return path.with_name(path.stem + ".growth.jsonl")
    return config_dir() / "growth" / f"{slot}.jsonl"


def growth_on(slot_data):
    """슬롯이 있고 growth 를 끄지 않았으면 켜져 있다. set 으로만 만든 슬롯에는 profile 절이 없을 수 있다."""
    if not slot_data:
        return False
    meta = slot_data.get("profile")
    return not (isinstance(meta, dict) and str(meta.get("growth")) == "off")


def read_growth(path, warn=lambda m: None):
    if not path.exists():
        return []
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except ValueError:
            warn(f"성장 기록 {n}행을 읽지 못해 건너뛴다: {path}")
            continue
        if isinstance(e, dict) and e.get("doc"):
            out.append(e)
    return out


def doc_key(src, text):
    """같은 문서를 다시 검사했는지 가리는 지문. 경로나 본문 대신 해시만 남긴다."""
    key = f"file:{Path(src).expanduser().resolve()}" if src != "-" else f"text:{text}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def level_cost(th, level):
    """이 레벨에서 다음 레벨로 가는 데 드는 경험치. growth.yaml 의 level 은 `시작 레벨: 경험치` 구간이다."""
    cost = 0
    for start, pts in sorted((int(k), int(v)) for k, v in th.growth["level"].items()):
        if level >= start:
            cost = pts
    return cost


def level_of(th, exp):
    """(레벨, 이번 레벨에서 쌓은 경험치, 다음 레벨까지 드는 경험치). 최고 레벨이면 마지막 값은 0 이다."""
    top = int(th.growth.get("max") or 0)
    level = 1
    while not top or level < top:
        need = level_cost(th, level)
        if exp < need:
            return level, exp, need
        exp -= need
        level += 1
    return level, exp, 0


def growth_state(th, entries, keys=()):
    """기록에서 경험치와 레벨, 문서 종류별 건수를 계산한다. 같은 문서는 가장 좋은 기록 하나로 센다.
    resolved 는 앞선 기록에 [확인 필요] 가 있던 문서를 다시 검사해 0 이 됐을 때만 준다. 처음부터 표시가 없는
    문서에 주면 모르는 곳을 [이름] 처럼 맨 괄호로 숨긴 글이 점수를 받는다."""
    pts = {k: int(v["points"]) for k, v in th.growth["exp"].items()}
    cap = int(th.growth["limit"]["daily-kind"])
    docs = {}
    for e in entries:
        d = docs.setdefault(e["doc"], {"day": str(e.get("at", ""))[:10], "kind": None, "best": [], "marked": False})
        d["kind"] = e.get("kind") or d["kind"]
        parts = ["done"] + (["clean"] if all((e.get("checks") or {}).values()) else []) \
            + (["resolved"] if d["marked"] and not e.get("unresolved") else [])
        d["marked"] = d["marked"] or bool(e.get("unresolved"))
        if sum(pts[p] for p in parts) > sum(pts[p] for p in d["best"]):
            d["best"] = parts
    exp, kinds, per_day, gains = 0, {}, {}, {}
    for key, d in docs.items():
        day = (d["day"], d["kind"])
        per_day[day] = per_day.get(day, 0) + 1
        parts = list(d["best"]) if per_day[day] <= cap else []
        if parts and d["kind"] and d["kind"] not in kinds:
            parts.append("new-kind")
        if d["kind"]:
            kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
        gains[key] = parts
        exp += sum(pts[p] for p in parts)
    level, into, need = level_of(th, exp)
    return {"exp": exp, "level": level, "into": into, "need": need, "tier": tier_of(th, level, keys),
            "docs": len(docs), "kinds": kinds, "gains": gains}


def promote_rules(th):
    """[(차수, 문턱 레벨, 승급 키가 필요한가)]."""
    return sorted((int(t), int(v["level"]), str(v.get("key", "")).lower() == "true")
                  for t, v in (th.growth.get("promote") or {}).items())


def tier_of(th, level, keys=()):
    """전직 차수. 0 은 전직 전이다. 키가 걸린 차수는 그 차수의 승급 키가 keys 에 있어야 오른다."""
    tier = 0
    for t, lv, keyed in promote_rules(th):
        if level < lv or (keyed and t not in keys):
            break
        tier = t
    return tier


def title_of(th, cls, tier):
    titles = th.classes.get(cls, {}).get("titles") or []
    return titles[min(tier, len(titles) - 1)] if titles else None


def opened_at(th, tier):
    """이 차수에서 새로 여는 꾸미기 부위의 이름들."""
    return [v["label"] for v in (th.look.get("unlock") or {}).values() if int(v["at"]) == tier]


def growth_line(th, before, after, key, kind, cls=None):
    """기록 한 건을 남긴 뒤 에이전트가 답 끝에 옮길 한 줄. 전직했으면 새 칭호와 새로 열린 꾸미기를 붙인다."""
    exp = th.growth["exp"]
    old = before["gains"].get(key)
    new = after["gains"][key]
    shown = [p for p in new if old is None or p not in old]
    label = th.kinds[kind]["label"] if kind else "일반 글"
    head = f"{label} {'다시 검사 ' if old is not None else ''}+{after['exp'] - before['exp']}"
    if shown:
        head += " (" + ", ".join(f"{exp[p]['label']} {exp[p]['points']}" for p in shown) + ")"
    elif old is None:
        head += f" (같은 날 같은 종류는 {th.growth['limit']['daily-kind']}건까지 센다)"
    lv = f"Lv.{after['level']}" if after["level"] == before["level"] else f"Lv.{before['level']} → Lv.{after['level']}"
    for tier in range(before["tier"] + 1, after["tier"] + 1):
        title = title_of(th, cls, tier)
        lv += f" · 전직 [{title}]" if title else f" · {tier}차 전직"
        lv += "".join(f" · {label} 열림" for label in opened_at(th, tier))
    left = f"다음 레벨까지 {after['need'] - after['into']}" if after["need"] else "최고 레벨"
    return f"성장: {head} · {lv} · {left}"


def record_check(th, name, src, text, kind, checks, left, warn=lambda m: None):
    """캐릭터 키우기가 켜져 있으면 기록 한 줄을 남기고 성장 줄을 돌려준다. 꺼져 있거나 슬롯이 없으면 None."""
    slot_data = read_slot(profile_path(name), warn)
    if not growth_on(slot_data):
        return None
    path = growth_path(name)
    entries = read_growth(path, warn)
    entry = {"v": 1, "at": datetime.now().isoformat(timespec="minutes"), "doc": doc_key(src, text), "kind": kind,
             "checks": {axis: ok for axis, ok, _ in checks}, "unresolved": left,
             "chars": len("\n".join(body_lines(text)))}
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    keys = key_tiers(promote_keys(warn))
    return growth_line(th, growth_state(th, entries, keys), growth_state(th, entries + [entry], keys), entry["doc"], kind,
                       (slot_data.get("profile") or {}).get("class"))


# ---------------------------------------------------------------- 테마 조합
# 축 기본값과 독자별 값을 한 묶음으로 남긴 것이다. 게임의 스킬 조합처럼 남이 기여한 조합을 내 슬롯에 입힌다.
# 자기 조합을 기여하는 것이 4차 전직의 조건이다.
def preset_order(th, cls=None):
    """추천 표시가 있는 조합, 고른 클래스의 조합 순으로 앞에 둔다."""
    return sorted(th.presets, key=lambda k: (str(th.presets[k].get("featured")) != "true",
                                             bool(cls) and th.presets[k].get("class") != cls, k))


def apply_preset(data, preset):
    """슬롯이나 폴더 파일의 축 값을 조합의 값으로 바꾼다. 페르소나와 꾸미기는 그대로 둔다."""
    data["defaults"] = dict(preset.get("defaults") or {})
    data["audiences"] = {k: dict(v) for k, v in (preset.get("audiences") or {}).items() if isinstance(v, dict)}
    return data


def known_values(th, values):
    """알려진 축 값만 남긴다. 조합으로 내보낼 때 모르는 값을 걸러 낸다."""
    out = {}
    for axis, value in (values or {}).items():
        try:
            th.known(axis, value)
            out[axis] = value
        except Missing:
            pass
    return out


# ---------------------------------------------------------------- 승급 키
# 3차와 4차 전직은 저장소에 기여하고 받은 승급 키가 있어야 오른다. 키는 `dsk1.<내용>.<서명>` 꼴이고,
# 내용은 GitHub 아이디와 차수, 기여 링크다. 엔진과 기록이 사용자 컴퓨터에 있어 마음먹은 조작은 막지 못한다.
# 키는 정직하게 오르는 길을 기여로 잇는 장치다.
def rsa_verify(n, e, msg, sig):
    """RSA PKCS#1 v1.5 SHA-256 서명 확인. 표준 라이브러리의 큰 정수 거듭제곱으로 한다."""
    k = (n.bit_length() + 7) // 8
    if len(sig) != k:
        return False
    em = pow(int.from_bytes(sig, "big"), e, n).to_bytes(k, "big")
    t = SHA256_INFO + hashlib.sha256(msg).digest()
    return hmac.compare_digest(em, b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t)


def _unb64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def read_promote_key(text, keys=None):
    """서명이 맞으면 키의 내용을, 아니면 None 을 돌려준다."""
    keys = PROMOTE_KEYS if keys is None else keys
    parts = text.strip().split(".")
    if len(parts) != 3 or parts[0] != "dsk1":
        return None
    try:
        payload, sig = json.loads(_unb64(parts[1]).decode("utf-8")), _unb64(parts[2])
    except (ValueError, UnicodeDecodeError):
        return None
    pub = keys.get(payload.get("kid")) if isinstance(payload, dict) else None
    if not pub or not rsa_verify(pub[0], pub[1], parts[1].encode("ascii"), sig):
        return None
    if not isinstance(payload.get("tier"), int) or not payload.get("who"):
        return None
    return payload


def keys_path():
    """승급 키는 사람 단위라 슬롯마다 두지 않고 설정 폴더에 한 파일로 둔다."""
    return config_dir() / "keys.txt"


def promote_keys(warn=lambda m: None):
    path = keys_path()
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").split():
        payload = read_promote_key(line)
        if payload:
            out.append(payload)
        else:
            warn(f"확인하지 못한 승급 키를 건너뛴다: {path}")
    return out


def key_tiers(payloads):
    """키가 열어 주는 차수. 4차 키는 3차 조건인 기여도 채운다."""
    return {t for p in payloads for t in range(1, int(p["tier"]) + 1)}


# ---------------------------------------------------------------- 도트 그림
def read_sprite(path):
    """(팔레트, 픽셀 줄). 팔레트는 글자마다 {color, label, custom}."""
    pal, rows, part = {}, [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.startswith("#"):
            continue
        if line in ("palette", "pixels"):
            part = line
            continue
        if part == "palette":
            ch, color, *name = line.split()
            label = " ".join(name)
            pal[ch] = {"color": color, "label": label.rstrip(" *"), "custom": label.endswith("*")}
        elif part == "pixels":
            rows.append(line)
    return pal, rows


def color_depth(mode="auto"):
    """0 은 색 없음, 8 은 256색, 24 는 트루컬러."""
    if mode == "never" or (mode == "auto" and (os.environ.get("NO_COLOR") or not sys.stdout.isatty())):
        return 0
    return 24 if os.environ.get("COLORTERM", "").lower() in ("truecolor", "24bit") else 8


def _ansi(color, ground, depth):
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    if depth == 24:
        return f"\033[{ground};2;{r};{g};{b}m"
    steps = (0, 95, 135, 175, 215, 255)
    near = [min(range(6), key=lambda i: abs(steps[i] - v)) for v in (r, g, b)]
    return f"\033[{ground};5;{16 + 36 * near[0] + 6 * near[1] + near[2]}m"


def sprite_grid(path, custom=None):
    """그림 한 장을 색 격자로 읽는다. 빈칸은 None. custom 을 주면 * 가 붙은 색을 그 색으로 바꾼다."""
    pal, rows = read_sprite(path)
    colors = {ch: p["color"] for ch, p in pal.items()}
    if custom:
        colors.update({ch: custom for ch, p in pal.items() if p["custom"]})
    return [[colors.get(ch) for ch in row] for row in rows]


LOOK_LAYERS = ("top", "hair", "prop")  # 기본 몸 위에 이 순서로 겹친다


def look_of(th, slot_data, tier=None, warn=lambda m: None):
    """슬롯의 look 절에 기본값을 채운다. 모르는 값은 기본값으로 돌린다. tier 를 주면 그 차수까지 열린 부위만
    입힌다. 슬롯 파일을 손으로 고쳐 잠긴 옷을 입히는 길을 막는다."""
    have = (slot_data or {}).get("look") or {}
    have = have if isinstance(have, dict) else {}
    bases = th.look.get("base") or {}
    base = have.get("base") if have.get("base") in bases else next(iter(bases), "a")
    look = {"base": base, "top": "shirt", "hair": bases.get(base, {}).get("hair"), "prop": None, "color": None}
    for part, table in (("top", th.look.get("top")), ("hair", th.look.get("hair")), ("prop", th.look.get("prop")),
                        ("color", th.look.get("colors"))):
        val = have.get(part)
        locked = tier is not None and tier < int(((th.look.get("unlock") or {}).get(part) or {}).get("at", 0))
        if val and val in (table or {}) and not locked:
            look[part] = val
        elif val and not locked:
            warn(f"프로필의 look.{part}={val} 는 모르는 값이라 기본값을 쓴다")
    return look


def look_grid(th, look):
    """기본 몸 위에 옷, 머리, 소품을 겹친 색 격자."""
    grid = sprite_grid(th.part_path("base", look["base"]))
    color = (th.look.get("colors") or {}).get(look["color"], {}).get("color") if look["color"] else None
    for part in LOOK_LAYERS:
        if not look[part]:
            continue
        layer = sprite_grid(th.part_path(part, look[part]), color if part == "top" else None)
        for y, row in enumerate(layer):
            for x, c in enumerate(row):
                if c:
                    grid[y][x] = c
    return grid


def render_grid(grid, depth=24):
    """반 칸 블록 하나에 위아래 픽셀 두 개를 그린다. 위는 글자색, 아래는 배경색이다."""
    if len(grid) % 2:
        grid = grid + [[None] * len(grid[0])]
    out = []
    for top, bot in zip(grid[::2], grid[1::2]):
        line = ""
        for ca, cb in zip(top, bot):
            if ca and cb:
                line += _ansi(ca, 38, depth) + _ansi(cb, 48, depth) + "▀"
            elif ca or cb:
                line += "\033[0m" + _ansi(ca or cb, 38, depth) + ("▀" if ca else "▄")
            else:
                line += "\033[0m "
        out.append(line + "\033[0m")
    return out


def beside(art, width, info):
    """그림 오른쪽에 글 줄을 세로 가운데로 놓는다."""
    pad = max(0, (len(art) - len(info)) // 2)
    rows = max(len(art), len(info) + pad)
    return [(art[i] if i < len(art) else " " * width) + "   " + (info[i - pad] if 0 <= i - pad < len(info) else "")
            for i in range(rows)]


def display_width(text):
    """터미널에서 차지하는 칸 수. 한글처럼 넓은 글자는 두 칸으로 센다."""
    plain = re.sub(r"\033\[[0-9;]*m", "", text)
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in plain)


def card_lines(th, slot_data, slot, state, depth, vals=None, held=(), stacked=False):
    """캐릭터 카드. 색을 쓸 수 있으면 왼쪽에 도트 그림을 그리고 오른쪽에 글을 놓는다. held 는 받은 승급 키다."""
    cls = (slot_data.get("profile") or {}).get("class")
    name = (slot_data.get("persona") or {}).get("call") or slot or "이름 없음"
    title = title_of(th, cls, state["tier"])
    filled = state["into"] * 10 // state["need"] if state["need"] else 10
    tops = sorted(state["kinds"].items(), key=lambda kv: -kv[1])[:3]
    nxt = next(((t, lv, keyed) for t, lv, keyed in promote_rules(th) if t == state["tier"] + 1), None)
    who = max(held, key=lambda k: k["tier"])["who"] if held else None
    info = [(f"[{title}] " if title else "") + f"{name} · {th.classes[cls]['label'] if cls in th.classes else '클래스 없음'}"
            + (f" · 기여 @{who}" if who else ""),
            f"Lv.{state['level']}  {'█' * filled}{'░' * (10 - filled)}  "
            + (f"{state['into']}/{state['need']}" if state["need"] else "최고 레벨"),
            f"문서 {state['docs']}건 · 도감 {len(state['kinds'])}/{len(th.kinds)} 종류",
            "많이 쓴 문서 " + (" · ".join(f"{th.kinds[k]['label']} {n}" for k, n in tops if k in th.kinds) or "아직 없음")]
    if nxt:
        t, lv, keyed = nxt
        nt = title_of(th, cls, t)
        when = "승급 키를 받으면" if keyed and state["level"] >= lv else f"Lv.{lv}" + (" + 승급 키" if keyed else "")
        info.append(f"다음 전직 {when}" + (f" [{nt}]" if nt else "") + "".join(f" · {label} 열림" for label in opened_at(th, t)))
    else:
        info.append("전직을 모두 마쳤다")
    if vals:
        info.append("지금 테마 " + " · ".join(th.label(ax, vals[ax][0]) for ax in ("register", "voice", "length")))
    if not growth_on(slot_data):
        info.append("캐릭터 키우기가 꺼져 있다. 켜려면 suit.py growth on")
    if not depth or not th.look:
        return info
    grid = look_grid(th, look_of(th, slot_data, state["tier"]))
    if stacked:
        return render_grid(grid, depth) + [""] + info
    return beside(render_grid(grid, depth), len(grid[0]), info)


def status_cwd(text):
    """상태 줄이 표준 입력으로 넘기는 JSON 에서 작업 폴더를 꺼낸다. Claude Code 는 workspace.current_dir 와 cwd 를 준다."""
    try:
        data = json.loads(text) if text.strip() else {}
    except ValueError:
        return None
    ws = data.get("workspace") if isinstance(data, dict) else None
    return (ws or {}).get("current_dir") or data.get("cwd") if isinstance(data, dict) else None


def status_lines(th, slot_data, slot, state, depth, size="face", held=()):
    """상태 줄에 그릴 캐릭터. face 는 얼굴과 세 줄, full 은 온몸, line 은 글 한 줄이다."""
    cls = (slot_data.get("profile") or {}).get("class")
    name = (slot_data.get("persona") or {}).get("call") or slot or "이름 없음"
    title = title_of(th, cls, state["tier"])
    filled = state["into"] * 10 // state["need"] if state["need"] else 10
    bar = f"Lv.{state['level']} {'█' * filled}{'░' * (10 - filled)} " + (
        f"{state['into']}/{state['need']}" if state["need"] else "최고 레벨")
    head = (f"[{title}] " if title else "") + name
    if size == "line" or not depth or not th.look:
        return [f"{head} · {bar}"]
    nxt = next(((t, lv, keyed) for t, lv, keyed in promote_rules(th) if t == state["tier"] + 1), None)
    info = [head + (f" · {th.classes[cls]['label']}" if cls in th.classes else ""), bar]
    if nxt:
        t, lv, keyed = nxt
        nt = title_of(th, cls, t)
        info.append(("다음 전직 승급 키" if keyed and state["level"] >= lv else f"다음 전직 Lv.{lv}") + (f" [{nt}]" if nt else ""))
    grid = look_grid(th, look_of(th, slot_data, state["tier"]))
    if size == "face":
        grid = grid[:13]
    return beside(render_grid(grid, depth), len(grid[0]), info)


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
    auds = ", ".join(f"`{k}` {v['label']}" for k, v in th.audiences.items())
    axes = "; ".join(f"`{a}` {th.axes[a]['label']}: " + ", ".join(f"`{v}` {lab}" for v, lab in th.axes[a]["values"].items())
                     for a in COMPOSE_ORDER)
    return f"""---
name: docs-suit
description: 문서를 쓰거나 다듬을 때 docs-suit 테마를 입힌다. 보고서, 발표 자료, 회의록, 메일, 이력서, 자기소개서, 포트폴리오, 논문 초록, 설계 문서, PR 설명, 기획서, 업무 보고, 블로그, 뉴스레터, SNS 글을 써 달라는 요청을 받으면 쓰기 전에 이 스킬로 규칙을 조립해 따른다. 이 폴더에서는 평어체로, 팀장님께는 해요체로 써 달라는 식으로 문서의 말투나 모양을 앞으로 정해 달라는 요청도 이 스킬로 프로필이나 폴더 파일에 남긴다.
---
{EXPORT_MARK} 다시 만들려면 `{run} export` 를 돌린다. -->

# docs-suit

엔진은 `{run}` 이다. 출력은 마크다운 지침 한 장이고, 어떤 에이전트든 그대로 따르면 된다. 프로필은 폴더마다 다를 수 있으니 엔진은 사용자의 작업 폴더에서 부르고, 엔진 폴더로 옮겨 가서 부르지 않는다.

1. `{run} profile` 로 프로필이 있는지 본다. 없으면 이번 문서는 중립 기본값으로 쓰고, 다 쓴 뒤 프로필을 만들면 다음 문서부터 호칭과 말투가 맞춰진다고 권한다. 사용자가 원하거나 세팅해 달라고 하면 bootstrap 을 대신 진행하고, 사용자의 답 없이 프로필을 저장하지 않는다.
   - `{run} list --classes` 로 클래스 일곱 가지를 보여 주고 하나 고르게 한다.
   - `{run} bootstrap --questions` 가 내는 페르소나 질문을 차례로 묻는다. 답하기 싫은 질문은 비워 둔다.
   - 같은 출력의 `presets` 에 고른 클래스의 조합이 있으면, 다른 사람이 기여한 테마 조합으로 시작할지 묻는다. 추천 표시가 붙은 조합을 앞에 보인다.
   - 같은 출력의 `looks` 로 캐릭터 A 와 B 가운데 하나를 고르게 한다. 고르지 않으면 A 다.
   - `{run} bootstrap --class <클래스> --call … --affiliation … --goal … --docs <종류,종류> --facts … --dislikes … [--preset <조합>] [--look a|b] --yes` 로 저장한다.
2. 요청에서 문서 종류를 정한다. 종류는 {kinds} 이다. 맞는 것이 없으면 종류 없이 조립한다. 독자가 분명하면 `--audience <키>` 로 넘긴다. 독자 키는 {auds} 이다. 독자가 여럿이면 키를 쉼표로 잇는다.
3. 사용자가 문체, 어법, 분량, 글자수, 공개 범위를 말했으면 `--set 축=값` 과 `--chars` 로 넘긴다. 축과 값은 아래 영어 키로 쓴다. {axes}. 공개 범위는 안전 축이라 `--set exposure` 는 `team`, `submit`, `public` 순서로 더 조심하는 쪽으로만 먹는다. 사내나 팀 안에서만 볼 글이면 `--set` 대신 `--audience` 를 `teammate` 나 `peer-dev` 로 넘긴다.
4. `{run} compose --kind <종류> [--audience …] [--set …] [--chars N]` 의 출력 전체를 이번 문서의 규칙으로 따른다. 다른 문체 지침이나 스킬과 겹치면 어법, 분량, 공개 범위 같은 축의 값은 이 출력을 따른다. 지침의 공통 바닥이 시키는 대로, 쓰기 전에 틀리면 결과가 쓸모없어지는 것만 두세 개 묻는다.
5. 답을 끝내기 전에 본문을 검사한다. 검사하지 않은 답은 끝난 답이 아니다. compose 에 넘긴 `--kind`, `--audience`, `--set`, `--chars` 를 그대로 붙인다. 본문을 파일로 썼으면 `{run} check <본문 파일> --kind <종류> …` 로 부른다. 답에만 썼으면 임시 파일을 만들지 말고 본문 전체를 heredoc 으로 넘긴다.
   ```sh
   {run} check - --kind <종류> [--audience …] <<'EOF'
   (본문 전체)
   EOF
   ```
   `✗` 가 나온 축이 있으면 그 줄이 말하는 대로 한 번 고쳐 쓰고 같은 명령을 다시 부른다. 답에 보이는 본문은 마지막으로 검사에 넘긴 본문과 글자 하나까지 같게 둔다. 보일 때 제목을 굵게 바꾸는 식으로 손대지 않는다. 출력에 `성장:` 으로 시작하는 줄이 있으면 본문과 떨어뜨려 답의 맨 끝에 그 줄만 그대로 옮긴다. 이 줄은 check 만 만들 수 있으니 지어내지 않고, 문서 본문에도 넣지 않는다. `[확인 필요: …]` 표시가 남았으면 모아서 보여 준다.
6. 사용자가 말투나 모양이 마음에 안 든다고 하면 어느 축의 문제인지 짚고, 그 축의 다른 값으로 다시 조립해 대표 문단 하나를 견줘 보인다. 계속 쓰고 싶어 하면 `{run} set <축> <값> [--audience <독자>]` 로 프로필에 남긴다. 이 폴더에서만 그렇게 쓰고 싶어 하면 `--here` 를 붙여 폴더 파일 `.docs-suit.yaml` 에 남긴다.
7. 사용자가 캐릭터를 보여 달라고 하면 `{run} card --color never` 의 출력을 보여 준다. 꾸며 달라고 하면 `{run} look` 으로 열린 부위를 보고 `{run} look <부위> <값>` 을 부른다. 캐릭터 키우기를 끄거나 켜 달라고 하면 `{run} growth off` 나 `{run} growth on` 을 부른다. 성장 기록과 승급 키, 슬롯의 `look:` 절은 사용자가 부탁해도 직접 고치지 않는다. 레벨은 문서를 써서 오르고, 3차와 4차 전직은 저장소에 기여하고 받은 승급 키를 `{run} promote <키>` 로 넣어야 열린다고 알려 준다.
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
    preset = None
    order = preset_order(th, cls)
    if order:
        print("다른 사람이 기여한 테마 조합으로 시작할 수 있다. Enter 면 클래스 기본값으로 시작한다.\n")
        for i, k in enumerate(order, 1):
            v = th.presets[k]
            mark = " · 추천" if str(v.get("featured")) == "true" else ""
            print(f"  {i}. {v.get('label', k)} · @{v.get('by', '')}{mark}\n     {v.get('desc', '')}")
        picked = _pick_numbers(_ask("\n번호를 고른다: "), order)
        preset = picked[0] if picked else None
        print()
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
    names = ["claude", "codex", "antigravity", "cursor", "grok", "web"]
    labels = {"claude": "Claude Code", "codex": "Codex CLI", "antigravity": "Antigravity CLI", "cursor": "Cursor",
              "grok": "Grok Build", "web": "웹 채팅 (ChatGPT, Claude, Gemini, Grok 에 붙여 넣기)"}
    for i, n in enumerate(names, 1):
        print(f"  {i}. {labels[n]}")
    agents = _pick_numbers(_ask("\n번호를 쉼표로 이어 고른다: "), names)
    print("\n4단계. 캐릭터. 문서를 쓸수록 자라고, 전직하면 칭호와 꾸미기 거리가 열린다.\n")
    bases = list(th.look.get("base") or {})
    depth = color_depth()
    if depth and bases:
        grids = [look_grid(th, look_of(th, {"look": {"base": b}})) for b in bases]
        arts = [render_grid(g, depth) for g in grids]
        for row in zip(*arts):
            print("  " + "    ".join(row))
    for i, b in enumerate(bases, 1):
        print(f"  {i}. {th.look['base'][b]['label']}")
    picked = _pick_numbers(_ask("\n번호를 고른다. Enter 면 1번: "), bases)
    return cls, persona, agents, (picked[0] if picked else None), preset


def cmd_bootstrap(a, th):
    if a.questions:
        print(json.dumps({"classes": {k: {"label": v["label"], "desc": v["desc"], "kinds": v["kinds"]}
                                      for k, v in th.classes.items()},
                          "questions": th.persona,
                          "presets": [{"name": k, "label": th.presets[k].get("label"), "desc": th.presets[k].get("desc"),
                                       "class": th.presets[k].get("class"),
                                       "featured": str(th.presets[k].get("featured")) == "true"}
                                      for k in preset_order(th)],
                          "looks": {k: v["label"] for k, v in (th.look.get("base") or {}).items()}},
                         ensure_ascii=False, indent=1))
        return 0
    p = profile_path(a.profile)
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
        base, preset = a.look, a.preset
    else:
        if not sys.stdin.isatty():
            raise Missing("대화형 입력을 받을 수 없다. --class 와 --yes 로 진행한다")
        cls, persona, agents, base, preset = bootstrap_interactive(th)
    expand_agents(agents)
    if base and base not in (th.look.get("base") or {}):
        raise Missing(f"모르는 캐릭터: {base}. 고를 수 있는 것은 {', '.join(th.look.get('base') or {})}")
    data = {"profile": {"class": cls, "lang": DEFAULT_LANG}, "persona": persona}
    if base:
        data["look"] = {"base": base}
    if preset:
        if preset not in th.presets:
            raise Missing(f"모르는 조합: {preset}. 고를 수 있는 조합은 {', '.join(preset_order(th)) or '없음'}")
        apply_preset(data, th.presets[preset])
    if agents:
        data["profile"]["agents"] = agents
    if p.exists():
        p.with_name(p.name + ".bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"\n프로필을 저장했다: {write_profile(data, a.profile)}")
    if agents:
        if not a.yes and _ask("고른 도구에 스킬을 설치할까? [Y/n] ", "y").lower() not in ("y", "yes", "ㅛ"):
            print("설치를 건너뛰었다. 나중에 `suit.py export --agent …` 로 설치한다.")
        else:
            export(th, agents, profile=load_profile(name=a.profile))
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
    path, slot, folder, why = profile_source(a.profile)
    if a.action == "list":
        slots = ["default"] + sorted(f.stem for f in (config_dir() / "profiles").glob("*.yaml"))
        for name in slots:
            mark = "*" if name == slot else " "
            note = "" if slot_path(name).exists() else "  아직 없음"
            print(f"{mark} {name:<12} {slot_path(name)}{note}")
        for f in folder:
            print(f"폴더 파일: {f}")
        return 0
    if a.action == "use":
        if not a.name:
            raise Missing("슬롯 이름을 준다: suit.py profile use <이름> [--here]")
        target = slot_path(a.name)
        if a.here:
            data = read_folder(Path.cwd() / FOLDER_FILE, warn_stderr)
            data = {"profile": a.name, **{k: v for k, v in data.items() if k != "profile"}}
            print(f"폴더 파일 {write_folder(data)} 이 슬롯 {a.name} 을 쓴다")
        else:
            current = config_dir() / "current"
            current.parent.mkdir(parents=True, exist_ok=True)
            if a.name == "default":
                current.unlink(missing_ok=True)
            else:
                current.write_text(a.name + "\n", encoding="utf-8")
            print(f"이제 슬롯 {a.name} 을 쓴다. 폴더 파일이 있는 폴더에서는 폴더 파일이 앞선다")
        if not target.exists():
            print(f"슬롯 {a.name} 은 아직 없다. `python3 suit.py bootstrap --profile {a.name}` 으로 만든다")
        return 0
    reason = {"env": "환경 변수 DOCS_SUIT_PROFILE", "arg": "--profile 인자", "folder": "폴더 파일",
              "current": "profile use 로 고른 슬롯", "default": "기본 슬롯"}[why]
    if not path.exists():
        print(f"프로필이 없다: {path}\n`python3 suit.py bootstrap` 으로 만든다. 슬롯 {slot or '-'} ({reason})")
    else:
        print(f"# 슬롯 {slot or '-'}: {path} ({reason})\n")
        print(path.read_text(encoding="utf-8"))
    for f in reversed(folder):
        print(f"\n# 폴더 파일 {f} 이 얹는 값. 아래 파일일수록 앞선다\n")
        print(f.read_text(encoding="utf-8"))
    return 0  # 프로필이 없는 것은 오류가 아니다. 에이전트가 && 로 이은 다음 명령이 끊기지 않게 한다


def cmd_get(a, th):
    vals, auds, cls = resolve(th, a.kind, _auds(a.audience), _sets(a.set), load_profile(warn_stderr, a.profile), a.cls,
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
    text, _ = compose(th, a.kind, _auds(a.audience), _sets(a.set), load_profile(warn_stderr, a.profile), a.cls,
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
    # 쓸 때는 폴더 값을 얹지 않은 원본에 쓴다. --here 는 지금 폴더의 폴더 파일에 쓴다.
    data = read_folder(Path.cwd() / FOLDER_FILE, warn_stderr) if a.here else read_slot(profile_path(a.profile), warn_stderr)
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
    p = write_folder(data) if a.here else write_profile(data, a.profile)
    where = f"독자 {a.audience}" if a.audience else "기본값"
    print(f"{'폴더 파일' if a.here else '프로필'} {p} 의 {where} 에 {a.axis}={'(지움)' if a.unset else a.value}")
    return 0


def cmd_export(a, th):
    agents = [x.strip() for x in a.agent.split(",") if x.strip()]
    export(th, agents, a.dest, a.dry_run, load_profile(warn_stderr, a.profile))
    return 0


def cmd_check(a, th):
    text = sys.stdin.read() if a.file == "-" else Path(a.file).expanduser().read_text(encoding="utf-8")
    if not text.strip():
        print("오류: 본문이 비어 있다. 파일 경로를 주거나, - 를 쓰고 본문 전체를 heredoc 으로 넘긴다: "
              "check - --kind <종류> <<'EOF' … EOF", file=sys.stderr)
        return 1
    vals, auds, _ = resolve(th, a.kind, _auds(a.audience), _sets(a.set), load_profile(warn_stderr, a.profile), a.cls,
                            warn_stderr)
    checks = check_doc(text, vals, a.chars, a.kind)
    left = len(UNRESOLVED.findall(text))
    line = None if a.no_record else record_check(th, a.profile, a.file, text, a.kind, checks, left, warn_stderr)
    if a.json:
        print(json.dumps({"checks": [{"axis": ax, "ok": ok, "got": got} for ax, ok, got in checks],
                          "unresolved": left, "growth": line}, ensure_ascii=False, indent=1))
        return 0
    kind_label = th.kinds[a.kind]["label"] if a.kind else "일반 글"
    print(f"검사 · {kind_label} · 독자 {', '.join(th.audiences[x]['label'] for x in auds) or '정하지 않음'}")
    for ax, ok, got in checks:
        print(f"{'✓' if ok else '✗'} {th.axes[ax]['label']}: {got}" + ("" if ok else f". {check_hint(th, ax, vals)}"))
    if not checks:
        print("· 잴 거리가 없다")
    if left:
        print(f"· [확인 필요] {left}곳이 남았다")
    if line:
        print(line)
    return 0


def cmd_card(a, th):
    path, slot, _, _ = profile_source(a.profile)
    data = read_slot(path, warn_stderr)
    if not data:
        print(f"프로필이 없다: {path}\n`python3 suit.py bootstrap` 으로 캐릭터를 만든다")
        return 3
    held = promote_keys(warn_stderr)
    state = growth_state(th, read_growth(growth_path(a.profile), warn_stderr), key_tiers(held))
    if a.json:
        cls = (data.get("profile") or {}).get("class")
        print(json.dumps({"slot": slot, "name": (data.get("persona") or {}).get("call") or slot, "class": cls,
                          "title": title_of(th, cls, state["tier"]), "look": look_of(th, data, state["tier"]), "on": growth_on(data),
                          "keys": [{k: p[k] for k in ("tier", "who", "ref", "at") if k in p} for p in held],
                          **{k: v for k, v in state.items() if k != "gains"}}, ensure_ascii=False, indent=1))
        return 0
    vals = resolve(th, profile=load_profile(warn_stderr, a.profile), warn=warn_stderr)[0]
    print("\n".join(card_lines(th, data, slot, state, color_depth(a.color), vals, held)))
    return 0


def cmd_look(a, th):
    """꾸미기를 보거나 바꾼다. 캐릭터 A, B 는 언제든, 나머지는 전직해서 연 부위만 바꾼다."""
    path, slot, _, _ = profile_source(a.profile)
    data = read_slot(path, warn_stderr)
    if not data:
        print(f"프로필이 없다: {path}\n`python3 suit.py bootstrap` 으로 캐릭터를 만든다")
        return 3
    tier = growth_state(th, read_growth(growth_path(a.profile), warn_stderr), key_tiers(promote_keys(warn_stderr)))["tier"]
    look = look_of(th, data, tier, warn_stderr)
    unlock = th.look.get("unlock") or {}
    tables = {"base": {k: v["label"] for k, v in th.look["base"].items()}, "top": th.look["top"],
              "hair": th.look["hair"], "prop": th.look["prop"],
              "color": {k: v["label"] for k, v in th.look["colors"].items()}}
    labels = {"base": "캐릭터", **{k: v["label"] for k, v in unlock.items()}}
    is_open = {k: k == "base" or tier >= int(unlock[k]["at"]) for k in tables}
    if a.json:
        print(json.dumps({"look": look, "tier": tier, "open": is_open, "options": tables}, ensure_ascii=False, indent=1))
        return 0
    if not a.part:
        print(("아직 전직 전이다" if not tier else f"{tier}차 전직까지 마쳤다") + ". 바꾸려면 suit.py look <부위> <값>")
        for part in ("base", "color", "hair", "prop", "top"):
            now = tables[part].get(look[part]) if look[part] else ("기본" if part == "color" else "없음")
            if is_open[part]:
                opts = ", ".join(f"{k} {v}" for k, v in tables[part].items())
                print(f"- {labels[part]} ({part}): 지금 {now}. 고를 수 있는 값 {opts}")
            else:
                print(f"- {labels[part]} ({part}): 지금 {now}. {unlock[part]['at']}차 전직에서 열린다")
        return 0
    if a.part not in tables:
        raise Missing(f"모르는 부위: {a.part}. 부위는 {', '.join(tables)}")
    if not is_open[a.part]:
        print(f"{labels[a.part]}: {unlock[a.part]['at']}차 전직에서 열린다. 지금은 {tier}차다")
        return 1
    if not a.value:
        raise Missing(f"값을 준다: suit.py look {a.part} <값>. 고를 수 있는 값은 {', '.join(tables[a.part])}")
    want = dict(data.get("look") or {}) if isinstance(data.get("look"), dict) else {}
    if a.value == "none" and a.part in ("prop", "color"):
        want.pop(a.part, None)
    elif a.value not in tables[a.part]:
        raise Missing(f"모르는 값: {a.part}={a.value}. 고를 수 있는 값은 {', '.join(tables[a.part])}")
    else:
        want[a.part] = a.value
    data["look"] = want
    write_profile(data, a.profile)
    print(f"바꿨다: {labels[a.part]} → {tables[a.part].get(a.value, '없음')}. suit.py card 로 본다")
    return 0


def cmd_preset(a, th):
    """테마 조합 보기, 입히기, 내 설정을 조합 파일로 내보내기."""
    if a.action == "list":
        order = preset_order(th, a.cls)
        if not order:
            print("아직 조합이 없다")
        for k in order:
            v = th.presets[k]
            mark = " · 추천" if str(v.get("featured")) == "true" else ""
            cls = th.classes.get(v.get("class"), {}).get("label", "클래스 없음")
            print(f"- {k}: {v.get('label', k)} · {cls} · @{v.get('by', '')}{mark}\n  {v.get('desc', '')}")
        return 0
    if not a.name:
        raise Missing(f"조합 이름을 준다: suit.py preset {a.action} <이름>")
    if a.action == "export":
        if not SLOT_RE.match(a.name):
            raise Missing(f"조합 이름은 글자, 숫자, -, _ 로 쓴다: {a.name}")
        if not a.by:
            raise Missing("--by 에 GitHub 아이디를 준다. 기여한 사람으로 남고 승급 키를 받을 때 쓴다")
        prof = load_profile(warn_stderr, a.profile)
        defaults = known_values(th, prof.get("defaults"))
        auds = {k: known_values(th, v) for k, v in (prof.get("audiences") or {}).items()
                if k in th.audiences and isinstance(v, dict) and known_values(th, v)}
        if not defaults and not auds:
            print("오류: 내보낼 축 값이 없다. suit.py set 으로 고른 값이 있어야 조합이 된다", file=sys.stderr)
            return 1
        meta = {"label": a.label or a.name, "desc": a.desc or "", "by": a.by.lstrip("@"),
                "class": (prof.get("profile") or {}).get("class", "")}
        out = Path(a.output or f"{a.name}.yaml").expanduser()
        out.write_text(dump_yaml({"preset": {k: v for k, v in meta.items() if v}, "defaults": defaults,
                                  "audiences": auds}, PRESET_HEAD), encoding="utf-8")
        print(f"썼다: {out}\n이 파일을 docs-suit 저장소의 themes/ko/presets/ 에 넣어 PR 을 보낸다. "
              "머지되면 4차 승급 키를 받는다" + ("" if a.desc else ". --desc 로 쓰임새를 한 줄 적으면 고르는 사람이 알아보기 쉽다"))
        return 0
    if a.name not in th.presets:
        raise Missing(f"모르는 조합: {a.name}. 고를 수 있는 조합은 {', '.join(preset_order(th)) or '없음'}")
    v = th.presets[a.name]
    if a.action == "show":
        print(f"{v.get('label', a.name)} · @{v.get('by', '')}\n{v.get('desc', '')}")
        for axis, value in (v.get("defaults") or {}).items():
            print(f"- {th.axes[axis]['label']}: {th.label(axis, value)}")
        for aud, vals in (v.get("audiences") or {}).items():
            print(f"- 독자 {th.audiences[aud]['label']}: " + ", ".join(f"{th.axes[x]['label']} {th.label(x, y)}"
                                                                    for x, y in vals.items()))
        return 0
    if a.here:
        data = read_folder(Path.cwd() / FOLDER_FILE, warn_stderr)
        where = write_folder(apply_preset(data, v))
    else:
        path = profile_path(a.profile)
        data = read_slot(path, warn_stderr)
        if path.exists():
            path.with_name(path.name + ".bak").write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        where = write_profile(apply_preset(data, v), a.profile)
    print(f"입혔다: {v.get('label', a.name)} → {where}. 축 기본값과 독자별 값을 이 조합으로 바꿨다")
    return 0


def cmd_promote(a, th):
    """승급 키를 넣거나, 받은 키를 보인다."""
    held = promote_keys(warn_stderr)
    if not a.key:
        if not held:
            print("받은 승급 키가 없다. 저장소에 기여하고 받은 키를 suit.py promote <키> 로 넣는다")
        for k in held:
            print(f"- {k['tier']}차 승급 키 · @{k['who']} · {k.get('ref', '')} · {k.get('at', '')}")
        return 0
    payload = read_promote_key(a.key)
    if not payload:
        print("오류: 승급 키가 맞지 않는다. 받은 키 전체를 줄바꿈 없이 그대로 넣는다", file=sys.stderr)
        return 1
    path = keys_path()
    have = path.read_text(encoding="utf-8").split() if path.exists() else []
    if a.key.strip() not in have:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(a.key.strip() + "\n")
    print(f"승급 키를 받았다: {payload['tier']}차 · @{payload['who']} · {payload.get('ref', '')}")
    data = read_slot(profile_path(a.profile), warn_stderr)
    if data:
        before = growth_state(th, read_growth(growth_path(a.profile), warn_stderr), key_tiers(held))
        after = growth_state(th, read_growth(growth_path(a.profile), warn_stderr), key_tiers(held + [payload]))
        cls = (data.get("profile") or {}).get("class")
        for tier in range(before["tier"] + 1, after["tier"] + 1):
            print(f"전직 [{title_of(th, cls, tier)}]" + "".join(f" · {label} 열림" for label in opened_at(th, tier)))
        if after["tier"] == before["tier"]:
            lv = next((lv for t, lv, _ in promote_rules(th) if t == after["tier"] + 1), None)
            print(f"지금 Lv.{after['level']}" + (f". Lv.{lv} 이 되면 전직한다" if lv else ""))
    return 0


def cmd_growth(a, th):
    path = profile_path(a.profile)
    data = read_slot(path, warn_stderr)
    if not data:
        print(f"프로필이 없다: {path}\n`python3 suit.py bootstrap` 으로 캐릭터를 만든다")
        return 3
    meta = data.get("profile") if isinstance(data.get("profile"), dict) else {}
    meta["growth"] = a.action
    data["profile"] = meta
    write_profile(data, a.profile)
    print(f"캐릭터 키우기를 {'켰다' if a.action == 'on' else '껐다'}: {path}. 지난 기록은 그대로 둔다")
    return 0


def cmd_status(a, th):
    """상태 줄에 캐릭터를 그린다. 슬롯이 없거나 캐릭터 키우기가 꺼져 있으면 아무것도 내지 않는다."""
    piped = "" if sys.stdin.isatty() else sys.stdin.read()
    cwd = a.cwd or status_cwd(piped) or os.getcwd()
    path, slot, _, _ = profile_source(a.profile, start=cwd)
    data = read_slot(path)
    if not growth_on(data):
        return 0
    held = promote_keys()
    state = growth_state(th, read_growth(growth_path(a.profile, start=cwd)), key_tiers(held))
    depth = color_depth("never" if os.environ.get("NO_COLOR") else "always")
    print("\n".join(status_lines(th, data, slot, state, depth, a.size, held)))
    return 0


def widget_frame(th, cwd, width, depth, events=()):
    """캐릭터 창 한 장. 칸이 좁으면 그림 아래로 글을 내린다. events 는 최근 성장 줄들이다."""
    path, slot, _, _ = profile_source(None, start=cwd)
    data = read_slot(path)
    if not data:
        return ["이 폴더에는 docs-suit 슬롯이 없다.", "python3 suit.py bootstrap 으로 캐릭터를 만든다"]
    if not growth_on(data):
        return ["캐릭터 키우기가 꺼져 있다.", "켜려면 python3 suit.py growth on"]
    held = promote_keys()
    state = growth_state(th, read_growth(growth_path(start=cwd)), key_tiers(held))
    vals = resolve(th, profile=load_profile(start=cwd))[0]
    lines = card_lines(th, data, slot, state, depth, vals, held)
    if max(display_width(x) for x in lines) > width:
        lines = card_lines(th, data, slot, state, depth, vals, held, stacked=True)
    if events:
        lines += ["", "최근 기록"] + [f"\033[1m{e}\033[0m" if depth else e for e in events]
    return lines


def widget_watch(cwd):
    """다시 그릴지 가르는 지문. 슬롯, 폴더 파일, 성장 기록, 승급 키 파일의 수정 시각이다."""
    path, _, folder, _ = profile_source(None, start=cwd)
    files = [path, growth_path(start=cwd), keys_path(), *folder]
    return tuple(f.stat().st_mtime if f.exists() else 0 for f in files)


def cmd_widget(a, th):
    """터미널 옆 칸에 캐릭터 창을 띄운다. 기록이 바뀌면 다시 그린다. Codex 처럼 상태 줄이 없는 에이전트 옆에 둔다."""
    cwd = os.path.abspath(os.path.expanduser(a.cwd or os.getcwd()))
    if a.split:
        cmd = shlex.join([sys.executable, str(HERE / "suit.py"), "widget", "--cwd", cwd])
        if os.environ.get("HERDR_ENV") == "1" and os.environ.get("HERDR_PANE_ID"):
            # herdr 는 칸을 나누고 새 칸 번호를 JSON 으로 돌려준 뒤, 그 칸에 명령을 넣고 Enter 를 누른다
            out = subprocess.run(["herdr", "pane", "split", "--current", "--direction", "right", "--cwd", cwd],
                                 capture_output=True, text=True, check=True).stdout
            pane = json.loads(out)["result"]["pane"]["pane_id"]
            subprocess.run(["herdr", "pane", "run", pane, cmd], capture_output=True, check=True)
        elif os.environ.get("TMUX"):
            subprocess.run(["tmux", "split-window", "-h", "-d", "-l", str(a.width), cmd], check=True)
        else:
            print("herdr 나 tmux 안에서 돌릴 때만 칸을 나눈다. 터미널 앱의 창 나누기로 옆 칸을 열고 "
                  f"`python3 {HERE / 'suit.py'} widget` 을 돌려도 된다", file=sys.stderr)
            return 1
        print("오른쪽 칸에 캐릭터 창을 띄웠다. 닫으려면 그 칸에서 Ctrl+C")
        return 0
    depth = color_depth("never" if os.environ.get("NO_COLOR") else "always")
    if a.once:
        print("\n".join(widget_frame(th, cwd, shutil.get_terminal_size().columns, depth)))
        return 0
    events, last = [], None
    count = len(read_growth(growth_path(start=cwd)))

    def stop(signum, frame):
        raise KeyboardInterrupt  # 칸을 닫거나 kill 해도 커서를 되돌리고 끝낸다

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGHUP, stop)
    sys.stdout.write("\033[?25l")
    try:
        while True:
            now = (widget_watch(cwd), shutil.get_terminal_size())
            if now != last:
                entries = read_growth(growth_path(start=cwd))
                if len(entries) > count:
                    data = read_slot(profile_source(None, start=cwd)[0])
                    keys = key_tiers(promote_keys())
                    cls = (data.get("profile") or {}).get("class")
                    for i in range(count, len(entries)):
                        before, after = growth_state(th, entries[:i], keys), growth_state(th, entries[:i + 1], keys)
                        events.append(growth_line(th, before, after, entries[i]["doc"], entries[i].get("kind"), cls))
                    events = events[-3:]
                count = len(entries)
                frame = widget_frame(th, cwd, now[1].columns, depth, events)
                sys.stdout.write("\033[H\033[2J" + "\n".join(frame) + "\n")
                sys.stdout.flush()
                last = now
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h\033[0m\n")
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
        old = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = open(os.devnull, "w")
        try:
            return fn(*args)
        finally:
            sys.stdout.close()
            sys.stdout, sys.stderr = old

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
    gr = th.growth
    for k in ("done", "clean", "resolved", "new-kind"):
        spec = (gr.get("exp") or {}).get(k)
        check(isinstance(spec, dict) and str(spec.get("points", "")).isdigit() and spec.get("label"),
              f"growth.yaml 의 exp.{k} 에 points 나 label 이 없다")
    check(str((gr.get("limit") or {}).get("daily-kind", "")).isdigit(), "growth.yaml 의 limit.daily-kind 가 없다")
    lv = gr.get("level") or {}
    check("1" in lv and all(str(k).isdigit() and str(v).isdigit() and int(v) > 0 for k, v in lv.items()),
          "growth.yaml 의 level 은 1 레벨부터 `시작 레벨: 경험치` 꼴이어야 한다")
    promote = gr.get("promote") or {}
    try:
        rules_p = promote_rules(th)
        steps = [lvl for _, lvl, _ in rules_p]
        check([t for t, _, _ in rules_p] == [1, 2, 3, 4] and steps == sorted(set(steps))
              and steps[-1] < int(gr.get("max") or steps[-1] + 1),
              "growth.yaml 의 promote 는 1차부터 4차까지 커지는 레벨이고 최고 레벨보다 낮아야 한다")
    except (KeyError, TypeError, ValueError, AttributeError):
        problems.append("growth.yaml 의 promote 는 `차수: {level: 레벨}` 꼴이어야 한다")
    for k, v in th.classes.items():
        check(len(v["titles"]) == len(promote) + 1, f"클래스 {k} 의 칭호는 기본과 전직 차수만큼 {len(promote) + 1}개다")

    for k, v in th.presets.items():
        check(SLOT_RE.match(k) and v.get("label") and v.get("desc") and v.get("by"),
              f"조합 {k} 에 label, desc, by 가 없거나 이름이 다르다")
        check(not v.get("class") or v.get("class") in th.classes, f"조합 {k} 의 클래스를 모른다")
        check(str(v.get("featured", "false")) in ("true", "false"), f"조합 {k} 의 featured 는 true 나 false 다")
        check(v.get("defaults") or v.get("audiences"), f"조합 {k} 에 축 값이 없다")
        check_profile(f"조합 {k}", v.get("defaults") or {}, False)
        for aud, vals in (v.get("audiences") or {}).items():
            check(aud in th.audiences and isinstance(vals, dict), f"조합 {k} 의 독자 {aud} 를 모른다")
            check_profile(f"조합 {k} 독자 {aud}", vals if isinstance(vals, dict) else {}, False)

    # 캐릭터 그림과 꾸미기. 모든 그림은 기본 몸과 같은 크기라야 겹쳐 그릴 수 있다.
    lk = th.look
    check(lk.get("base") and all(v.get("hair") in (lk.get("hair") or {}) for v in lk["base"].values()),
          "look.yaml 의 base 가 없거나 처음 머리 모양을 모른다")
    check(set(lk.get("unlock") or {}) == {"color", "hair", "prop", "top"}
          and all(str(v.get("at", "")).isdigit() and v.get("label") for v in lk["unlock"].values()),
          "look.yaml 의 unlock 에 color, hair, prop, top 의 at 과 label 이 있어야 한다")
    check("shirt" in (lk.get("top") or {}), "look.yaml 의 top 에 기본 옷 shirt 가 없다")
    for k, v in (lk.get("colors") or {}).items():
        check(re.match(r"^#[0-9a-fA-F]{6}$", str(v.get("color", ""))) and v.get("label"), f"look.yaml 의 색 {k} 이 다르다")
    listed = {("base", k) for k in lk.get("base") or {}} | {(part, k) for part in LOOK_LAYERS for k in lk.get(part) or {}}
    found = {(f.parent.name, f.stem) for f in (th.root / "sprites").glob("*/*.txt")}
    check(listed == found, f"look.yaml 과 sprites 폴더가 다르다. 그림 없음 {sorted(listed - found)}, 목록에 없음 {sorted(found - listed)}")
    size = None
    for part, name in sorted(found):
        f = th.part_path(part, name)
        pal, rows = read_sprite(f)
        here = (len(rows), len(rows[0]) if rows else 0)
        size = size or here
        check(rows and len({len(r) for r in rows}) == 1 and here == size, f"그림 크기가 다르다: sprites/{part}/{name}.txt")
        bad = sorted({ch for r in rows for ch in r if ch != "." and ch not in pal})
        check(not bad, f"팔레트에 없는 글자 {bad}: sprites/{part}/{name}.txt")
        check(all(re.match(r"^#[0-9a-fA-F]{6}$", x["color"]) for x in pal.values()), f"색은 #rrggbb 로 쓴다: sprites/{part}/{name}.txt")
        mine = sum(1 for x in pal.values() if x["custom"])
        check(mine == (1 if part == "top" else 0), f"* 는 옷에만 하나 둔다: sprites/{part}/{name}.txt")
    if lk.get("colors") and not problems:
        grid = look_grid(th, look_of(th, {"look": {"base": "b", "top": "suit", "prop": "tie", "color": "wine"}}))
        check(any(lk["colors"]["wine"]["color"] in row for row in grid), "옷 색 바꾸기가 그림에 먹지 않는다")
        check(look_of(th, {"look": {"top": "nope"}})["top"] == "shirt", "모르는 옷을 기본 옷으로 돌리지 않는다")

    # 본문 검사와 경험치 계약. 경험치 숫자는 growth.yaml 과 상관없이 고정한 규칙으로 잰다.
    vals = {"register": ("polite", ""), "skeleton": ("bluf", ""), "voice": ("prose", ""), "length": ("brief", ""),
            "emphasis": ("none", "")}
    got = {ax: ok for ax, ok, _ in check_doc("보고드립니다.\n확인했습니다.\n**진행합니다.**\n", vals, None)}
    check(got.get("register") is True and got.get("emphasis") is False and got.get("length") is True,
          f"본문 검사가 어법, 강조, 분량을 다르게 잰다: {got}")
    got = {ax: ok for ax, ok, _ in check_doc("간다. 본다. 한다. 쓴다.\n" * 40, vals, 100)}
    check(got.get("register") is False and got.get("length") is False, f"본문 검사가 어법이나 글자수 한도를 놓친다: {got}")
    rules = argparse.Namespace(growth={
        "exp": {k: {"points": p, "label": k} for k, p in (("done", "10"), ("clean", "10"), ("resolved", "5"), ("new-kind", "20"))},
        "limit": {"daily-kind": "2"}, "level": {"1": "50", "2": "75"}, "max": "4",
        "promote": {"1": {"level": "2"}, "2": {"level": "3", "key": "true"}}})
    day1, day2 = "2026-01-01T09:00", "2026-01-02T09:00"
    log = [{"doc": "a", "at": day1, "kind": "email", "checks": {"emphasis": False}, "unresolved": 1},
           {"doc": "a", "at": day1, "kind": "email", "checks": {"emphasis": True}, "unresolved": 0},
           {"doc": "b", "at": day1, "kind": "email", "checks": {}, "unresolved": 0},
           {"doc": "c", "at": day1, "kind": "email", "checks": {}, "unresolved": 0},
           {"doc": "d", "at": day2, "kind": "email", "checks": {}, "unresolved": 0}]
    st = growth_state(rules, log)
    check((st["exp"], st["level"], st["into"], st["need"], st["docs"]) == (85, 2, 35, 75, 4),
          f"경험치 계산이 다르다. 같은 문서는 가장 좋은 기록, 같은 날 같은 종류는 두 건까지다: {st}")
    check(st["gains"]["a"] == ["done", "clean", "resolved", "new-kind"] and st["gains"]["b"] == ["done", "clean"],
          f"[확인 필요] 를 채운 문서만 resolved 를 받아야 한다: {st['gains']}")
    st = growth_state(rules, log + [{"doc": "a", "at": day2, "kind": "email", "checks": {"emphasis": False}, "unresolved": 3}])
    check(st["exp"] == 85, "다시 검사해 나빠진 기록이 경험치를 깎았다")
    check(level_of(rules, 50 + 75) == (3, 0, 75) and level_of(rules, 50 + 75 * 2 + 30) == (4, 30, 0),
          "레벨 구간이나 최고 레벨 계산이 다르다")
    check([tier_of(rules, x) for x in (1, 2, 3)] == [0, 1, 1] and tier_of(rules, 3, {2}) == 2,
          "전직 차수 계산이 다르다. 키가 걸린 차수는 키가 있어야 오른다")
    check(title_of(th, "office", 0) == th.classes["office"]["titles"][0]
          and title_of(th, "office", 9) == th.classes["office"]["titles"][-1], "칭호를 차수로 고르지 못한다")

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
        check(vals["exposure"] == ("public", "arg"), "더 조심하는 공개 범위 인자가 졌다")
        vals, _, _ = resolve(th, kind="report", sets={"exposure": "team"})
        check(vals["exposure"][0] == "submit", "덜 조심하는 공개 범위 인자가 이겼다")
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
        check("- 호칭: 민수 님" in text and "- 클래스: 학생" in text and "report" not in text.split("## 쓰는 사람")[1][:200],
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
            ns = argparse.Namespace(questions=False, force=False, cls="developer", yes=True, profile=None,
                                    call='민수 "님"', affiliation="백엔드, 2년 차: 결제", goal=None,
                                    facts="#1 은 지도 시각화", dislikes=None, docs="pr,design-doc", agents="", look="b",
                                    preset=next(iter(th.presets), None))
            quiet(cmd_bootstrap, ns, th)
            prof = load_profile(start=td)
            check(prof.get("profile", {}).get("class") == "developer", "bootstrap 이 클래스를 남기지 않았다")
            check(prof.get("look") == {"base": "b"}, "bootstrap 이 캐릭터를 남기지 않았다")
            if th.presets:
                check(prof.get("defaults") == th.presets[next(iter(th.presets))]["defaults"],
                      "bootstrap 이 고른 조합으로 시작하지 않았다")
            per = prof.get("persona", {})
            check(per.get("affiliation") == "백엔드, 2년 차: 결제" and per.get("facts") == "#1 은 지도 시각화"
                  and per.get("docs") == ["pr", "design-doc"] and "”" in per.get("call", ""),
                  f"페르소나가 그대로 읽히지 않는다: {per}")
            check(quiet(cmd_bootstrap, ns, th) == 1, "프로필이 있는데 --force 없이 덮어썼다")
            quiet(cmd_set, argparse.Namespace(axis="register", value="haeyo", unset=False, audience="peer-dev",
                                                 here=False, profile=None), th)
            vals, _, _ = resolve(th, kind="pr", profile=load_profile(start=td))
            check(vals["register"] == ("haeyo", "profile-audience"), "set 으로 쓴 프로필 값을 읽지 못한다")
            check(load_profile(start=td).get("persona", {}).get("affiliation") == "백엔드, 2년 차: 결제", "set 이 페르소나를 망가뜨렸다")
            out = Path(td) / "export"
            paths = quiet(export, th, ["all"], str(out), False, load_profile(start=td))
            check(len(paths) == len(AGENT_TARGETS), "export 가 모든 자리에 쓰지 않았다")
            skill = (out / "claude" / "SKILL.md").read_text(encoding="utf-8")
            check(skill.startswith("---\nname: docs-suit") and EXPORT_MARK in skill and str(HERE / "suit.py") in skill,
                  "SKILL.md 머리나 엔진 경로가 다르다")
            check(all(f"`{k}`" in skill for k in list(th.kinds) + list(th.audiences) + list(th.axes)),
                  "SKILL.md 에 빠진 문서 종류나 독자, 축 키가 있다")
            web = (out / "web" / "prompt.md").read_text(encoding="utf-8")
            check("- 클래스: 개발자" in web, "웹 지침에 쓰는 사람 절이 없다")
            (out / "antigravity" / "SKILL.md").write_text("내가 만든 스킬", encoding="utf-8")
            quiet(export, th, ["gemini"], str(out), False, None)
            check((out / "antigravity" / "SKILL.md").read_text(encoding="utf-8") == "내가 만든 스킬",
                  "export 가 손으로 만든 SKILL.md 를 덮어썼다")
            check("check - --kind" in skill and "<<'EOF'" in skill and "growth off" in skill,
                  "SKILL.md 에 검사 단계나 캐릭터 끄기가 없다")
            check("--preset <조합>" in skill and "--look a|b" in skill and "promote <키>" in skill,
                  "SKILL.md 에 조합이나 캐릭터 고르기, 승급 키 안내가 없다")
            doc = Path(td) / "pr.md"
            doc.write_text("## 바뀐 것\n\n결제 재시도를 붙였다.\n테스트를 더했다.\n", encoding="utf-8")
            ns = argparse.Namespace(file=str(doc), cls=None, kind="pr", audience=None, set=None, chars=None,
                                    no_record=False, json=True, profile=None)
            grow = growth_path()
            quiet(cmd_check, ns, th)
            quiet(cmd_check, ns, th)
            check(grow == Path(td) / "profile.growth.jsonl" and len(read_growth(grow)) == 2,
                  "환경 변수로 정한 프로필 옆에 성장 기록이 남지 않는다")
            entry = read_growth(grow)[0]
            check(set(entry) == {"v", "at", "doc", "kind", "checks", "unresolved", "chars"} and str(td) not in json.dumps(entry),
                  f"성장 기록에 본문이나 경로가 남는다: {entry}")
            check(growth_state(th, read_growth(grow))["docs"] == 1, "같은 파일을 다시 검사했는데 문서가 두 건으로 셌다")
            empty = Path(td) / "empty.md"
            empty.write_text("\n", encoding="utf-8")
            code = quiet(cmd_check, argparse.Namespace(**{**vars(ns), "file": str(empty)}), th)
            check(code == 1 and len(read_growth(grow)) == 2, "빈 본문을 검사해 통과시키거나 기록했다")
            quiet(cmd_check, argparse.Namespace(**{**vars(ns), "no_record": True}), th)
            check(len(read_growth(grow)) == 2, "--no-record 인데 기록이 남았다")
            look_ns = argparse.Namespace(part="color", value="navy", json=False, profile=None)
            check(quiet(cmd_look, look_ns, th) == 1 and "color" not in (read_slot(profile_path()).get("look") or {}),
                  "전직 전인데 옷 색을 바꿨다")
            quiet(cmd_look, argparse.Namespace(part="base", value="a", json=False, profile=None), th)
            check(read_slot(profile_path()).get("look") == {"base": "a"}
                  and read_slot(profile_path()).get("persona", {}).get("affiliation") == "백엔드, 2년 차: 결제",
                  "look 이 캐릭터를 바꾸지 못하거나 프로필을 망가뜨렸다")
            quiet(cmd_growth, argparse.Namespace(action="off", profile=None), th)
            quiet(cmd_check, ns, th)
            check(len(read_growth(grow)) == 2 and not growth_on(read_slot(profile_path())), "캐릭터 키우기를 껐는데 기록이 남는다")
            check(load_profile(start=td).get("persona", {}).get("affiliation") == "백엔드, 2년 차: 결제",
                  "growth off 가 프로필을 망가뜨렸다")
        finally:
            if old is None:
                os.environ.pop("DOCS_SUIT_PROFILE", None)
            else:
                os.environ["DOCS_SUIT_PROFILE"] = old

    # 슬롯과 폴더 파일
    with tempfile.TemporaryDirectory() as td:
        saved = {k: os.environ.pop(k, None) for k in ("DOCS_SUIT_PROFILE", "DOCS_SUIT_HOME")}
        os.environ["DOCS_SUIT_HOME"] = str(Path(td) / "conf")
        top, sub = Path(td) / "proj", Path(td) / "proj" / "sub"
        sub.mkdir(parents=True)
        try:
            write_profile({"profile": {"class": "office"}, "persona": {"call": "회사"}, "defaults": {"voice": "prose"}}, "work")
            write_profile({"profile": {"class": "student"}}, "default")
            check(profile_source(start=sub)[1] == "default", "폴더 파일이 없는데 기본 슬롯을 쓰지 않는다")
            write_folder({"profile": "work", "defaults": {"register": "haeyo"}, "persona": {"call": "새면 안 된다"}}, top)
            write_folder({"defaults": {"register": "plain"}}, sub)
            _, name, files, why = profile_source(start=sub)
            check(name == "work" and why == "folder" and len(files) == 2, "위쪽 폴더 파일의 슬롯을 따르지 않는다")
            prof = load_profile(start=sub)
            check(prof.get("defaults") == {"voice": "prose", "register": "plain"}, "가까운 폴더 파일의 값이 이기지 않는다")
            check(prof.get("persona") == {"call": "회사"}, "폴더 파일의 페르소나가 섞였다")
            check(profile_source("default", start=sub)[1] == "default", "--profile 이 폴더 파일을 이기지 못한다")
            os.environ["DOCS_SUIT_PROFILE"] = str(Path(td) / "env.yaml")
            check(profile_source("work", start=sub)[3] == "env", "환경 변수가 --profile 을 이기지 못한다")
            os.environ.pop("DOCS_SUIT_PROFILE")
            (Path(td) / "conf" / "current").write_text("work\n", encoding="utf-8")
            check(profile_source(start=td)[1] == "work", "profile use 로 고른 슬롯을 쓰지 않는다")
            try:
                slot_path("../x")
                problems.append("슬롯 이름에 경로를 받았다")
            except Missing:
                pass
            check(status_cwd('{"workspace": {"current_dir": "/a/b"}, "cwd": "/c"}') == "/a/b"
                  and status_cwd('{"cwd": "/c"}') == "/c" and status_cwd("x") is None, "상태 줄 JSON 의 작업 폴더를 읽지 못한다")
            data = read_slot(slot_path("work"))
            state = growth_state(th, [])
            face = status_lines(th, data, "work", state, 24, "face")
            line = status_lines(th, data, "work", state, 24, "line")
            check(len(face) == 7 and "[" in face[2] + face[3] and len(line) == 1 and "Lv.1" in line[0],
                  f"상태 줄 캐릭터가 다르다: {len(face)}줄")
            wide, narrow = widget_frame(th, str(sub), 120, 24), widget_frame(th, str(sub), 30, 24)
            check(len(wide) == 12 and len(narrow) > 12 and narrow[13].startswith("["),
                  "캐릭터 창이 넓은 칸에서 옆으로, 좁은 칸에서 아래로 놓이지 않는다")
            check(display_width("가a\033[1m나\033[0m") == 5, "한글 칸 수를 두 칸으로 세지 않는다")
            out = Path(td) / "mine.yaml"
            ns = argparse.Namespace(action="export", name="mine", by="@someone", label="내 조합", desc="시험", output=str(out),
                                    cls=None, here=False, profile="work")
            quiet(cmd_preset, ns, th)
            mine = parse_yaml(out.read_text(encoding="utf-8")) if out.exists() else {}
            check(mine.get("preset", {}).get("by") == "someone" and mine.get("defaults") == {"voice": "prose"}
                  and "persona" not in mine and "call" not in out.read_text(encoding="utf-8"),
                  f"조합 내보내기가 다르거나 페르소나가 섞였다: {mine}")
            if th.presets:
                name = next(iter(th.presets))
                quiet(cmd_preset, argparse.Namespace(action="use", name=name, cls=None, here=False, profile="work",
                                                    by=None, label=None, desc=None, output=None), th)
                work = read_slot(slot_path("work"))
                check(work.get("defaults") == th.presets[name]["defaults"] and work.get("persona") == {"call": "회사"}
                      and slot_path("work").with_name("work.yaml.bak").exists(),
                      "조합 입히기가 축 값을 바꾸지 못하거나 페르소나를 건드렸거나 .bak 을 남기지 않았다")
        finally:
            for k, v in saved.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v

    # 승급 키. 시험용 작은 키로 서명한다. 이 키는 selftest 안에서만 PROMOTE_KEYS 에 잠깐 넣는다.
    tp = int("a5cacdc975e6a50165ab7aa7524623ee067919475ac06831b64a4dcfff2f88716519", 16)
    tq = int("8f91e9b245d2bc6f599805b725d29f00e8fa6218dc0e0008b7a9d320889cd03b3281", 16)
    tn, td_ = tp * tq, pow(65537, -1, (tp - 1) * (tq - 1))

    def test_key(payload):
        body = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
        k = (tn.bit_length() + 7) // 8
        t = SHA256_INFO + hashlib.sha256(body.encode("ascii")).digest()
        em = int.from_bytes(b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t, "big")
        sig = base64.urlsafe_b64encode(pow(em, td_, tn).to_bytes(k, "big")).rstrip(b"=").decode()
        return f"dsk1.{body}.{sig}"

    key3 = test_key({"v": 1, "kid": "selftest", "who": "someone", "tier": 3, "ref": "PR #1"})
    check((read_promote_key(key3, {"selftest": (tn, 65537)}) or {}).get("tier") == 3, "승급 키 서명을 확인하지 못한다")
    check(read_promote_key(key3) is None, "실제 공개 키가 시험 키를 받았다")
    body = key3.split(".")[1]
    forged = key3.replace(body, base64.urlsafe_b64encode(json.dumps(
        {"v": 1, "kid": "selftest", "who": "someone", "tier": 4, "ref": "PR #1"}).encode()).rstrip(b"=").decode())
    check(read_promote_key(forged, {"selftest": (tn, 65537)}) is None, "내용을 바꾼 승급 키를 받았다")
    check(key_tiers([{"tier": 4}]) == {1, 2, 3, 4}, "4차 키가 3차 조건을 채우지 않는다")
    with tempfile.TemporaryDirectory() as td:
        saved = {k: os.environ.pop(k, None) for k in ("DOCS_SUIT_PROFILE", "DOCS_SUIT_HOME")}
        os.environ["DOCS_SUIT_HOME"] = td
        PROMOTE_KEYS["selftest"] = (tn, 65537)
        try:
            write_profile({"profile": {"class": "office"}}, "default")
            check(quiet(cmd_promote, argparse.Namespace(key="dsk1.x.y", profile=None), th) == 1, "틀린 승급 키를 받았다")
            quiet(cmd_promote, argparse.Namespace(key=key3, profile=None), th)
            quiet(cmd_promote, argparse.Namespace(key=key3, profile=None), th)
            check([k["tier"] for k in promote_keys()] == [3], "승급 키를 한 번만 남기지 않는다")
            many = [{"doc": str(i), "at": datetime.fromordinal(738000 + i).isoformat(), "kind": None, "checks": {},
                     "unresolved": 0} for i in range(400)]
            check(growth_state(th, many)["tier"] == 2 and growth_state(th, many, key_tiers(promote_keys()))["tier"] == 3,
                  "승급 키 없이 3차에 오르거나, 키가 있는데 오르지 못한다")
        finally:
            PROMOTE_KEYS.pop("selftest", None)
            for k, v in saved.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v

    web = HERE / "docs" / "themes.json"
    if (HERE / "docs").is_dir() and th.root.resolve() == (HERE / "themes" / DEFAULT_LANG).resolve():
        check(web.exists() and web.read_text(encoding="utf-8") == bundle_text(th),
              "docs/themes.json 이 테마와 다르다. python3 suit.py bundle 을 돌린다")

    for p in problems:
        print(f"✗ {p}")
    print("selftest 통과" if not problems else f"selftest 실패 {len(problems)}건")
    return 0 if not problems else 1


def main(argv=None):
    log = os.environ.get("DOCS_SUIT_LOG")  # 동작 테스트가 에이전트의 호출 인자를 모은다. tests/agent/run.py
    if log:
        try:
            with open(log, "a", encoding="utf-8") as f:
                f.write(json.dumps({"argv": sys.argv[1:] if argv is None else argv}, ensure_ascii=False) + "\n")
        except OSError:
            pass
    ap = argparse.ArgumentParser(prog="suit.py", description="docs-suit: 문서에 옷을 입히는 AI 글쓰기 테마 엔진")
    sub = ap.add_subparsers(dest="cmd", required=True)
    slot = argparse.ArgumentParser(add_help=False)
    slot.add_argument("--profile", metavar="슬롯", help="이 슬롯의 프로필을 쓴다. 폴더 파일과 profile use 보다 앞선다")
    b = sub.add_parser("bootstrap", parents=[slot])
    b.add_argument("--class", dest="cls")
    for k in PERSONA_IN_PROMPT:
        b.add_argument(f"--{k}")
    b.add_argument("--docs", help="자주 쓰는 문서 종류. 쉼표로 잇는다")
    b.add_argument("--agents", help="스킬을 설치할 도구. 쉼표로 잇는다")
    b.add_argument("--look", help="캐릭터 a 나 b. 주지 않으면 a")
    b.add_argument("--preset", help="이 테마 조합으로 시작한다. suit.py preset list 로 본다")
    b.add_argument("--yes", action="store_true", help="묻지 않고 진행한다")
    b.add_argument("--force", action="store_true", help="있는 프로필을 .bak 으로 남기고 새로 만든다")
    b.add_argument("--questions", action="store_true", help="클래스와 페르소나 질문 목록을 JSON 으로 낸다")
    pr = sub.add_parser("profile", parents=[slot])
    pr.add_argument("action", nargs="?", choices=("show", "list", "use"), default="show")
    pr.add_argument("name", nargs="?", help="profile use 로 고를 슬롯 이름")
    pr.add_argument("--here", action="store_true", help="지금 폴더의 .docs-suit.yaml 에 슬롯을 적는다")
    li = sub.add_parser("list")
    li.add_argument("--classes", action="store_true")
    li.add_argument("--json", action="store_true")
    for name in ("get", "compose"):
        p = sub.add_parser(name, parents=[slot])
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
    s = sub.add_parser("set", parents=[slot])
    s.add_argument("axis")
    s.add_argument("value", nargs="?")
    s.add_argument("--unset", action="store_true")
    s.add_argument("--audience")
    s.add_argument("--here", action="store_true", help="슬롯 대신 지금 폴더의 .docs-suit.yaml 에 쓴다")
    e = sub.add_parser("export", parents=[slot])
    e.add_argument("--agent", required=True, help="claude, agents, codex, antigravity, cursor, grok, web, all")
    e.add_argument("--dest", help="에이전트별 하위 폴더로 이 폴더 아래에 쓴다. 시험용")
    e.add_argument("--dry-run", action="store_true")
    c = sub.add_parser("check", parents=[slot])
    c.add_argument("file", help="검사할 본문 파일. - 이면 표준 입력에서 읽는다")
    c.add_argument("--class", dest="cls")
    c.add_argument("--kind")
    c.add_argument("--audience")
    c.add_argument("--set", action="append", metavar="축=값")
    c.add_argument("--chars", type=int)
    c.add_argument("--no-record", action="store_true", help="재기만 하고 성장 기록에 남기지 않는다")
    c.add_argument("--json", action="store_true")
    ca = sub.add_parser("card", parents=[slot])
    ca.add_argument("--json", action="store_true")
    ca.add_argument("--color", choices=("auto", "always", "never"), default="auto",
                    help="auto 는 터미널일 때만 도트 그림을 그린다")
    lo = sub.add_parser("look", parents=[slot])
    lo.add_argument("part", nargs="?", help="base, color, hair, prop, top")
    lo.add_argument("value", nargs="?", help="고를 값. prop 과 color 는 none 으로 지운다")
    lo.add_argument("--json", action="store_true")
    ps = sub.add_parser("preset", parents=[slot])
    ps.add_argument("action", choices=("list", "show", "use", "export"))
    ps.add_argument("name", nargs="?")
    ps.add_argument("--class", dest="cls", help="list 에서 이 클래스의 조합을 앞에 둔다")
    ps.add_argument("--here", action="store_true", help="use 를 지금 폴더의 .docs-suit.yaml 에 쓴다")
    ps.add_argument("--by", help="export 에 남길 GitHub 아이디")
    ps.add_argument("--label", help="export 에 남길 조합 이름")
    ps.add_argument("--desc", help="export 에 남길 한 줄 소개")
    ps.add_argument("-o", "--output", help="export 로 쓸 파일. 주지 않으면 <이름>.yaml")
    pm = sub.add_parser("promote", parents=[slot])
    pm.add_argument("key", nargs="?", help="기여하고 받은 승급 키. 주지 않으면 받은 키를 보인다")
    g = sub.add_parser("growth", parents=[slot])
    g.add_argument("action", choices=("on", "off"))
    wd = sub.add_parser("widget")
    wd.add_argument("--cwd", help="이 폴더의 슬롯을 그린다. 주지 않으면 지금 폴더")
    wd.add_argument("--split", action="store_true", help="herdr 나 tmux 의 지금 칸 오른쪽에 칸을 나눠 띄운다")
    wd.add_argument("--width", type=int, default=44, help="tmux 로 나눌 칸의 너비")
    wd.add_argument("--once", action="store_true", help="한 번만 그리고 끝낸다")
    st = sub.add_parser("status", parents=[slot])
    st.add_argument("--size", choices=("face", "full", "line"), default="face", help="face 는 얼굴, full 은 온몸, line 은 한 줄")
    st.add_argument("--cwd", help="이 폴더 기준으로 슬롯을 고른다. 주지 않으면 표준 입력의 JSON 이나 지금 폴더")
    sub.add_parser("bundle")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    try:
        th = Themes(themes_root())
        if a.cmd == "selftest":
            return selftest(th)
        return {"bootstrap": cmd_bootstrap, "profile": cmd_profile, "list": cmd_list, "get": cmd_get,
                "compose": cmd_compose, "set": cmd_set, "export": cmd_export, "check": cmd_check, "card": cmd_card,
                "look": cmd_look, "preset": cmd_preset, "promote": cmd_promote, "growth": cmd_growth, "status": cmd_status, "widget": cmd_widget,
                "bundle": cmd_bundle}[a.cmd](a, th)
    except Missing as e:
        print(f"오류: {e}", file=sys.stderr)
        return 3
    except (OSError, ValueError) as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
