// 테마 조립 핵심. theme.py 의 resolve 와 compose 를 같은 순서로 옮겼다. 브라우저와 node 가 같이 쓴다.
(function (root) {
  "use strict";
  function make(T) {
    function fromAudiences(axis, auds, table) {
      const vals = auds.filter((a) => table[a] && table[a][axis]).map((a) => table[a][axis]);
      if (!vals.length) return null;
      const pick = (order) => vals.reduce((b, v) => (order.indexOf(v) < order.indexOf(b) ? v : b));
      if (axis === "exposure") return pick(T.exposureStrict);
      if (axis === "terms") return pick(T.termsPlain);
      return vals[0];
    }

    // theme.py resolve() 와 같은 순서: kind > arg > personal-audience > prefer > personal > audience > default
    function resolve(kind, auds, sets, personal) {
      const warns = [];
      const kspec = kind ? T.kinds[kind] : {};
      if (!auds.length && kspec.audience) auds = kspec.audience.slice();
      const pDef = personal.defaults || {};
      const pAud = personal.audiences || {};
      const prefer = (kind && T.prefer[kind]) || {};
      const out = {};
      for (const axis of T.axesOrder) {
        const fixed = kspec[axis];
        if (axis === "exposure") {
          let base = null, src = null;
          for (const [c, s] of [[fixed, "kind"], [fromAudiences(axis, auds, T.audiences), "audience"], [T.defaults[axis], "default"]]) {
            if (c) { base = c; src = s; break; }
          }
          for (const [c, s] of [[sets[axis], "arg"], [fromAudiences(axis, auds, pAud), "personal-audience"], [pDef[axis], "personal"]]) {
            if (!c || T.exposureStrict.indexOf(c) < 0) continue;
            if (T.exposureStrict.indexOf(c) < T.exposureStrict.indexOf(base)) { base = c; src = s; }
            else if (c !== base) warns.push(`공개 범위는 넓힐 수 없어 ${c} 대신 ${base} 를 씁니다`);
          }
          out[axis] = [base, src];
          continue;
        }
        if (fixed) {
          if (sets[axis] && sets[axis] !== fixed) warns.push(`${T.axes[axis].label} 은 문서 종류가 고정해 바꿀 수 없습니다`);
          out[axis] = [fixed, "kind"];
          continue;
        }
        const chain = [[sets[axis], "arg"], [fromAudiences(axis, auds, pAud), "personal-audience"], [prefer[axis], "prefer"],
          [pDef[axis], "personal"], [fromAudiences(axis, auds, T.audiences), "audience"], [T.defaults[axis], "default"]];
        for (const [c, s] of chain) {
          if (!c) continue;
          if (s.startsWith("personal") && !(c in T.axes[axis].values)) continue;
          out[axis] = [c, s];
          break;
        }
      }
      return { vals: out, auds, warns };
    }

    const SRC = { kind: "문서 종류가 고정", arg: "직접 고름", "personal-audience": "내 독자 설정", prefer: "문서 종류가 권함",
      personal: "내 기본값", audience: "독자", default: "기본 프리셋" };

    function label(axis, v) { return v === "template" ? "문서 종류의 틀" : (T.axes[axis].values[v] || v); }

    function compose(kind, auds, vals, chars, fmt, html) {
      const kindLabel = kind ? T.kinds[kind].label : "일반 글";
      const audLabel = auds.map((a) => T.audiences[a].label).join(", ") || "정하지 않음";
      const parts = [
        `# 글쓰기 테마 · ${kindLabel} · 독자 ${audLabel}`,
        "이 대화에서 쓰는 글에 아래 규칙을 적용한다. 규칙끼리 부딪치면 앞에 나온 규칙을 따른다. 이 지침은 geulot 로 조립했다.",
        "## 공통 바닥\n\n" + T.base,
      ];
      if (kind) parts.push(`## 문서 종류 · ${kindLabel}\n\n` + T.kindText[kind]);
      for (const axis of T.composeOrder) {
        const v = vals[axis][0];
        if (v === "template") continue;
        if (axis === "visual-deck" && kind !== "slides") continue;
        if (axis === "visual-doc" && !html) continue;
        parts.push(`## ${T.axes[axis].label} · ${label(axis, v)}\n\n` + T.rules[`${axis}/${v}`]);
        if (axis === "length" && chars) {
          parts.push(`## 글자수 · 공백 포함 ${chars}자 이내\n\n` +
            `- 본문은 공백 포함 ${chars}자를 넘기지 않는다. 넘치면 근거가 약한 문장부터 뺀다.\n` +
            "- 다 쓴 뒤 끝에 `(공백 포함 n자)` 로 센 값을 적는다.\n" +
            "- AI 가 센 글자수는 틀리기 쉽다. 제출 전에 글자수 세기 도구로 다시 잰다.");
        }
      }
      let text = parts.join("\n\n") + "\n";
      if (fmt === "output-style") {
        text = "---\n" + `name: ${kindLabel} (${audLabel})\n` +
          `description: geulot 로 조립한 글쓰기 테마. ${kindLabel}, 독자 ${audLabel}\n` +
          "keep-coding-instructions: true\n---\n\n" + text;
      }
      return text;
    }
    return { resolve, compose, label, SRC };
  }
  if (typeof module !== "undefined" && module.exports) module.exports = make;
  else root.ThemeCore = make;
})(typeof self !== "undefined" ? self : this);
