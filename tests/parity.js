// 웹 고르개(core.js)와 suit.py 가 같은 지침을 조립하는지 견준다. 실행: node tests/parity.js
const { execFileSync } = require("child_process");
const path = require("path");
const root = path.join(__dirname, "..");
const T = require(path.join(root, "docs", "themes.json"));
const C = require(path.join(root, "docs", "core.js"))(T);

const cases = JSON.parse(execFileSync("python3", [path.join(__dirname, "parity_cases.py")], { maxBuffer: 1 << 28 }).toString());
let bad = 0;
for (const c of cases) {
  const r = C.resolve(c.kind, c.auds, c.sets, c.profile, c.cls);
  const js = C.compose(c.kind, r.auds, r.vals, c.chars, c.fmt, c.html, r.cls, (c.profile || {}).persona);
  if (js !== c.expected) {
    bad++;
    if (bad <= 3) console.log(`다름: class=${c.cls} kind=${c.kind} audience=${c.auds} fmt=${c.fmt}`);
  }
}
console.log(bad ? `parity 실패 ${bad}/${cases.length}` : `parity 통과 ${cases.length}건`);
process.exit(bad ? 1 : 0);
