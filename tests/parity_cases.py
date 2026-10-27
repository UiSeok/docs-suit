"""웹 조립(core.js)과 비교할 조립 결과를 suit.py 로 만들어 JSON 으로 낸다. tests/parity.js 가 부른다."""
import importlib.util
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("suit", ROOT / "suit.py")
suit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(suit)
th = suit.Themes(ROOT / "themes" / suit.DEFAULT_LANG)

profiles = [
    {},
    {"persona": {"call": "민수 님", "affiliation": "백엔드, 2년 차", "facts": "지도 시각화를 좋아한다", "docs": ["pr"]},
     "defaults": {"register": "haeyo", "exposure": "team"}, "audiences": {"professor": {"skeleton": "pcs"}}},
]
extras = [
    {"sets": {}, "chars": None, "fmt": "prompt", "html": False},
    {"sets": {"register": "polite", "exposure": "submit", "visual-deck": "contrast"}, "chars": 800,
     "fmt": "output-style", "html": True},
]
aud_ids = list(th.audiences)
cases = []
for i, (cls, kind) in enumerate(itertools.product([None] + list(th.classes), [None] + list(th.kinds))):
    for prof, ex in itertools.product(profiles, extras):
        auds = [] if (i + len(cases)) % 3 else [aud_ids[i % len(aud_ids)]]
        text, _ = suit.compose(th, kind, auds or None, ex["sets"], prof, cls, ex["chars"], ex["fmt"], ex["html"])
        cases.append({"cls": cls, "kind": kind, "auds": auds, "profile": prof, **ex, "expected": text})
# 웹 캐릭터 만들기가 내려받게 하는 슬롯 파일. suit.py 가 읽는 꼴과 같아야 한다.
slots = [
    {"profile": {"class": "office", "lang": "ko", "agents": ["claude", "codex"]},
     "persona": {"call": '민수 "님"', "affiliation": "백엔드, 2년 차: 결제", "goal": " 앞뒤 공백 ", "facts": "#1 은 [지도]",
                 "docs": ["work-report", "email"]},
     "look": {"base": "b"}, "defaults": {"register": "polite", "length": "brief"},
     "audiences": {"manager": {"register": "haeyo"}}},
    {"profile": {"class": "student", "lang": "ko"}, "persona": {}, "defaults": {}},
]
slot_cases = [{"data": d, "expected": suit.dump_yaml(d)} for d in slots]
# 웹이 그리는 캐릭터. 기본 몸에 옷, 머리, 소품을 겹치고, 차수로 잠긴 부위는 기본값으로 둔다.
looks = [({}, None), ({"look": {"base": "b"}}, 0), ({"look": {"base": "a", "color": "wine", "hair": "bangs"}}, 1),
         ({"look": {"base": "b", "top": "suit", "prop": "tie", "color": "navy", "hair": "short"}}, 4),
         ({"look": {"base": "b", "top": "coat", "prop": "glasses"}}, 2), ({"look": {"top": "nope"}}, 4)]
look_cases = [{"slot": slot, "tier": tier, "look": suit.look_of(th, slot, tier),
               "expected": suit.look_grid(th, suit.look_of(th, slot, tier))} for slot, tier in looks]
json.dump({"compose": cases, "slots": slot_cases, "looks": look_cases}, sys.stdout, ensure_ascii=False)
