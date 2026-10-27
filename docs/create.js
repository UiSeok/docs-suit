// 캐릭터 만들기 화면. suit.py bootstrap 이 묻는 것을 웹으로 옮겼다.
// 슬롯 파일의 꼴과 캐릭터 그림은 core.js 가 엔진과 같은 규칙으로 만들고, tests/parity.js 가 견준다.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const AGENTS = [["claude", "Claude Code"], ["codex", "Codex CLI"], ["antigravity", "Antigravity CLI"],
    ["cursor", "Cursor"], ["grok", "Grok Build"], ["web", "웹 채팅"]];
  const SLOT_RE = /^[\p{L}\p{N}_-]+$/u;  // suit.py 의 슬롯 이름 규칙과 같다
  const state = { cls: null, preset: null, base: null, persona: {}, docs: [], agents: [] };
  let T = null, C = null;

  function esc(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

  function draw(canvas, grid, scale) {
    canvas.width = grid[0].length * scale;
    canvas.height = grid.length * scale;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    grid.forEach((row, y) => row.forEach((c, x) => {
      if (!c) return;
      ctx.fillStyle = c;
      ctx.fillRect(x * scale, y * scale, scale, scale);
    }));
  }

  function opt(box, pressed, html, onClick, extra) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "opt" + (extra ? " " + extra : "");
    b.setAttribute("aria-pressed", String(pressed));
    b.innerHTML = html;
    b.addEventListener("click", onClick);
    box.appendChild(b);
    return b;
  }

  function chip(box, label, pressed, onClick) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.textContent = label;
    b.setAttribute("aria-pressed", String(pressed));
    b.addEventListener("click", onClick);
    box.appendChild(b);
  }

  // suit.py preset_order 와 같다. 추천 표시가 있는 조합, 고른 클래스의 조합 순으로 앞에 둔다.
  function presetOrder() {
    return Object.keys(T.presets).sort((a, b) => {
      const key = (k) => [String(T.presets[k].featured) !== "true" ? 1 : 0, state.cls && T.presets[k].class !== state.cls ? 1 : 0, k];
      const [x, y] = [key(a), key(b)];
      return x[0] - y[0] || x[1] - y[1] || (x[2] < y[2] ? -1 : 1);
    });
  }

  function unlockLabels(tier) {
    return Object.values(T.look.unlock || {}).filter((u) => parseInt(u.at, 10) === tier).map((u) => u.label);
  }

  // suit.py bootstrap 이 쓰는 슬롯과 같은 꼴
  function slotData() {
    const data = { profile: { class: state.cls, lang: "ko" } };
    if (state.agents.length) data.profile.agents = state.agents.slice();
    const persona = {};
    for (const key of T.personaInPrompt) {
      if ((state.persona[key] || "").trim()) persona[key] = C.cleanText(state.persona[key]);
    }
    if (state.docs.length) persona.docs = state.docs.slice();
    data.persona = persona;
    if (state.base) data.look = { base: state.base };
    const p = state.preset && T.presets[state.preset];
    if (p) {
      data.defaults = Object.assign({}, p.defaults || {});
      data.audiences = {};
      for (const [k, v] of Object.entries(p.audiences || {})) data.audiences[k] = Object.assign({}, v);
    }
    return data;
  }

  // ---------------------------------------------------------------- 왼쪽 단계
  function renderClasses() {
    const box = $("classes");
    box.textContent = "";
    for (const [key, c] of Object.entries(T.classes)) {
      const kinds = c.kinds.map((k) => T.kinds[k].label).join(", ");
      opt(box, state.cls === key,
        `<b>${esc(c.label)}</b><span class="d">${esc(c.desc)}</span><span class="d">주력 문서 ${esc(kinds)}</span>` +
        `<span class="ladder">${esc((c.titles || []).join(" → "))}</span>`,
        () => { state.cls = key; if (state.preset && !T.presets[state.preset]) state.preset = null; render(); });
    }
  }

  function renderPresets() {
    const box = $("presets");
    box.textContent = "";
    opt(box, state.preset === null, `<b>클래스 기본값으로 시작</b><span class="d">고른 클래스의 기본 말투를 그대로 씁니다</span>`,
      () => { state.preset = null; render(); });
    for (const key of presetOrder()) {
      const p = T.presets[key];
      const values = Object.entries(p.defaults || {}).map(([ax, v]) => C.label(ax, v)).join(" · ");
      const cls = T.classes[p.class] ? T.classes[p.class].label : "";
      const mark = String(p.featured) === "true" ? " · 추천" : "";
      opt(box, state.preset === key,
        `<b>${esc(p.label || key)}</b><span class="d">${esc(p.desc || "")}</span>` +
        `<span class="d">${esc(values)}</span><span class="ladder">${esc(cls)} · @${esc(p.by || "")}${mark}</span>`,
        () => { state.preset = key; render(); });
    }
  }

  function renderBases() {
    const box = $("bases");
    box.textContent = "";
    for (const [key, b] of Object.entries(T.look.base || {})) {
      const btn = opt(box, (state.base || "a") === key, `<canvas class="portrait"></canvas><b>${esc(b.label)}</b>`,
        () => { state.base = key; render(); }, "base");
      draw(btn.querySelector("canvas"), C.lookGrid(C.lookOf({ look: { base: key } }, 0)), 5);
    }
  }

  function renderPersona() {
    const box = $("persona");
    box.textContent = "";
    for (const [key, q] of Object.entries(T.persona)) {
      const label = document.createElement("label");
      label.textContent = q.ask || q.label;
      if (key === "docs") {
        const chips = document.createElement("div");
        chips.className = "chips";
        const main = state.cls ? T.classes[state.cls].kinds : [];
        const order = main.concat(Object.keys(T.kinds).filter((k) => main.indexOf(k) < 0));
        for (const k of order) {
          chip(chips, T.kinds[k].label + (main.indexOf(k) >= 0 ? " ★" : ""), state.docs.indexOf(k) >= 0, () => {
            const i = state.docs.indexOf(k);
            if (i >= 0) state.docs.splice(i, 1); else state.docs.push(k);
            renderPersona();
            renderAside();
          });
        }
        label.innerHTML = `${esc(q.ask || q.label).replace(/ 번호를.*$/, "")} <span class="hint">★ 는 클래스의 주력 문서</span>`;
        label.appendChild(chips);
      } else {
        const input = document.createElement(key === "facts" ? "textarea" : "input");
        if (key !== "facts") input.type = "text";
        input.value = state.persona[key] || "";
        input.placeholder = (q.hint || "").replace(/^예\) /, "");
        input.addEventListener("input", () => { state.persona[key] = input.value; renderAside(); });
        label.appendChild(input);
      }
      box.appendChild(label);
    }
  }

  function renderAgents() {
    const box = $("agents");
    box.textContent = "";
    for (const [key, label] of AGENTS) {
      chip(box, label, state.agents.indexOf(key) >= 0, () => {
        const i = state.agents.indexOf(key);
        if (i >= 0) state.agents.splice(i, 1); else state.agents.push(key);
        renderAgents();
        renderAside();
      });
    }
  }

  // ---------------------------------------------------------------- 오른쪽 결과
  function renderAside() {
    const cls = state.cls;
    const grid = C.lookGrid(C.lookOf({ look: { base: state.base || "a" } }, 0));
    draw($("portrait"), grid, 8);
    const name = C.cleanText(state.persona.call || "") || "이름 없음";
    const title = cls ? C.titleOf(cls, 0) : null;
    const need = C.levelCost(1);
    const who = $("who");
    who.textContent = "";
    const t = document.createElement("div");
    t.className = "t";
    t.textContent = (title ? `[${title}] ` : "") + name;
    const s1 = document.createElement("div");
    s1.className = "s";
    s1.textContent = cls ? T.classes[cls].label : "클래스를 고르세요";
    const s2 = document.createElement("div");
    s2.className = "s";
    s2.innerHTML = `Lv.1 <span class="lvbar" role="img" aria-label="경험치 0/${need}"><i style="width:0%"></i></span> 0/${need}`;
    who.append(t, s1, s2);

    const ladder = $("ladder");
    ladder.textContent = "";
    for (const p of T.promote) {
      const li = document.createElement("li");
      const nt = cls ? C.titleOf(cls, p.tier) : `${p.tier}차`;
      li.innerHTML = `Lv.${p.level} <b>[${esc(nt)}]</b> · ${esc(unlockLabels(p.tier).join(", "))} 열림` +
        (p.key ? (p.tier === 4 ? " · 테마 조합 기여" : " · 저장소 기여") : "");
      ladder.appendChild(li);
    }

    const slot = $("slot").value.trim();
    const slotOk = !slot || SLOT_RE.test(slot);
    const file = slot ? `${slot}.yaml` : "profile.yaml";
    const dest = slot ? `~/.config/docs-suit/profiles/${file}` : `~/.config/docs-suit/${file}`;
    const ready = !!cls && slotOk;
    $("yaml").value = cls ? C.dumpYaml(slotData()) : "클래스를 고르면 슬롯 파일이 여기에 나옵니다.";
    $("download").disabled = !ready;
    $("copyYaml").disabled = !ready;
    $("copyPrompt").disabled = !cls;
    const agents = state.agents.filter((a) => a !== "web");
    $("install").textContent = !slotOk ? "슬롯 이름은 글자, 숫자, -, _ 로 씁니다." : [
      `mkdir -p ${dest.replace(/\/[^/]+$/, "")}`,
      `mv ~/Downloads/${file} ${dest}`,
      slot ? `cd <작업 폴더> && python3 <docs-suit 경로>/suit.py profile use ${slot} --here` : null,
      agents.length ? `python3 <docs-suit 경로>/suit.py export --agent ${agents.join(",")}` : null,
      state.agents.indexOf("web") >= 0 ? "웹 채팅은 '웹 채팅용 지침 복사' 로 받은 지침을 맞춤 지침에 붙여 넣습니다" : null,
    ].filter(Boolean).join("\n");
  }

  function render() {
    renderClasses();
    renderPresets();
    renderBases();
    renderPersona();
    renderAgents();
    renderAside();
  }

  async function copy(text, done) {
    try {
      await navigator.clipboard.writeText(text);
      $("status").textContent = done;
    } catch (e) {
      $("status").textContent = "복사하지 못했습니다. 브라우저가 클립보드를 막았습니다.";
    }
  }

  function wire() {
    $("slot").addEventListener("input", renderAside);
    $("download").addEventListener("click", () => {
      const slot = $("slot").value.trim();
      const blob = new Blob([C.dumpYaml(slotData())], { type: "text/yaml" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = slot ? `${slot}.yaml` : "profile.yaml";
      a.click();
      URL.revokeObjectURL(a.href);
      $("status").textContent = "내려받았습니다. 아래 명령으로 제자리에 둡니다.";
    });
    $("copyYaml").addEventListener("click", () => copy(C.dumpYaml(slotData()), "슬롯 파일을 복사했습니다."));
    $("copyPrompt").addEventListener("click", () => {
      const data = slotData();
      const r = C.resolve(null, [], {}, data, state.cls);
      copy(C.compose(null, r.auds, r.vals, null, "prompt", false, r.cls, data.persona),
        "웹 채팅용 지침을 복사했습니다. 맞춤 지침이나 프로젝트 지침에 붙여 넣으세요.");
    });
  }

  fetch("themes.json").then((r) => r.json()).then((data) => {
    T = data;
    C = ThemeCore(T);
    wire();
    render();
  }).catch(() => {
    $("yaml").value = "themes.json 을 읽지 못했습니다. 로컬에서 열 때는 docs 폴더에서 python3 -m http.server 로 띄워 주세요.";
  });
})();
