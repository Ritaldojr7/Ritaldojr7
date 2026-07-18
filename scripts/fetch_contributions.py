#!/usr/bin/env python3
"""Fetch public contribution calendar data without a GitHub token."""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER = "Ritaldojr7"
URL = f"https://github.com/users/{USER}/contributions"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
}
OUTPUT = Path("data/contributions.json")


def parse_count(tooltip_text: str) -> int:
    text = tooltip_text.strip()
    if not text or "no contributions" in text.lower():
        return 0
    match = re.match(r"(\d+)", text)
    return int(match.group(1)) if match else 0


def compute_streaks(days: list[dict]) -> tuple[int, int]:
    if not days:
        return 0, 0

    sorted_days = sorted(days, key=lambda item: item["date"])
    longest = 0
    current_run = 0

    for item in sorted_days:
        if item["count"] > 0:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 0

    current = 0
    for item in reversed(sorted_days):
        if item["count"] > 0:
            current += 1
        else:
            break

    return current, longest


def compute_best_day(days: list[dict]) -> dict | None:
    if not days:
        return None
    return max(days, key=lambda item: item["count"])


def fetch_contributions() -> dict:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    tips_by_target: dict[str, str] = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        if target:
            tips_by_target[target] = tip.get_text(" ", strip=True)

    days: list[dict] = []
    for cell in soup.select("td.ContributionCalendar-day"):
        day = cell.get("data-date")
        if not day:
            continue

        level_raw = cell.get("data-level", "0")
        try:
            level = int(level_raw)
        except ValueError:
            level = 0

        cell_id = cell.get("id", "")
        count = parse_count(tips_by_target.get(cell_id, ""))

        days.append({"date": day, "count": count, "level": level})

    days.sort(key=lambda item: item["date"])
    total = sum(item["count"] for item in days)
    current_streak, longest_streak = compute_streaks(days)
    best_day = compute_best_day(days)

    payload = {
        "user": USER,
        "generated": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "days": days,
    }
    return payload


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    try:
        payload = fetch_contributions()
    except requests.RequestException as exc:
        print(f"Failed to fetch contributions: {exc}", file=sys.stderr)
        sys.exit(1)

    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {OUTPUT}: {payload['total']:,} contributions across "
        f"{len(payload['days'])} days"
    )


if __name__ == "__main__":
    main()
