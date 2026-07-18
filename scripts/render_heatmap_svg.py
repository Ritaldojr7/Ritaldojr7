#!/usr/bin/env python3
"""Render an animated GitHub-style contribution heatmap SVG."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

DATA_PATH = Path("data/contributions.json")
OUTPUT_PATH = Path("contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BOX = 12
GAP = 3
WEEKS = 53
DAYS = 7
BG = "#0d1117"
PADDING = 20
LEGEND_GAP = 24
FOOTER_H = 28
ANIM_DUR = 0.35
ANIM_BASE = 0.02


def load_data() -> dict:
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def color_for_level(level: int) -> str:
    idx = max(0, min(len(PALETTE) - 1, level))
    return PALETTE[idx]


def build_grid(days: list[dict]) -> list[list[dict | None]]:
    if not days:
        return [[None for _ in range(DAYS)] for _ in range(WEEKS)]

    by_date = {item["date"]: item for item in days}
    sorted_dates = sorted(by_date)
    start = date.fromisoformat(sorted_dates[0])
    end = date.fromisoformat(sorted_dates[-1])

    # Align to the Sunday that starts the first week column.
    start_sunday = start - timedelta(days=(start.weekday() + 1) % 7)

    grid: list[list[dict | None]] = [[None for _ in range(DAYS)] for _ in range(WEEKS)]
    cursor = start_sunday

    for week in range(WEEKS):
        for weekday in range(DAYS):
            iso = cursor.isoformat()
            if start <= cursor <= end and iso in by_date:
                grid[week][weekday] = by_date[iso]
            cursor += timedelta(days=1)

    return grid


def build_svg(payload: dict) -> str:
    grid = build_grid(payload["days"])
    total = payload.get("total", 0)

    grid_w = WEEKS * BOX + (WEEKS - 1) * GAP
    grid_h = DAYS * BOX + (DAYS - 1) * GAP
    svg_w = PADDING * 2 + grid_w
    svg_h = PADDING * 2 + grid_h + LEGEND_GAP + FOOTER_H

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}" role="img" '
        f'aria-label="Contribution heatmap for the last year">',
        "<defs>",
        "<style><![CDATA[",
        "@keyframes heatmap-reveal {",
        "  from { opacity: 0; transform: translateY(-10px); }",
        "  to { opacity: 1; transform: translateY(0); }",
        "}",
        ".contrib-box {",
        f"  animation: heatmap-reveal {ANIM_DUR}s ease-out forwards;",
        "  opacity: 0;",
        "}",
        "]]></style>",
        "</defs>",
        f'<rect width="{svg_w}" height="{svg_h}" fill="{BG}"/>',
    ]

    origin_x = PADDING
    origin_y = PADDING

    for week in range(WEEKS):
        for weekday in range(DAYS):
            cell = grid[week][weekday]
            if cell is None:
                continue

            x = origin_x + week * (BOX + GAP)
            y = origin_y + weekday * (BOX + GAP)
            delay = (week + weekday) * ANIM_BASE
            fill = color_for_level(int(cell.get("level", 0)))

            lines.append(
                f'<rect class="contrib-box" x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                f'rx="2.5" ry="2.5" fill="{fill}" '
                f'style="animation-delay: {delay:.2f}s;" '
                f'data-date="{cell["date"]}" data-count="{cell["count"]}"/>'
            )

    legend_y = origin_y + grid_h + LEGEND_GAP
    legend_x = origin_x
    lines.append(
        f'<text x="{legend_x}" y="{legend_y + 10}" fill="#8b949e" '
        f'font-family="ui-monospace, monospace" font-size="11">Less</text>'
    )

    swatch_x = legend_x + 34
    for index in range(5):
        x = swatch_x + index * (BOX + GAP)
        lines.append(
            f'<rect x="{x}" y="{legend_y}" width="{BOX}" height="{BOX}" '
            f'rx="2.5" ry="2.5" fill="{PALETTE[index]}"/>'
        )

    more_x = swatch_x + 5 * (BOX + GAP) + 8
    lines.append(
        f'<text x="{more_x}" y="{legend_y + 10}" fill="#8b949e" '
        f'font-family="ui-monospace, monospace" font-size="11">More</text>'
    )

    footer = f"{total:,} contributions in the last year"
    lines.append(
        f'<text x="{svg_w - PADDING}" y="{svg_h - 8}" fill="#8b949e" '
        f'text-anchor="end" font-family="ui-monospace, monospace" font-size="11">{footer}</text>'
    )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main() -> None:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run scripts/fetch_contributions.py first."
        )

    payload = load_data()
    OUTPUT_PATH.write_text(build_svg(payload), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(payload.get('days', []))} days, total={payload.get('total', 0):,})")


if __name__ == "__main__":
    main()
