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
json.dump(cases, sys.stdout, ensure_ascii=False)
