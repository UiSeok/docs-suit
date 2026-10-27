// 웹 고르개 화면. 조립은 core.js 가 하고, 데이터는 themes.json 하나다.
// 축마다 같은 예문을 값별로 써 본 보기 카드를 보이고, 카드를 누르면 그 값을 고른다. 다시 누르면 자동으로 돌아간다.
// 개인 기본값은 이 브라우저의 localStorage 에만 남는다.
(function () {
  "use strict";
  const KEY = "geulot.personal";
  const $ = (id) => document.getElementById(id);
  // 화면에 보이는 축 순서. 글에 바로 드러나는 축을 앞에 둔다.
  const SHOW = ["voice", "register", "skeleton", "terms", "length", "sources", "exposure", "ai-disclosure",
    "diagram", "emphasis", "visual-deck", "visual-doc"];
  const state = { kind: "report", aud: null, sets: {} };
  let T = null, C = null;

  function loadPersonal() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function savePersonal(p) {
    try { localStorage.setItem(KEY, JSON.stringify(p)); return true; } catch (e) { return false; }
  }

  // ---------------------------------------------------------------- 보기용 작은 마크다운
  function esc(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
  function inline(s) {
    return esc(s)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, "<a>$1</a>");
  }
  function md(src) {
    const lines = src.split("\n"), out = [];
    for (let i = 0; i < lines.length; i++) {
      const l = lines[i];
      if (l.startsWith("```")) {
        const buf = [];
        for (i++; i < lines.length && !lines[i].startsWith("```"); i++) buf.push(lines[i]);
        out.push("<pre>" + esc(buf.join("\n")) + "</pre>");
      } else if (l.startsWith("### ")) {
        out.push("<h4>" + inline(l.slice(4)) + "</h4>");
      } else if (l.startsWith("- ")) {
        const buf = [];
        for (; i < lines.length && lines[i].startsWith("- "); i++) buf.push("<li>" + inline(lines[i].slice(2)) + "</li>");
        i--;
        out.push("<ul>" + buf.join("") + "</ul>");
      } else if (l.startsWith("|")) {
        const rows = [];
        for (; i < lines.length && lines[i].startsWith("|"); i++) {
          if (/^\|[-| ]+\|$/.test(lines[i])) continue;
          rows.push("<tr>" + lines[i].slice(1, -1).split("|").map((c) => "<td>" + inline(c.trim()) + "</td>").join("") + "</tr>");
        }
        i--;
        out.push("<table>" + rows.join("") + "</table>");
      } else if (l.trim()) {
        out.push("<p>" + inline(l) + "</p>");
      }
    }
    return out.join("");
  }

  // ---------------------------------------------------------------- 보기 그리기
  function deckPreview(sample) {
    const m = sample.match(/```json\n([\s\S]*?)\n```/);
    let t = {};
    try { t = JSON.parse(m[1]); } catch (e) { /* 색 정보가 없으면 기본색으로 그린다 */ }
    const head = t.head === "serif" ? "'Noto Serif KR', 'AppleMyungjo', serif" : "inherit";
    return `<span class="deck" style="display:flex;background:${esc(t.bg)};color:${esc(t.ink)}">
      <span class="s" style="color:${esc(t.muted)}">정류장 대기 조사</span>
      <span class="t" style="font-family:${head}">8시대 버스 한 대가<br>대기를 절반으로 줄인다</span>
      <span class="bar" style="display:block;background:${esc(t.accent)}"></span>
      <span class="n" style="color:${esc(t.accent)}">12분 → 6분</span>
      <span class="s" style="color:${esc(t.muted)}">출근 시간대 평균 대기</span></span>`;
  }
  const DOC_SAMPLE = "<h2>정류장 대기 시간 조사</h2><p>출근 시간대 평균 대기는 <strong>12분</strong>으로 다른 시간대의 두 배였다.</p>" +
    "<table><tr><th>시간대</th><th>대기</th></tr><tr><td>8시</td><td>12분</td></tr><tr><td>14시</td><td>6분</td></tr></table>" +
    "<blockquote>8시대 1회 증차를 제안한다.</blockquote>";
  function docPreview(value) {
    const doc = `<!doctype html><meta charset="utf-8"><style>${T.css[value] || ""} body{font-size:13px;margin:0 auto;padding:10px}</style>${DOC_SAMPLE}`;
    return `<iframe title="${esc(value)} 보기" sandbox srcdoc="${esc(doc)}" tabindex="-1"></iframe>`;
  }
  function preview(axis, value) {
    const sample = T.samples[`${axis}/${value}`] || "";
    if (axis === "visual-deck") return deckPreview(sample);
    if (axis === "visual-doc") return docPreview(value);
    return md(sample);
  }

  // ---------------------------------------------------------------- 화면
  function chip(box, label, pressed, onClick) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.textContent = label;
    b.setAttribute("aria-pressed", String(pressed));
    b.addEventListener("click", onClick);
    box.appendChild(b);
  }

  function buildChips() {
    const k = $("kinds");
    k.textContent = "";
    chip(k, "일반 글", state.kind === null, () => { state.kind = null; render(); });
    for (const [key, v] of Object.entries(T.kinds)) chip(k, v.label, state.kind === key, () => { state.kind = key; render(); });
    const a = $("auds");
    a.textContent = "";
    const def = state.kind && T.kinds[state.kind].audience
      ? T.kinds[state.kind].audience.map((x) => T.audiences[x].label).join(", ") : "없음";
    chip(a, `문서 종류의 기본 (${def})`, state.aud === null, () => { state.aud = null; render(); });
    for (const [key, v] of Object.entries(T.audiences)) chip(a, v.label, state.aud === key, () => { state.aud = key; render(); });
  }

  function buildGallery(vals) {
    const g = $("gallery");
    const keepScroll = {};
    g.querySelectorAll(".cards").forEach((row) => { keepScroll[row.dataset.axis] = row.scrollLeft; });
    g.textContent = "";
    const kspec = state.kind ? T.kinds[state.kind] : {};
    for (const axis of SHOW) {
      const [v, src] = vals[axis];
      const sec = document.createElement("section");
      sec.className = "step";
      const h = document.createElement("h2");
      h.innerHTML = `${esc(T.axes[axis].label)} <span class="now">지금 <b>${esc(C.label(axis, v))}</b> · ${esc(C.SRC[src])}</span>`;
      sec.appendChild(h);
      const locked = kspec[axis] && axis !== "exposure";
      let note = "";
      if (locked) note = "이 축은 문서 종류가 정합니다.";
      else if (axis === "visual-deck" && state.kind !== "slides") note = "발표 PPT 를 고를 때만 지침에 실립니다.";
      else if (axis === "visual-doc" && !$("html").checked) note = "오른쪽 '문서 디자인 규칙 포함' 을 켜면 지침에 실립니다.";
      else if (axis === "exposure") note = "개인정보를 지키는 축이라 정해진 범위보다 넓힐 수는 없습니다.";
      if (note) {
        const n = document.createElement("p");
        n.className = "note";
        n.textContent = note;
        sec.appendChild(n);
      }
      const row = document.createElement("div");
      row.className = "cards";
      row.dataset.axis = axis;
      for (const [value, lab] of Object.entries(T.axes[axis].values)) {
        const b = document.createElement("button");
        b.type = "button";
        const chosen = state.sets[axis] === value, active = v === value;
        b.className = "card" + (active ? " active" : "") + (chosen ? " chosen" : "");
        b.disabled = !!locked;
        b.setAttribute("aria-pressed", String(chosen));
        b.setAttribute("aria-label", `${T.axes[axis].label} ${lab}${active ? ", 지금 쓰는 값" : ""}`);
        const kind = axis === "visual-doc" ? " frame" : axis === "visual-deck" ? " slide" : "";
        b.innerHTML = `<span class="cl"><span>${esc(lab)}</span><span class="badge">${chosen ? "고름" : active ? "자동" : ""}</span></span>` +
          `<span class="pv${kind}">${preview(axis, value)}</span>`;
        b.addEventListener("click", () => {
          if (state.sets[axis] === value) delete state.sets[axis];
          else state.sets[axis] = value;
          render();
        });
        row.appendChild(b);
      }
      sec.appendChild(row);
      g.appendChild(sec);
      if (keepScroll[axis]) row.scrollLeft = keepScroll[axis];
    }
  }

  function render() {
    const auds = state.aud ? [state.aud] : [];
    const r = C.resolve(state.kind, auds, state.sets, loadPersonal());
    buildChips();
    buildGallery(r.vals);
    $("warns").textContent = r.warns.join(" ");
    const chars = parseInt($("chars").value, 10) || null;
    const fmt = document.querySelector("input[name=fmt]:checked").value;
    $("out").value = C.compose(state.kind, r.auds, r.vals, chars, fmt, $("html").checked);
  }

  function wire() {
    document.querySelectorAll("aside input").forEach((el) => el.addEventListener("input", render));
    $("copy").addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText($("out").value);
        $("status").textContent = "복사했습니다.";
      } catch (e) {
        $("out").select();
        $("status").textContent = "선택해 두었습니다. Ctrl+C 로 복사하세요.";
      }
    });
    $("download").addEventListener("click", () => {
      const blob = new Blob([$("out").value], { type: "text/markdown" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `geulot-${state.kind || "general"}.md`;
      a.click();
      URL.revokeObjectURL(a.href);
    });
    $("save").addEventListener("click", () => {
      const ok = savePersonal({ defaults: { ...state.sets } });
      $("status").textContent = ok ? "고른 값을 이 브라우저의 내 기본값으로 저장했습니다." : "저장하지 못했습니다. 브라우저 저장소가 막혀 있습니다.";
      render();
    });
    $("reset").addEventListener("click", () => {
      savePersonal({});
      state.sets = {};
      $("chars").value = "";
      $("status").textContent = "고른 값과 내 기본값을 지웠습니다.";
      render();
    });
  }

  fetch("themes.json").then((r) => r.json()).then((data) => { T = data; C = ThemeCore(T); wire(); render(); })
    .catch(() => { $("out").value = "themes.json 을 읽지 못했습니다. 로컬에서 열 때는 docs 폴더에서 python3 -m http.server 로 띄워 주세요."; });
})();
