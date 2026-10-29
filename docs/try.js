// 웹 판의 써 보기 탭. 설치 없이 들어온 사람이 클래스와 템플릿을 고르고, 지침을 붙인 요청을 자기 AI 에 채워 연다.
// 템플릿은 themes/ko/trials/ 에서 오고, 축 값은 고를 수 없다. 문서 종류와 독자, 클래스의 기본값으로 core.js 가 조립한다.
// ChatGPT 와 Claude 는 주소의 q 로 입력창을 채운다. Gemini 는 긴 주소를 받지 않아 복사해 두고 연다.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const OPEN = { gpt: "https://chatgpt.com/?q=", claude: "https://claude.ai/new?q=" };
  const state = { cls: null, trial: null };
  let T = null, C = null;

  function esc(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

  function trialsOf(cls) { return Object.keys(T.trials).filter((k) => T.trials[k].class === cls); }

  function rules() {
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
    }).join("");
  }

  function links() {
    const full = withRules(), raw = $("ask").value.trim();
    $("gpt").href = OPEN.gpt + encodeURIComponent(full);
    $("claude").href = OPEN.claude + encodeURIComponent(full);
    $("gptRaw").href = OPEN.gpt + encodeURIComponent(raw);
    $("claudeRaw").href = OPEN.claude + encodeURIComponent(raw);
    $("rules").value = rules();
    const t = T.trials[state.trial];
    $("picked").textContent = `${T.kinds[t.kind].label} · ${T.audiences[t.audience].label} · 기본값`;
  }

  function pick(trial) {
    state.trial = trial;
    $("ask").value = T.trials[trial].ask;
    $("status").textContent = "";
    buildTrials();
    links();
  }

  function pickClass(cls) {
    state.cls = cls;
    buildClasses();
    pick(trialsOf(cls)[0]);
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
    $("copy").addEventListener("click", () => copy(withRules(), "지침을 붙인 요청을 복사했습니다. 쓰는 AI 의 입력창에 붙여 넣으세요."));
    // 복사는 누른 그 순간에 해야 브라우저가 허락한다. 링크는 막지 않고 그대로 새 창에서 연다
    $("gemini").addEventListener("click", () => copy(withRules(), "요청을 복사했습니다. 열린 Gemini 입력창에 붙여 넣고 보내세요."));
  }

  fetch("themes.json").then((r) => r.json()).then((data) => {
    T = data;
    C = ThemeCore(T);
    wire();
    const want = new URLSearchParams(location.search).get("class");
    pickClass(want in T.classes ? want : "office");
  }).catch(() => { $("status").textContent = "themes.json 을 읽지 못했습니다."; });
})();
