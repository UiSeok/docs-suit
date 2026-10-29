#!/usr/bin/env python3
"""readme-art.py: README 에 싣는 캐릭터 그림을 SVG 로 만든다.

엔진 suit.py 의 look_of 와 look_grid 로 그려서 상태 줄과 웹 화면의 캐릭터와 같은 그림이 나온다. 윗줄은 직장인이
사원에서 부장까지 전직하며 꾸미기를 여는 모습이고, 아랫줄은 클래스마다 4차 전직까지 연 모습이다. 부품이나
look.yaml 의 보상을 바꾸면 다시 돌린다.

  python3 tools/readme-art.py            docs/readme/characters.svg 를 다시 쓴다
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "readme" / "characters.svg"
PX = 5  # 도트 한 칸의 크기
CELL = 116  # 캐릭터 한 명이 차지하는 너비
GROW = "office"  # 윗줄에서 전직을 보여 줄 클래스


def load_suit():
    spec = importlib.util.spec_from_file_location("suit", ROOT / "suit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sprite(grid, x0, y0):
    """색 격자를 rect 로 옮긴다. 같은 색이 가로로 이어지면 한 rect 로 합친다."""
    out = []
    for y, row in enumerate(grid):
        x = 0
        while x < len(row):
            c = row[x]
            run = 1
            while x + run < len(row) and row[x + run] == c:
                run += 1
            if c:
                out.append(f'<rect x="{x0 + x * PX}" y="{y0 + y * PX}" width="{run * PX}" height="{PX}" fill="{c}"/>')
            x += run
    return out


def text(x, y, body, size, color, weight="normal"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="middle">{body}</text>')


def figure(suit, th, cls, tier, hair, x, y, caption, sub):
    look = suit.look_of(th, {"profile": {"class": cls}, "look": {"hair": hair}}, tier)
    grid = suit.look_grid(th, look)
    w = len(grid[0]) * PX
    out = sprite(grid, x + (CELL - w) // 2, y)
    out.append(text(x + CELL // 2, y + len(grid) * PX + 22, caption, 15, "#2b1d16", "bold"))
    out.append(text(x + CELL // 2, y + len(grid) * PX + 40, sub, 12, "#7a6a5c"))
    return out


def main():
    suit = load_suit()
    th = suit.Themes(suit.themes_root())
    hairs = list(th.look["hair"])
    classes = list(th.classes)
    width = CELL * len(classes) + 40
    body = []

    titles = th.classes[GROW]["titles"]
    left = (width - CELL * len(titles)) // 2
    body.append(text(width // 2, 34, f"글을 쓸수록 전직합니다 · {th.classes[GROW]['label']}", 16, "#2b1d16", "bold"))
    for t, title in enumerate(titles):
        sub = "처음" if t == 0 else f"{t}차 전직"
        body += figure(suit, th, GROW, t, "short", left + t * CELL, 54, title, sub)

    body.append(text(width // 2, 296, "클래스마다 여는 옷과 소품이 다릅니다 · 4차 전직", 16, "#2b1d16", "bold"))
    for i, cls in enumerate(classes):
        meta = th.classes[cls]
        body += figure(suit, th, cls, len(meta["titles"]) - 1, hairs[i % len(hairs)], 20 + i * CELL, 316,
                       meta["label"], meta["titles"][-1])

    height = 316 + 24 * PX + 56
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
           'shape-rendering="crispEdges" font-family="-apple-system, \'Apple SD Gothic Neo\', \'Malgun Gothic\', '
           '\'Noto Sans KR\', sans-serif">',
           "<!-- tools/readme-art.py 가 만든다. 손으로 고치지 않는다 -->",
           f'<rect width="{width}" height="{height}" rx="14" fill="#fdf8ef"/>'] + body + ["</svg>"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)} 를 썼다")


if __name__ == "__main__":
    main()
