// 웹 판 써 보기의 머리 맵. 풀밭에 기와집과 돌담, 나무를 두고, 아래 두 줄은 캐릭터가 서는 돌길이다.
// 타일은 16칸 격자로 그려 3배로 키운다. 그림은 이 저장소에서 새로 그렸다.
(function () {
  "use strict";
  const S = 3, T = 16;
  function rng(seed) { return () => ((seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff); }

  function draw() {
    const cv = document.getElementById("scene");
    if (!cv) return;
    const w = cv.parentElement.clientWidth, h = cv.parentElement.clientHeight;
    const cols = Math.ceil(w / (T * S)) + 1, rows = Math.ceil(h / (T * S));
    cv.width = cols * T; cv.height = rows * T;
    cv.style.width = cols * T * S + "px"; cv.style.height = rows * T * S + "px";
    const g = cv.getContext("2d");
    g.clearRect(0, 0, cv.width, cv.height);
    const px = (x, y, c) => { g.fillStyle = c; g.fillRect(x, y, 1, 1); };
    const rect = (x, y, ww, hh, c) => { g.fillStyle = c; g.fillRect(x, y, ww, hh); };
    const r = rng(7);
    const roadTop = (rows - 2) * T;

    // 풀밭
    rect(0, 0, cols * T, roadTop, "#6aa84f");
    for (let i = 0; i < cols * rows * 10; i++) {
      const x = Math.floor(r() * cols * T), y = Math.floor(r() * roadTop);
      px(x, y, r() < .5 ? "#5a9442" : "#82c063");
      if (r() < .3) px(x, y - 1, "#5a9442");
    }
    // 꽃
    for (let i = 0; i < cols * 2; i++) {
      const x = Math.floor(r() * cols * T), y = Math.floor(r() * (roadTop - 6)) + 3;
      const c = ["#f4d35e", "#f28c8c", "#ffffff"][i % 3];
      px(x, y, c); px(x - 1, y + 1, c); px(x + 1, y + 1, c); px(x, y + 2, c); px(x, y + 1, "#e07a2f");
    }

    // 돌길: 테두리 돌과 자갈
    rect(0, roadTop, cols * T, 2 * T, "#c8ab7a");
    rect(0, roadTop, cols * T, 2, "#8a7350");
    for (let x = 0; x < cols * T; x += 8) {
      const y0 = roadTop + 4 + Math.floor(r() * 18);
      rect(x + Math.floor(r() * 4), y0, 4, 3, "#b39461");
      px(x + 1, y0 + 3, "#a3844f");
    }

    // 기와집
    function house(x0, y0) {
      const k = "#2a2420";
      // 지붕: 처마 끝이 위로 들린다
      for (let y = 0; y < 10; y++) {
        const inset = Math.max(0, 9 - y);
        for (let x = inset; x < 36 - inset; x++) px(x0 + x, y0 + y, (x % 3 === 0) ? "#3e4a5c" : "#56647a");
        px(x0 + inset, y0 + y, k); px(x0 + 35 - inset, y0 + y, k);
      }
      rect(x0 + 9, y0, 18, 1, k);
      rect(x0 - 2, y0 + 10, 40, 2, k);
      px(x0 - 2, y0 + 9, k); px(x0 - 3, y0 + 8, k); px(x0 + 37, y0 + 9, k); px(x0 + 38, y0 + 8, k);
      // 벽과 기둥, 문, 창살
      rect(x0 + 2, y0 + 12, 32, 12, "#efe6cf");
      for (const x of [2, 12, 23, 33]) rect(x0 + x, y0 + 12, 2, 12, "#7a4b2a");
      rect(x0 + 15, y0 + 14, 6, 10, "#8b5a33");
      for (let y = 15; y < 24; y += 3) rect(x0 + 15, y0 + y, 6, 1, "#5a3a22");
      rect(x0 + 5, y0 + 15, 5, 5, "#d9c9a3");
      rect(x0 + 7, y0 + 15, 1, 5, "#7a4b2a"); rect(x0 + 5, y0 + 17, 5, 1, "#7a4b2a");
      rect(x0 + 26, y0 + 15, 5, 5, "#d9c9a3");
      rect(x0 + 28, y0 + 15, 1, 5, "#7a4b2a"); rect(x0 + 26, y0 + 17, 5, 1, "#7a4b2a");
      // 기단
      rect(x0, y0 + 24, 36, 3, "#9b9486");
      for (let x = 0; x < 36; x += 6) px(x0 + x, y0 + 25, "#6f695e");
    }

    function tree(x0, y0) {
      rect(x0 + 6, y0 + 12, 4, 8, "#6b4426");
      px(x0 + 6, y0 + 19, "#4d3019");
      for (let y = 0; y < 14; y++) for (let x = 0; x < 16; x++) {
        const dx = x - 7.5, dy = y - 6.5;
        const d = dx * dx + dy * dy;
        if (d < 52) px(x0 + x, y0 + y, d > 40 ? "#2f6b33" : (dx + dy < -4 ? "#5fae54" : "#3f8a3f"));
      }
    }

    // 돌담
    function wall(x0, y0, len) {
      for (let x = 0; x < len; x += 5) {
        rect(x0 + x, y0, 5, 4, "#a59d8f"); rect(x0 + x, y0, 1, 4, "#6f695e"); rect(x0 + x, y0 + 3, 5, 1, "#6f695e");
        rect(x0 + x + 2, y0 + 4, 5, 4, "#b6ae9f"); rect(x0 + x + 2, y0 + 7, 5, 1, "#6f695e");
      }
      rect(x0, y0 - 2, len + 2, 2, "#4a5a3e");
    }

    const W = cols * T;
    house(8, 17);
    wall(52, roadTop - 9, Math.floor(W * .3));
    tree(W - 24, 2); tree(W - 46, 10); tree(Math.floor(W * .55), 0);
  }

  window.addEventListener("load", draw);
  window.addEventListener("resize", draw);
})();
