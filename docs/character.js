// 캐릭터 탭. 캐릭터 카드와 꾸미기, 성장 기록, 승급 키를 보인다. 이 컴퓨터의 슬롯과 기록을 읽으므로 suit.py serve 로 띄웠을 때만 그린다.
// 고치는 일은 모두 엔진 API 로 보내고, 엔진은 대화의 look, growth, promote 와 같은 함수로 처리한다.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const PARTS = ["hair", "top", "color", "prop"];
  const L = window.DocsSuitLocal;
  let T = null, C = null, st = null;

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

  function empty(text, tab) {
    $("char").hidden = true;
    const p = $("empty");
    p.hidden = false;
    p.textContent = text + " ";
    if (tab) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "btn primary";
      b.textContent = "캐릭터 설정으로";
      b.addEventListener("click", () => window.DocsSuitTab(tab));
      p.appendChild(b);
    }
  }

  function label(part, value) {
    if (!value) return part === "color" ? "기본" : "없음";
    return part === "color" ? T.look.colors[value].label : T.look[part][value];
  }

  function renderCard(ch) {
    draw($("portrait"), C.lookGrid(ch.look), 10);
    const who = $("who");
    const pct = ch.need ? Math.round((ch.into / ch.need) * 100) : 100;
    who.innerHTML = `<div class="t">${ch.title ? `[${esc(ch.title)}] ` : ""}${esc(ch.name)}</div>` +
      `<div class="s">${esc(ch.classLabel || "클래스 없음")} · ${ch.tier ? `${ch.tier}차 전직` : "전직 전"}</div>` +
      `<div class="s">Lv.${ch.level} <span class="lvbar" role="img" aria-label="경험치 ${ch.into}/${ch.need}"><i style="width:${pct}%"></i></span> ` +
      (ch.need ? `${ch.into}/${ch.need}` : "최고 레벨") + `</div>` +
      `<div class="s">문서 ${ch.docs}건 · 도감 ${Object.keys(ch.kinds).length}/${ch.dex} 종류</div>`;
    $("statusline").textContent = ch.status;
    const next = $("next");
    next.textContent = "";
    const li = document.createElement("li");
    if (ch.next) {
      const n = ch.next;
      const when = n.keyed && ch.level >= n.level ? "승급 키를 받으면" : `Lv.${n.level}` + (n.keyed ? " + 승급 키" : "");
      li.innerHTML = `다음 전직 ${esc(when)} <b>[${esc(n.title || `${n.tier}차`)}]</b>` + (n.opens.length ? ` · ${esc(n.opens.join(" · "))} 열림` : "");
    } else {
      li.textContent = "전직을 모두 마쳤습니다.";
    }
    next.appendChild(li);
    $("growthOn").checked = ch.growthOn;
  }

  function renderLooks(ch) {
    const box = $("looks");
    box.textContent = "";
    const opened = ch.open;
    const later = {};
    for (const x of ch.later) later[`${x.part}.${x.value}`] = x.tier;
    for (const part of PARTS) {
      const table = part === "color" ? T.look.colors : T.look[part];
      // 옷 색과 소품은 비울 수 있다. 머리와 옷은 늘 하나를 입는다
      const values = (part === "color" || part === "prop" ? ["none"] : []).concat(Object.keys(table));
      const shown = values.filter((v) => v === "none" || opened[part].indexOf(v) >= 0 || later[`${part}.${v}`]);
      const h = document.createElement("h3");
      h.className = "parthead";
      h.textContent = `${T.look.parts[part]} · 지금 ${label(part, ch.look[part])}`;
      box.appendChild(h);
      const row = document.createElement("div");
      row.className = "opts looks";
      for (const v of shown) {
        const now = (ch.look[part] || "none") === v;
        const lockedAt = v !== "none" && opened[part].indexOf(v) < 0 ? later[`${part}.${v}`] : null;
        const b = document.createElement("button");
        b.type = "button";
        b.className = "opt base";
        b.setAttribute("aria-pressed", String(now));
        b.disabled = !!lockedAt;
        b.innerHTML = `<canvas class="portrait"></canvas><b>${esc(label(part, v === "none" ? null : v))}</b>` +
          (lockedAt ? `<span class="d">${lockedAt}차 전직에서 열림</span>` : "");
        const look = Object.assign({}, ch.look, { [part]: v === "none" ? null : v });
        draw(b.querySelector("canvas"), C.lookGrid(look), 4);
        if (lockedAt) b.querySelector("canvas").classList.add("locked");
        b.addEventListener("click", () => { if (!now) post("/api/look", { part, value: v }); });
        row.appendChild(b);
      }
      if (!shown.length || (shown.length === 1 && shown[0] === "none")) {
        const p = document.createElement("p");
        p.className = "note";
        p.textContent = "이 클래스는 이 부위를 여는 보상이 없습니다.";
        row.appendChild(p);
      }
      box.appendChild(row);
    }
  }

  function renderLog(ch) {
    $("logNote").textContent = `문서 ${ch.docs}건 · 경험치 ${ch.exp}`;
    const dex = $("dex");
    dex.textContent = "";
    for (const [k, v] of Object.entries(T.kinds)) {
      const n = ch.kinds[k] || 0;
      const c = document.createElement("span");
      c.className = "chip dexchip" + (n ? " got" : "");
      c.textContent = n ? `${v.label} ${n}` : v.label;
      dex.appendChild(c);
    }
    const tbl = $("log");
    tbl.textContent = "";
    if (!ch.log.length) {
      tbl.innerHTML = `<tr><td class="muted">아직 기록이 없습니다. 문서를 쓰고 검사하면 쌓입니다.</td></tr>`;
      return;
    }
    tbl.innerHTML = "<tr><th>날짜</th><th>종류</th><th>경험치</th><th>받은 까닭</th></tr>" + ch.log.map((r) =>
      `<tr><td>${esc(r.day)}</td><td>${esc(r.label)}</td><td>+${r.points}</td><td>${esc(r.parts.join(", ") || "그날 같은 종류를 넘게 써 경험치 없음")}</td></tr>`).join("");
  }

  function renderKeys(ch) {
    const ul = $("keys");
    ul.textContent = "";
    for (const k of ch.keys) {
      const li = document.createElement("li");
      li.textContent = `${k.tier}차 승급 키 · @${k.who}` + (k.ref ? ` · ${k.ref}` : "") + (k.at ? ` · ${k.at}` : "");
      ul.appendChild(li);
    }
    if (!ch.keys.length) {
      const li = document.createElement("li");
      li.className = "muted";
      li.textContent = "받은 키가 없습니다.";
      ul.appendChild(li);
    }
  }

  function render() {
    if (!st.exists || !st.character) return empty("이 폴더에 이은 캐릭터가 없습니다. 캐릭터 설정에서 만들거나 다른 폴더의 캐릭터를 이 폴더에 잇습니다.", "setup");
    $("empty").hidden = true;
    $("char").hidden = false;
    const ch = st.character;
    renderCard(ch);
    renderLooks(ch);
    renderLog(ch);
    renderKeys(ch);
    L.banner(st, async (name) => { st = await L.api(L.stateUrl(name)); render(); });
  }

  async function post(path, body) {
    try {
      const r = await L.api(path, Object.assign({ slot: st.slot }, body));
      st = r.state;
      render();
      $("status").textContent = r.message;
      L.changed();
    } catch (e) { $("status").textContent = e.message; }
  }

  function wire() {
    $("growthOn").addEventListener("change", () => post("/api/growth", { on: $("growthOn").checked }));
    $("addKey").addEventListener("click", () => {
      const key = $("key").value.trim();
      if (!key) return;
      post("/api/promote", { key }).then(() => { $("key").value = ""; });
    });
  }

  fetch("themes.json" + ((m) => (m ? `?v=${m.content}` : ""))(document.querySelector('meta[name="docs-suit-data"]'))).then((r) => r.json()).then(async (data) => {
    T = data;
    C = ThemeCore(T);
    if (!L) return empty("캐릭터 탭은 이 컴퓨터의 기록을 읽어서 suit.py serve 로 띄운 화면에서 보입니다. 에이전트에게 \"docs-suit 대시보드 열어 줘\" 라고 하면 됩니다.", "setup");
    document.body.classList.add("is-local");
    wire();
    try { st = await L.api(L.stateUrl()); render(); } catch (e) { empty(e.message); }
  }).catch(() => empty("themes.json 을 읽지 못했습니다."));
})();
