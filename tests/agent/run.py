#!/usr/bin/env python3
"""동작 테스트. 실제 에이전트에 요청을 넣고, 에이전트가 suit.py 를 어떤 인자로 불렀는지 모아 채점한다.

에이전트마다 로그인이 필요하고 돌릴 때마다 사용료가 들어서 CI 에는 넣지 않는다.
  python3 tests/agent/run.py --agent claude                 # 케이스 전체
  python3 tests/agent/run.py --agent antigravity --only sns,pr --model gemini-3.8-flash-high
  python3 tests/agent/run.py --agent claude --record        # tests/agent/results/claude.md 에 남긴다
홈 폴더의 스킬과 프로필은 건드리지 않는다. 케이스마다 임시 폴더에 프로젝트 단위 스킬과 시험 프로필을 두고,
DOCS_SUIT_LOG 로 suit.py 호출 인자를 모은다. Claude Code 는 사용자 설정과 개인 스킬을 끄고 돌린다.
"""
import argparse
import base64
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SUIT = ROOT / "suit.py"
spec = importlib.util.spec_from_file_location("suit", SUIT)
suit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(suit)
sys.path.insert(0, str(HERE))
from cases import CASES, PROFILE  # noqa: E402

th = suit.Themes(ROOT / "themes" / suit.DEFAULT_LANG)
RUN = f"python3 {SUIT}"


def claude_cmd(ask, tmp, model):
    # 사용자 설정과 개인 스킬, 전역 CLAUDE.md, MCP 를 끄고 처음 설치한 사람과 같은 조건으로 돌린다.
    return ["claude", "-p", ask, "--output-format", "stream-json", "--verbose",
            "--setting-sources", "project,local", "--strict-mcp-config",
            "--settings", '{"disableAllHooks": true}',
            "--allowedTools", f"Bash({RUN}:*)", "Bash(date:*)", "Read", "Skill",
            "--disallowedTools", "Write", "Edit"] + (["--model", model] if model else [])


def claude_meta(out):
    meta = {"skills": [], "denied": 0, "cost": 0.0, "model": ""}
    for line in out.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("type") == "system" and o.get("subtype") == "init":
            meta["model"] = o.get("model", "")
        elif o.get("type") == "assistant":
            for b in o["message"].get("content", []):
                if b.get("type") == "tool_use" and b.get("name") == "Skill":
                    meta["skills"].append(b["input"].get("skill", ""))
        elif o.get("type") == "result":
            meta["denied"] = len(o.get("permission_denials", []))
            meta["cost"] = o.get("total_cost_usd", 0.0)
            meta["sec"] = round(o.get("duration_ms", 0) / 1000)
            meta["reply"] = o.get("result", "")
    return meta


def antigravity_cmd(ask, tmp, model):
    # 한 번 실행 모드는 확인 창을 띄우지 못해 명령을 거절한다. 작업 폴더 단위 설정이 없으므로
    # ~/.gemini/antigravity-cli/settings.json 의 permissions.allow 에 command(python3 <suit.py 절대 경로>) 가 있어야 한다.
    return ["agy", "-p", ask, "--output-format", "stream-json", "--print-timeout", "900s"] + \
        (["--model", model] if model else [])


def antigravity_meta(out):
    meta = {"skills": [], "denied": 0, "cost": 0.0, "model": "", "reply": ""}
    for line in out.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("event") == "step_update":
            s = o["step_update"]
            path = ((s.get("tool_info") or {}).get("parameters") or {}).get("Path", "")
            if s.get("tool_name") == "read_file" and path.endswith("/SKILL.md"):
                meta["skills"].append(Path(path).parent.name)
        elif o.get("event") == "result":
            r = o["result"]
            meta["denied"] = len(r.get("denied_actions") or [])
            meta["sec"] = round(r.get("duration_seconds", 0))
            meta["reply"] = r.get("response", "")
    return meta


def codex_cmd(ask, tmp, model):
    # exec 모드는 확인을 묻지 않고 샌드박스 안에서 돌린다. suit.py 가 호출 기록을 쓰도록 임시 폴더를 쓰기 자리에 더하고,
    # 사용자 config.toml 은 읽지 않는다.
    return ["codex", "exec", ask, "--json", "--sandbox", "workspace-write", "--add-dir", str(tmp),
            "--skip-git-repo-check", "--ignore-user-config", "--ephemeral"] + (["--model", model] if model else [])


def codex_meta(out):
    meta = {"skills": [], "denied": 0, "cost": 0.0, "model": "", "reply": ""}
    for line in out.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        item = o.get("item") or {}
        if o.get("type") != "item.completed":
            continue
        if item.get("type") == "agent_message":
            meta["reply"] = item.get("text", "")
        elif item.get("type") == "command_execution":
            for part in item.get("command", "").split():
                if part.endswith("/SKILL.md"):
                    meta["skills"].append(Path(part.strip("'\"")).parent.name)
    return meta


def codex_plan():
    """로그인한 ChatGPT 요금제. 토큰은 읽기만 하고 요금제 이름 말고는 꺼내지 않는다."""
    try:
        auth = json.loads((Path.home() / ".codex" / "auth.json").read_text(encoding="utf-8"))
        payload = auth["tokens"]["id_token"].split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        return claims["https://api.openai.com/auth"]["chatgpt_plan_type"]
    except (OSError, KeyError, IndexError, ValueError):
        return ""


AGENTS = {
    "claude": {"skill": ".claude/skills/docs-suit/SKILL.md", "cmd": claude_cmd, "meta": claude_meta,
               "version": ["claude", "--version"]},
    "antigravity": {"skill": ".agents/skills/docs-suit/SKILL.md", "cmd": antigravity_cmd, "meta": antigravity_meta,
                    "version": ["agy", "--version"],
                    "note": "한 번 실행 모드는 허용 규칙 밖의 명령을 만나면 답 없이 끝난다. 이 표는 종류와 축을 고르는 단계까지 잰다."},
    "codex": {"skill": ".agents/skills/docs-suit/SKILL.md", "cmd": codex_cmd, "meta": codex_meta,
              "version": ["codex", "--version"], "plan": codex_plan},
}


def compose_args(argv):
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--kind")
    p.add_argument("--audience")
    p.add_argument("--set", action="append")
    p.add_argument("--chars", type=int)
    p.add_argument("--class", dest="cls")
    a, _ = p.parse_known_args(argv[1:])
    return a


def describe(argv):
    return " ".join(x for x in argv if not x.startswith("/"))


def grade(case, calls):
    """(맞았나, 에이전트가 부른 것, 어긋난 까닭) 을 돌려준다."""
    expect = case.get("expect", "compose")
    composes = [c for c in calls if c[:1] == ["compose"] and not {"--help", "-h"} & set(c)]
    shown = "; ".join(describe(c) for c in composes) or ", ".join(sorted({c[0] for c in calls if c})) or "부르지 않음"
    if expect == "skip":
        return not calls, shown, "" if not calls else "문서 요청이 아닌데 suit.py 를 불렀다"
    if any(c[:1] == ["bootstrap"] and "--yes" in c for c in calls):
        return False, shown, "사용자의 답 없이 프로필을 저장했다"
    if not composes:
        return False, shown, "compose 를 부르지 않았다"
    a = compose_args(composes[-1])
    why = []
    kinds = case["kind"] if isinstance(case["kind"], list) else [case["kind"]]
    if (a.kind or "") not in kinds:
        why.append(f"종류가 {a.kind or '없음'} 이다")
    try:
        sets = suit._sets(a.set)
        prof = PROFILE if case.get("profile", True) else {}
        vals, auds, _ = suit.resolve(th, a.kind or None, suit._auds(a.audience), sets, prof, a.cls)
    except suit.Missing as e:
        return False, shown, f"엔진이 거절했다: {e}"
    if case.get("audience") and case["audience"] not in auds:
        why.append(f"독자가 {','.join(auds) or '없음'} 이다")
    for axis, v in case.get("want", {}).items():
        if vals[axis][0] != v:
            why.append(f"{axis} 가 {vals[axis][0]} 이다")
    if case.get("chars") and a.chars != case["chars"]:
        why.append(f"글자수가 {a.chars} 이다")
    return not why, shown, ", ".join(why)


LIMIT_SIGNS = ("quota", "RESOURCE_EXHAUSTED", "usage limit", "rate limit")


def load_case(agent, case, base):
    """지난 실행의 기록으로 다시 채점한다. 기대값만 고쳤을 때 에이전트를 다시 부르지 않는다."""
    tmp = base / case["id"]
    log = tmp / "calls.jsonl"
    calls = [json.loads(x)["argv"] for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    ok, shown, why = grade(case, calls)
    meta = AGENTS[agent]["meta"]((tmp / "transcript.jsonl").read_text(encoding="utf-8"))
    meta.setdefault("sec", 0)
    err = (tmp / "stderr.txt").read_text(encoding="utf-8") if (tmp / "stderr.txt").exists() else ""
    # 무료 요금제는 사용 한도에 걸리면 답 없이 끝난다. 그런 건은 틀림이 아니라 재지 못한 것으로 센다.
    meta["limited"] = not ok and any(k in err for k in LIMIT_SIGNS)
    return case, ok, shown, why, meta


def run_case(agent, case, base, model):
    tmp = base / case["id"]
    proj = tmp / "proj"
    skill = proj / AGENTS[agent]["skill"]
    skill.parent.mkdir(parents=True)
    skill.write_text(suit.skill_text(th), encoding="utf-8")
    prof = tmp / "profile.yaml"
    if case.get("profile", True):
        prof.write_text(suit.dump_yaml(PROFILE), encoding="utf-8")
    log = tmp / "calls.jsonl"
    env = dict(os.environ, DOCS_SUIT_PROFILE=str(prof), DOCS_SUIT_LOG=str(log))
    t0 = time.time()
    try:
        p = subprocess.run(AGENTS[agent]["cmd"](case["ask"], tmp, model), cwd=proj, env=env, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=900)
        out, err = p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        out, err = e.stdout or "", "시간 초과"
        out = out.decode() if isinstance(out, bytes) else out
    (tmp / "transcript.jsonl").write_text(out, encoding="utf-8")
    (tmp / "stderr.txt").write_text(err or "", encoding="utf-8")
    case, ok, shown, why, meta = load_case(agent, case, base)
    meta["sec"] = round(time.time() - t0)
    return case, ok, shown, why, meta


def expected(case):
    expect = case.get("expect", "compose")
    if expect == "skip":
        return "부르지 않음"
    kinds = case["kind"] if isinstance(case["kind"], list) else [case["kind"]]
    parts = [" 또는 ".join(k or "종류 없음" for k in kinds)]
    if case.get("audience"):
        parts.append(f"독자 {case['audience']}")
    parts += [f"{k}={v}" for k, v in case.get("want", {}).items()]
    if case.get("chars"):
        parts.append(f"{case['chars']}자")
    return ", ".join(parts)


def report(agent, results, version, model=None):
    models = sorted({m["model"] for *_, m in results if m["model"]}) or ([model] if model else [])
    passed = sum(1 for _, ok, *_ in results if ok)
    limited = sum(1 for *_, m in results if m["limited"])
    cost = sum(m["cost"] for *_, m in results)
    lines = [f"# 동작 테스트: {agent}", "",
             f"- 날짜: {date.today().isoformat()}",
             f"- 에이전트: {version}",
             f"- 모델: {', '.join(models) or '알 수 없음'}",
             *([f"- 요금제: {AGENTS[agent]['plan']() or '알 수 없음'}"] if AGENTS[agent].get("plan") else []),
             f"- 맞음: {passed}/{len(results) - limited}" + (f" (사용 한도로 재지 못한 {limited}건 제외)" if limited else ""),
             f"- 사용료: {cost:.2f}달러" if cost else "- 사용료: 에이전트가 알려 주지 않음",
             *([f"- 한계: {AGENTS[agent]['note']}"] if AGENTS[agent].get("note") else []),
             "", "| 케이스 | 기대 | 에이전트가 부른 것 | 판정 | 비고 | 초 |", "|---|---|---|---|---|---|"]
    for case, ok, shown, why, m in results:
        others = sorted({s for s in m["skills"] if s and s != "docs-suit"})
        note = ", ".join(([f"같이 불린 스킬 {', '.join(others)}"] if others else [])
                         + ([f"거절된 도구 {m['denied']}건"] if m["denied"] else []))
        verdict = "맞음" if ok else "재지 못함: 사용 한도" if m["limited"] else f"틀림: {why}"
        lines.append(f"| {case['id']} | {expected(case)} | `{shown}` | {verdict} | {note} | {m['sec']} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="docs-suit 동작 테스트")
    ap.add_argument("--agent", required=True, choices=list(AGENTS))
    ap.add_argument("--only", help="케이스 id 를 쉼표로 잇는다")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--model", help="에이전트에 넘길 모델. 주지 않으면 에이전트 기본값")
    ap.add_argument("--record", action="store_true", help="tests/agent/results/<agent>.md 에 남긴다")
    ap.add_argument("--regrade", metavar="기록 폴더", help="에이전트를 부르지 않고 지난 실행의 기록으로 다시 채점한다")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    cases = [c for c in CASES if not only or c["id"] in only]
    if a.record and only:
        ap.error("--record 는 케이스 전체를 돌릴 때만 쓴다")
    version = subprocess.run(AGENTS[a.agent]["version"], capture_output=True, text=True).stdout.strip()
    if a.regrade:
        base = Path(a.regrade)
        results = [load_case(a.agent, c, base) for c in cases]
    else:
        base = Path(tempfile.mkdtemp(prefix=f"docs-suit-agent-{a.agent}-"))
        print(f"{a.agent} {version}, 케이스 {len(cases)}건, 기록은 {base}", file=sys.stderr)
        with ThreadPoolExecutor(a.jobs) as ex:
            results = list(ex.map(lambda c: run_case(a.agent, c, base, a.model), cases))
    for case, ok, shown, why, m in results:
        print(f"{'맞음' if ok else '틀림'} {case['id']}: {shown}" + (f" ({why})" if why else ""), file=sys.stderr)
    text = report(a.agent, results, version, a.model)
    print(text)
    if a.record:
        out = HERE / "results" / f"{a.agent}.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text(text, encoding="utf-8")
    return 0 if all(ok or m["limited"] for _, ok, *_, m in results) else 1


if __name__ == "__main__":
    sys.exit(main())
