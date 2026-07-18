#!/usr/bin/env python3
"""Generate a neofetch-style animated info card SVG."""

from __future__ import annotations

import os
from pathlib import Path

# --- edit these placeholders freely ---
TITLE = "Ritaldojr7 @github"
ROWS = [
    ("Now", "Building animated profile READMEs", "#79c0ff"),
    ("Prev", "Full-stack & automation projects", "#ffa657"),
    ("Stack", "Python · TypeScript · Docker · n8n", "#7ee787"),
    ("Editor", "Cursor + Neovim", "#d2a8ff"),
    ("Highlights", "Open source · CI/CD · workflows", "#ff7b72"),
    ("Contact", "ritaldojr7@users.noreply.github.com", "#a5d6ff"),
]

CARD_W = 490
CARD_H = 300
PANEL_X = 8
PANEL_Y = 8
PANEL_W = CARD_W - 16
PANEL_H = CARD_H - 16
BG = "#0d1117"
BORDER = "#30363d"
VALUE_FILL = "#c9d1d9"
FONT = "ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace"
ROW_START_Y = 92
ROW_STEP = 28
ROW_DUR = 0.45
ROW_STAGGER = 0.12


def escape_text(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;")


def static_mode() -> bool:
    return os.environ.get("STATIC", "").strip() in {"1", "true", "True", "yes", "YES"}


def row_animation(index: int) -> tuple[str, str]:
    if static_mode():
        return ("", "")

    begin = 0.35 + index * ROW_STAGGER
    opacity_anim = (
        f'<animate attributeName="opacity" from="0" to="1" '
        f'dur="{ROW_DUR}s" begin="{begin:.2f}s" fill="freeze"/>'
    )
    slide_anim = (
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="-16 0" to="0 0" dur="{ROW_DUR}s" begin="{begin:.2f}s" fill="freeze"/>'
    )
    return (opacity_anim, slide_anim)


def build_svg() -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" '
        f'viewBox="0 0 {CARD_W} {CARD_H}" role="img" aria-label="Profile info card">',
        f'<rect width="{CARD_W}" height="{CARD_H}" fill="{BG}"/>',
        f'<rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" '
        f'rx="14" ry="14" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>',
        '<circle cx="28" cy="28" r="5.5" fill="#ff5f57"/>',
        '<circle cx="48" cy="28" r="5.5" fill="#febc2e"/>',
        '<circle cx="68" cy="28" r="5.5" fill="#28c840"/>',
        f'<text x="28" y="58" fill="{VALUE_FILL}" font-family="{FONT}" '
        f'font-size="15" font-weight="700">{escape_text(TITLE)}</text>',
        f'<line x1="28" y1="68" x2="{CARD_W - 28}" y2="68" stroke="{BORDER}" stroke-width="1"/>',
    ]

    for index, (key, value, key_color) in enumerate(ROWS):
        y = ROW_START_Y + index * ROW_STEP
        opacity_anim, slide_anim = row_animation(index)
        group_open = '<g opacity="0">' if not static_mode() else "<g>"
        lines.append(group_open)
        if not static_mode():
            lines.append(f"  {opacity_anim}")
            lines.append(f"  {slide_anim}")
        lines.extend(
            [
                f'  <text x="28" y="{y}" fill="{key_color}" font-family="{FONT}" '
                f'font-size="13" font-weight="700">{escape_text(key)}</text>',
                f'  <text x="130" y="{y}" fill="{VALUE_FILL}" font-family="{FONT}" '
                f'font-size="13">{escape_text(value)}</text>',
                "</g>",
            ]
        )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main() -> None:
    output = Path("info-card.svg")
    output.write_text(build_svg(), encoding="utf-8")
    mode = "static" if static_mode() else "animated"
    print(f"Wrote {output} ({mode})")


if __name__ == "__main__":
    main()
