// 로컬로 띄운 화면(suit.py serve)인지 알아보고, 맞으면 맨 위에 "이 컴퓨터에 바로 적용" 띠를 그린다.
// 엔진이 화면에 심은 열쇠를 모든 요청에 붙인다. GitHub Pages 로 열면 열쇠가 없어서 아무것도 하지 않는다.
(function (root) {
  "use strict";
  const meta = document.querySelector('meta[name="docs-suit-token"]');
  const token = meta ? meta.content : null;

  async function api(path, body) {
    const opts = { headers: { "X-Docs-Suit-Token": token } };
    if (body !== undefined) {
      opts.method = "POST";
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    const r = await fetch(path, opts);
    const j = await r.json();
    if (!r.ok || j.ok === false) throw new Error(j.message || `요청이 실패했습니다 (${r.status})`);
    return j;
  }

  function short(path) { return String(path).replace(/^\/Users\/[^/]+/, "~"); }

  // 띠: 실행한 폴더, 지금 슬롯과 고른 까닭, 슬롯 바꾸기, 끄기
  function banner(state, onSlot) {
    let box = document.getElementById("local");
    if (!box) return;
    box.className = "local";
    box.textContent = "";
    const why = { env: "환경 변수", arg: "직접 고름", folder: "폴더 파일", current: "profile use", default: "기본 슬롯" }[state.why] || "";
    const t = document.createElement("span");
    t.innerHTML = `<b>이 컴퓨터에 바로 적용</b> · 폴더 <code></code> · 슬롯 `;
    const code = t.querySelector("code");
    code.textContent = String(state.cwd).split("/").filter(Boolean).pop() || state.cwd;
    code.title = short(state.cwd);
    const sel = document.createElement("select");
    sel.setAttribute("aria-label", "슬롯");
    for (const s of state.slots) {
      const o = document.createElement("option");
      o.value = s.name;
      o.textContent = s.name + (s.call ? ` · ${s.call}` : "") + (s.exists ? "" : " (아직 없음)");
      o.selected = s.name === (state.slot || "default");
      sel.appendChild(o);
    }
    sel.addEventListener("change", () => onSlot(sel.value));
    const w = document.createElement("span");
    w.className = "muted";
    w.textContent = ` ${why}` + (state.growth ? ` · [${state.growth.title || ""}] Lv.${state.growth.level}` : "");
    const stop = document.createElement("button");
    stop.type = "button";
    stop.className = "btn";
    stop.textContent = "끄기";
    stop.addEventListener("click", async () => {
      try {
        const r = await api("/api/stop", {});
        box.textContent = r.message;
      } catch (e) { box.textContent = e.message; }
    });
    box.append(t, sel, w, stop);
  }

  root.DocsSuitLocal = token ? { token, api, banner, short } : null;
})(typeof self !== "undefined" ? self : this);
