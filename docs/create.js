// 대시보드의 캐릭터 설정 탭. suit.py bootstrap 이 묻는 것을 웹으로 옮겼다.
// 슬롯 파일의 꼴과 캐릭터 그림은 core.js 가 엔진과 같은 규칙으로 만들고, tests/parity.js 가 견준다.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const AGENTS = [["claude", "Claude Code"], ["codex", "Codex CLI"], ["antigravity", "Antigravity CLI"],
    ["cursor", "Cursor"], ["grok", "Grok Build"], ["web", "웹 채팅"]];
  const SLOT_RE = /^[\p{L}\p{N}_-]+$/u;  // suit.py 의 슬롯 이름 규칙과 같다
  const state = { cls: null, preset: null, hair: null, persona: {}, docs: [], agents: [], keep: null };
  // 문체 배우기. 붙여 넣은 글은 화면에만 두고, 잰 결과와 사용자가 고른 축 값만 슬롯에 넣는다
  const learn = { texts: [""], human: [], result: null, use: {} };
  const L = window.DocsSuitLocal;  // suit.py serve 로 띄웠으면 슬롯 파일을 바로 쓴다
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
    if (state.hair) data.look = { hair: state.hair };
    // 조합을 고르면 조합의 값, 고르지 않았으면 불러온 슬롯에 있던 값을 그대로 둔다
    const p = (state.preset && T.presets[state.preset]) || state.keep;
    if (p) {
      data.defaults = Object.assign({}, p.defaults || {});
      data.audiences = {};
      for (const [k, v] of Object.entries(p.audiences || {})) data.audiences[k] = Object.assign({}, v);
    }
    // 예전 글에서 배운 값은 조합의 값보다 앞선다. 사용자가 고른 것만 넣는다
    const learned = learnedValues();
    if (Object.keys(learned).length) data.defaults = Object.assign({}, data.defaults || {}, learned);
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
    opt(box, state.preset === null, state.keep
      ? `<b>지금 슬롯의 값 그대로</b><span class="d">불러온 슬롯에 저장된 말투와 독자별 값을 그대로 둡니다</span>`
      : `<b>클래스 기본값으로 시작</b><span class="d">고른 클래스의 기본 말투를 그대로 씁니다</span>`,
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
    const first = T.look.base[Object.keys(T.look.base)[0]].hair;
    for (const [key, label] of Object.entries(T.look.hair || {})) {
      const btn = opt(box, (state.hair || first) === key, `<canvas class="portrait"></canvas><b>${esc(label)}</b>`,
        () => { state.hair = key; render(); }, "base");
      draw(btn.querySelector("canvas"), C.lookGrid(C.lookOf({ look: { hair: key } }, 0)), 5);
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
        input.addEventListener("input", () => {
          state.persona[key] = input.value;
          if (key === "call") $("styleTitle").textContent = `5. ${C.cleanText(input.value) || "나"}만의 글쓰기 스타일`;
          renderAside();
        });
        label.appendChild(input);
      }
      box.appendChild(label);
    }
  }

  function learnedValues() {
    const out = {};
    const plan = (learn.result && learn.result.plan) || {};
    for (const [axis, x] of Object.entries(plan)) if (x.value && learn.use[axis] !== false) out[axis] = x.value;
    return out;
  }

  function renderLearn() {
    const call = C.cleanText(state.persona.call || "");
    $("styleTitle").textContent = `5. ${call || "나"}만의 글쓰기 스타일`;
    const box = $("learn");
    box.textContent = "";
    if (!L) {
      const p = document.createElement("p");
      p.className = "hint";
      p.textContent = "이 칸은 suit.py serve 로 띄운 화면에서 씁니다. 에이전트에게 \"예전 글로 내 문체 맞춰 줘\" 라고 해도 됩니다.";
      box.appendChild(p);
      return;
    }
    learn.texts.forEach((text, i) => {
      const label = document.createElement("label");
      label.textContent = `글 ${i + 1}`;
      const ta = document.createElement("textarea");
      ta.className = "sample";
      ta.value = text;
      ta.placeholder = "예전에 쓴 보고서나 메일, 글 한 편을 붙여 넣습니다";
      ta.addEventListener("input", () => { learn.texts[i] = ta.value; });
      label.appendChild(ta);
      const sample = learn.result && learn.result.samples[i];
      if (sample) {
        const info = document.createElement("span");
        info.className = "hint";
        const parts = [`${sample.chars.toLocaleString()}자`];
        if (sample.register) parts.push(`어법 ${C.label("register", sample.register)}`);
        if (sample.voice) parts.push(`문체 ${C.label("voice", sample.voice)}`);
        info.textContent = parts.join(" · ");
        label.appendChild(info);
        if (sample.suspect || sample.vouched) {
          const w = document.createElement("label");
          w.className = "inline";
          const cb = document.createElement("input");
          cb.type = "checkbox";
          cb.checked = learn.human.indexOf(i) >= 0;
          cb.addEventListener("change", () => {
            if (cb.checked) learn.human.push(i); else learn.human = learn.human.filter((x) => x !== i);
          });
          w.append(cb, ` AI 가 쓴 글의 표지(${sample.ai.join(", ")})가 있어 제안에서 뺐습니다. 직접 쓴 글이면 체크하고 다시 잽니다`);
          label.appendChild(w);
        }
        if (sample.secret) {
          const s = document.createElement("span");
          s.className = "warn";
          s.textContent = "키나 비밀번호로 보이는 값이 있습니다. 이 글은 다른 곳에 옮기지 마세요.";
          label.appendChild(s);
        }
      }
      box.appendChild(label);
    });
    const row = document.createElement("div");
    row.className = "actions";
    const more = document.createElement("button");
    more.type = "button";
    more.className = "btn";
    more.textContent = "글 더하기";
    more.disabled = learn.texts.length >= 6;
    more.addEventListener("click", () => { learn.texts.push(""); renderLearn(); });
    const run = document.createElement("button");
    run.type = "button";
    run.className = "btn primary";
    run.textContent = "문체 재기";
    run.addEventListener("click", async () => {
      // 빈 칸을 먼저 걷어야 엔진이 돌려준 글 번호와 칸 번호가 맞는다
      learn.texts = learn.texts.filter((x) => x.trim());
      if (!learn.texts.length) learn.texts = [""];
      try {
        learn.result = await L.api("/api/learn", { texts: learn.texts, human: learn.human });
        learn.use = {};
      } catch (e) { learn.result = null; $("status").textContent = e.message; }
      renderLearn();
      renderAside();
    });
    row.append(more, run);
    box.appendChild(row);
    if (!learn.result) return;
    const plan = learn.result.plan;
    const out = document.createElement("div");
    out.className = "learned";
    const head = document.createElement("p");
    head.innerHTML = `<b>제안</b> · 사람이 쓴 것으로 보는 글 ${learn.result.chars.toLocaleString()}자`;
    out.appendChild(head);
    if (!Object.keys(plan).length) {
      const p = document.createElement("p");
      p.className = "hint";
      p.textContent = "축 값을 정할 만큼 글이 모이지 않았습니다. 같은 사람이 쓴 글을 두세 편 더 붙여 넣어 보세요.";
      out.appendChild(p);
    }
    for (const [axis, x] of Object.entries(plan)) {
      const l = document.createElement("label");
      l.className = "inline";
      if (x.value) {
        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.checked = learn.use[axis] !== false;
        cb.addEventListener("change", () => { learn.use[axis] = cb.checked; renderAside(); });
        l.append(cb, ` ${T.axes[axis].label} ${C.label(axis, x.value)} · ${x.note}`);
      } else {
        l.textContent = `${T.axes[axis].label} · ${x.note}`;
      }
      out.appendChild(l);
    }
    const tip = document.createElement("p");
    tip.className = "hint";
    tip.textContent = learn.result.voice_ok
      ? "글이 넉넉합니다. 저장한 뒤 에이전트에게 \"내 문체 문서 만들어 줘\" 라고 하면 축에 잡히지 않는 버릇까지 정리해 줍니다."
      : "축 값만 제안했습니다. 세 편 넘게, 2천 자 넘게 모이면 에이전트가 버릇까지 담은 내 문체 문서를 만들 수 있습니다.";
    out.appendChild(tip);
    box.appendChild(out);
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
    const grid = C.lookGrid(C.lookOf({ look: { hair: state.hair } }, 0));
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
      const opened = cls ? C.openedAt(cls, p.tier).join(" · ") : "클래스의 꾸미기";
      li.innerHTML = `Lv.${p.level} <b>[${esc(nt)}]</b> · ${esc(opened)} 열림` +
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
    if (L) {
      $("whereHead").textContent = "저장하면";
      $("install").textContent = !slotOk ? "슬롯 이름은 글자, 숫자, -, _ 로 씁니다." : [
        `${dest} 에 씁니다. 있던 파일은 .bak 으로 남깁니다.`,
        slot && $("useHere").checked ? "실행한 폴더의 .docs-suit.yaml 이 이 슬롯을 쓰게 합니다." : null,
        $("installSkills").checked && agents.length ? `${agents.join(", ")} 에 스킬을 깝니다.` : null,
      ].filter(Boolean).join("\n");
      return;
    }
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
    renderLearn();
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

  // 불러온 슬롯으로 고른 값을 채운다. 조합은 슬롯에 남지 않으니 저장된 축 값을 keep 으로 들고 있는다
  function fill(st) {
    const prof = st.profile || {};
    const meta = prof.profile || {};
    state.cls = meta.class || null;
    state.persona = {};
    for (const k of T.personaInPrompt) state.persona[k] = (prof.persona || {})[k] || "";
    state.docs = ((prof.persona || {}).docs || []).slice();
    state.hair = (prof.look || {}).hair || null;
    state.agents = (meta.agents || []).slice();
    state.preset = null;
    state.keep = st.exists ? { defaults: prof.defaults || {}, audiences: prof.audiences || {} } : null;
    // 캐릭터는 폴더마다 따로 키운다. 폴더에 이은 슬롯이 없으면 폴더 이름으로 새 슬롯을 제안하고 이 폴더에 잇는다
    $("slot").value = st.why === "folder" || st.why === "arg" ? st.slot : st.suggest || "";
    $("useHere").checked = true;
    // 다른 폴더에서 만든 캐릭터를 띠에서 골랐으면 저장하지 않고 이 폴더에 이을 수 있다. 대화의 profile use --here 와 같다
    const folder = String(st.cwd).split("/").filter(Boolean).pop() || st.cwd;
    const canBind = st.exists && st.slot && st.slot !== "default" && st.bound !== st.slot;
    $("bindRow").hidden = !canBind;
    $("bindNote").textContent = canBind ? `폴더 ${folder} 은 ${st.bound ? `지금 슬롯 ${st.bound} 을 씁니다` : "아직 캐릭터를 잇지 않았습니다"}.` : "";
    $("bind").onclick = async () => {
      try {
        const r = await L.api("/api/use", { slot: st.slot });
        $("status").textContent = r.message;
        L.changed();
        fill(r.state);
      } catch (e) { $("status").textContent = e.message; }
    };
    L.banner(st, async (name) => {
      try { fill(await L.api(`/api/state?slot=${encodeURIComponent(name)}`)); } catch (e) { $("status").textContent = e.message; }
    });
    render();
  }

  async function saveLocal() {
    try {
      const r = await L.api("/api/slot", { slot: $("slot").value.trim() || "default", data: slotData(),
        install: $("installSkills").checked, useHere: $("useHere").checked });
      $("status").textContent = r.message;
      L.changed();
      L.banner(r.state, async (name) => {
        try { fill(await L.api(`/api/state?slot=${encodeURIComponent(name)}`)); } catch (e) { $("status").textContent = e.message; }
      });
    } catch (e) { $("status").textContent = e.message; }
  }

  function wire() {
    $("slot").addEventListener("input", renderAside);
    $("installSkills").addEventListener("change", renderAside);
    $("useHere").addEventListener("change", renderAside);
    $("download").addEventListener("click", () => {
      if (L) return saveLocal();
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

  fetch("themes.json" + ((m) => (m ? `?v=${m.content}` : ""))(document.querySelector('meta[name="docs-suit-data"]'))).then((r) => r.json()).then(async (data) => {
    T = data;
    C = ThemeCore(T);
    wire();
    if (L) {
      document.body.classList.add("is-local");
      $("download").textContent = "이 컴퓨터에 저장";
      try { fill(await L.api(L.stateUrl())); return; } catch (e) { $("status").textContent = e.message; }
    }
    render();
  }).catch(() => {
    $("yaml").value = "themes.json 을 읽지 못했습니다. 로컬에서 열 때는 docs 폴더에서 python3 -m http.server 로 띄워 주세요.";
  });
})();
