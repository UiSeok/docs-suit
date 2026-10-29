// 웹 판의 써 보기 탭. 설치 없이 들어온 사람이 클래스와 템플릿을 고르고, 지침을 붙인 요청을 자기 AI 에 채워 연다.
// 템플릿은 themes/ko/trials/ 에서 오고, 축 값은 고를 수 없다. 문서 종류와 독자, 클래스의 기본값으로 core.js 가 조립한다.
// 클래스마다 끝에 두는 자유 형식은 종류 없이 조립해, 말투와 분량을 요청에 적은 대로 따르게 한다.
// ChatGPT 와 Claude 는 주소의 q 로 입력창을 채운다. Gemini 는 긴 주소를 받지 않아 복사해 두고 연다.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const OPEN = { gpt: "https://chatgpt.com/?q=", claude: "https://claude.ai/new?q=" };
  const FREE = "free";
  const NOTE = {
    trial: "예시 그대로 보내도 되고, 정류장 조사 대신 내 일을 적어도 됩니다. 글의 형식은 2번에서 고른 대로입니다.",
    free: "쓸 글과 읽을 사람, 담을 내용을 적습니다. 말투와 분량도 적으면 그대로 따릅니다.",
  };
  const state = { cls: null, trial: null };
  let T = null, C = null;

  function esc(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

  function trialsOf(cls) { return Object.keys(T.trials).filter((k) => T.trials[k].class === cls); }

  function rules() {
    if (state.trial === FREE) {
      const r = C.resolve(null, [], {}, null, null, true);
      return C.compose(null, r.auds, r.vals, null, "prompt", false, r.cls, null);
    }
    const t = T.trials[state.trial];
    const r = C.resolve(t.kind, [t.audience], {}, null, t.class, false);
    return C.compose(t.kind, r.auds, r.vals, null, "prompt", false, r.cls, null);
  }

  function withRules() { return `${rules()}\n---\n\n위 지침을 이번 글의 규칙으로 따른다.\n\n${$("ask").value.trim()}\n`; }

  function buildClasses() {
    $("classes").innerHTML = Object.keys(T.classes).map((c) =>
      `<button type="button" class="chip" data-cls="${c}" aria-pressed="${c === state.cls}">${esc(T.classes[c].label)}</button>`).join("");
  }

  function buildTrials() {
    $("trials").innerHTML = trialsOf(state.cls).map((k) => {
      const t = T.trials[k];
      const sub = `읽는 사람 ${T.audiences[t.audience].label}`;
      return `<button type="button" class="opt" data-trial="${k}" aria-pressed="${k === state.trial}"><b>${esc(t.label)}</b><span class="d">${esc(sub)}</span></button>`;
    }).join("") + `<button type="button" class="opt" data-trial="${FREE}" aria-pressed="${state.trial === FREE}"><b>자유 형식</b><span class="d">형식과 말투를 요청에 적은 대로</span></button>`;
  }

  function links() {
    const full = withRules(), raw = $("ask").value.trim();
    $("gpt").href = OPEN.gpt + encodeURIComponent(full);
    $("claude").href = OPEN.claude + encodeURIComponent(full);
    $("gptRaw").href = OPEN.gpt + encodeURIComponent(raw);
    $("claudeRaw").href = OPEN.claude + encodeURIComponent(raw);
    $("rules").value = rules();
    const t = T.trials[state.trial];
    $("picked").textContent = t ? `${T.kinds[t.kind].label} · ${T.audiences[t.audience].label} · 기본값` : "자유 형식";
  }

  function pick(trial) {
    state.trial = trial;
    const free = trial === FREE;
    $("ask").value = free ? "" : T.trials[trial].ask;
    $("ask").placeholder = free ? "예) 팀원들에게 보낼 다음 주 사무실 이사 공지를 해요체로 짧게 써 줘.\n- 이사 날짜는 다음 주 금요일\n- 짐은 목요일 저녁까지 상자에 담아 둔다" : "";
    $("askNote").textContent = free ? NOTE.free : NOTE.trial;
    $("reset").hidden = free;
    $("status").textContent = "";
    buildTrials();
    links();
  }

  function pickClass(cls) {
    state.cls = cls;
    buildClasses();
    pick(trialsOf(cls)[0]);
  }

  // 자유 형식에서 요청을 비운 채 보내면 AI 가 무엇을 쓸지 되묻기만 한다. 보내기 전에 막고 칸으로 돌려보낸다
  function empty(e) {
    if ($("ask").value.trim()) return false;
    e.preventDefault();
    $("status").textContent = "3번에 쓸 글을 먼저 적어 주세요.";
    $("ask").focus();
    return true;
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
    $("classes").addEventListener("click", (e) => { const b = e.target.closest("[data-cls]"); if (b) pickClass(b.dataset.cls); });
    $("trials").addEventListener("click", (e) => { const b = e.target.closest("[data-trial]"); if (b) pick(b.dataset.trial); });
    $("ask").addEventListener("input", links);
    $("reset").addEventListener("click", () => pick(state.trial));
    ["gpt", "claude", "gptRaw", "claudeRaw"].forEach((id) => $(id).addEventListener("click", empty));
    $("copy").addEventListener("click", (e) => { if (!empty(e)) copy(withRules(), "지침을 붙인 요청을 복사했습니다. 쓰는 AI 의 입력창에 붙여 넣으세요."); });
    // 복사는 누른 그 순간에 해야 브라우저가 허락한다. 링크는 막지 않고 그대로 새 창에서 연다
    $("gemini").addEventListener("click", (e) => { if (!empty(e)) copy(withRules(), "요청을 복사했습니다. 열린 Gemini 입력창에 붙여 넣고 보내세요."); });
  }

  fetch("themes.json").then((r) => r.json()).then((data) => {
    T = data;
    C = ThemeCore(T);
    wire();
    const want = new URLSearchParams(location.search).get("class");
    pickClass(want in T.classes ? want : "office");
  }).catch(() => { $("status").textContent = "themes.json 을 읽지 못했습니다."; });
})();
