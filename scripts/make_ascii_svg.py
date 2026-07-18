#!/usr/bin/env python3
"""Convert source-prepped.png into an animated ASCII-art SVG."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"
SVG_W = 370
SVG_H = 300
ROWS = 64
# Monospace glyphs render ~0.6x as wide as tall; sample the image to match so
# the portrait keeps its real proportions instead of getting squeezed.
CELL_ASPECT = 0.60
FILL = "#c9d1d9"
BG = "#0d1117"
FONT = "ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace"
ROW_STAGGER = 0.045
REVEAL_DUR = 0.35
CROP_THRESHOLD = 248
CROP_PAD_RATIO = 0.03


def escape_text(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;")


def pixel_to_char(value: int) -> str:
    idx = round((255 - value) / 255 * (len(RAMP) - 1))
    idx = max(0, min(len(RAMP) - 1, idx))
    return RAMP[idx]


def crop_to_subject(image: Image.Image) -> Image.Image:
    pixels = np.array(image.convert("L"))
    mask = pixels < CROP_THRESHOLD
    if not mask.any():
        return image.convert("L")

    ys, xs = np.where(mask)
    pad = max(4, int(min(image.width, image.height) * CROP_PAD_RATIO))
    left = max(0, int(xs.min()) - pad)
    top = max(0, int(ys.min()) - pad)
    right = min(image.width, int(xs.max()) + pad + 1)
    bottom = min(image.height, int(ys.max()) + pad + 1)
    return image.convert("L").crop((left, top, right, bottom))


def compute_geometry(image_aspect: float) -> dict:
    """Fit an aspect-correct ASCII block inside the fixed canvas and center it."""
    canvas_aspect = SVG_W / SVG_H
    if image_aspect > canvas_aspect:
        block_w = float(SVG_W)
        block_h = block_w / image_aspect
    else:
        block_h = float(SVG_H)
        block_w = block_h * image_aspect

    char_h = block_h / ROWS
    char_w = char_h * CELL_ASPECT
    cols = max(1, round(block_w / char_w))
    block_w = cols * char_w  # snap block width to a whole number of columns

    return {
        "cols": cols,
        "char_w": char_w,
        "char_h": char_h,
        "block_w": block_w,
        "block_h": block_h,
        "offset_x": (SVG_W - block_w) / 2,
        "offset_y": (SVG_H - block_h) / 2,
    }


def load_grid(source: Path) -> tuple[list[str], dict]:
    image = Image.open(source)
    cropped = crop_to_subject(image)
    geom = compute_geometry(cropped.width / cropped.height)

    resized = cropped.resize((geom["cols"], ROWS), Image.Resampling.LANCZOS)
    pixels = np.array(resized)

    rows = ["".join(pixel_to_char(int(p)) for p in row) for row in pixels]
    return rows, geom


def build_svg(rows: list[str], geom: dict) -> str:
    block_w = geom["block_w"]
    char_h = geom["char_h"]
    font_size = char_h
    offset_x = geom["offset_x"]
    offset_y = geom["offset_y"]

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" '
        f'viewBox="0 0 {SVG_W} {SVG_H}" role="img" aria-label="ASCII portrait">',
        f'<rect width="{SVG_W}" height="{SVG_H}" fill="{BG}"/>',
        "<defs>",
        "  <style><![CDATA[",
        "    @keyframes row-reveal {",
        "      from { width: 0; }",
        f"      to {{ width: {block_w:.2f}px; }}",
        "    }",
        "    .reveal {",
        f"      animation: row-reveal {REVEAL_DUR}s ease-out both;",
        f"      width: {block_w:.2f}px;",
        "    }",
        "  ]]></style>",
    ]

    for index in range(len(rows)):
        y = offset_y + index * char_h
        begin = index * ROW_STAGGER
        lines.extend(
            [
                f'  <clipPath id="row-clip-{index}" clipPathUnits="userSpaceOnUse">',
                f'    <rect class="reveal" x="{offset_x:.2f}" y="{y:.2f}" '
                f'width="{block_w:.2f}" height="{char_h:.2f}" '
                f'style="animation-delay:{begin:.2f}s"/>',
                "  </clipPath>",
            ]
        )

    lines.append("</defs>")

    for index, row in enumerate(rows):
        y_text = offset_y + (index + 1) * char_h - char_h * 0.18
        safe = escape_text(row)
        lines.append(
            f'<text x="{offset_x:.2f}" y="{y_text:.2f}" fill="{FILL}" '
            f'font-family="{FONT}" font-size="{font_size:.2f}" '
            f'textLength="{block_w:.2f}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve" clip-path="url(#row-clip-{index})">{safe}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main() -> None:
    source = Path("source-prepped.png")
    output = Path("avi-ascii.svg")

    if not source.is_file():
        raise FileNotFoundError(
            "source-prepped.png not found. Run scripts/prep_photo.py on your photo first."
        )

    rows, geom = load_grid(source)
    output.write_text(build_svg(rows, geom), encoding="utf-8")
    print(
        f"Wrote {output} ({geom['cols']}x{ROWS} grid, {SVG_W}x{SVG_H}px, "
        f"{len(rows)} animated rows)"
    )


if __name__ == "__main__":
    main()
