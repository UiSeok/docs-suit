// 웹 고르개(core.js)와 theme.py 가 같은 지침을 조립하는지 견준다. 실행: node tests/parity.js
const { execFileSync } = require("child_process");
const path = require("path");
const root = path.join(__dirname, "..");
const T = require(path.join(root, "docs", "themes.json"));
const C = require(path.join(root, "docs", "core.js"))(T);

const env = { ...process.env, GEULOT_PERSONAL: path.join(__dirname, "no-such-personal.yaml") };
const kinds = [null, ...Object.keys(T.kinds)];
const auds = [null, ...Object.keys(T.audiences)];
const extras = [
  { sets: {}, chars: null, fmt: "prompt", html: false },
  { sets: { register: "haeyo", exposure: "team" }, chars: 1000, fmt: "output-style", html: true },
  { sets: { skeleton: "chrono", "visual-deck": "contrast" }, chars: null, fmt: "prompt", html: false },
];
let n = 0, bad = 0;
for (const kind of kinds) for (const aud of auds) for (const ex of extras) {
  const args = ["theme.py", "compose", "--format", ex.fmt];
  if (kind) args.push("--kind", kind);
  if (aud) args.push("--audience", aud);
  for (const [k, v] of Object.entries(ex.sets)) args.push("--set", `${k}=${v}`);
  if (ex.chars) args.push("--chars", String(ex.chars));
  if (ex.html) args.push("--html");
  const py = execFileSync("python3", args, { cwd: root, env, stdio: ["ignore", "pipe", "ignore"] }).toString();
  const r = C.resolve(kind, aud ? [aud] : [], ex.sets, {});
  const js = C.compose(kind, r.auds, r.vals, ex.chars, ex.fmt, ex.html);
  n++;
  if (py !== js) { bad++; console.log(`다름: kind=${kind} audience=${aud} ${JSON.stringify(ex)}`); }
}
console.log(bad ? `parity 실패 ${bad}/${n}` : `parity 통과 ${n}건`);
process.exit(bad ? 1 : 0);
