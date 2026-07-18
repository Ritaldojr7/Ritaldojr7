# Setup

Build the animated GitHub profile README for **Ritaldojr7**. All animation lives inside the SVG files (SMIL + CSS keyframes) so GitHub can render it safely.

## Prerequisites

- macOS/Linux with **Python 3** (`python3` on macOS)
- A portrait photo named `source-photo.jpg` in the repo root (for the ASCII art)

## One-time portrait pipeline

Install the heavy image dependencies once:

```bash
python3 -m pip install -r scripts/requirements.txt
```

Then run the portrait scripts in order:

```bash
python3 scripts/prep_photo.py source-photo.jpg
python3 scripts/make_ascii_svg.py
python3 scripts/make_info_card.py
```

`prep_photo.py` writes `source-prepped.png`. `make_ascii_svg.py` writes `avi-ascii.svg`. `make_info_card.py` writes `info-card.svg`.

For a non-animated local preview of the info card:

```bash
STATIC=1 python3 scripts/make_info_card.py
```

## Contribution heatmap (local)

These scripts only need `requests` and `beautifulsoup4`:

```bash
python3 -m pip install requests==2.32.3 beautifulsoup4==4.12.3
python3 scripts/fetch_contributions.py
python3 scripts/render_heatmap_svg.py
```

That produces `data/contributions.json` and `contrib-heatmap.svg`.

## Publish

```bash
git add .
git commit -m "feat: add animated profile README"
git push origin main
```

After pushing, open **Actions → Update profile art → Run workflow** once to verify the daily cron job. The workflow refreshes `data/contributions.json` and `contrib-heatmap.svg` every day at 06:17 UTC.

## Edit placeholders

Open `scripts/make_info_card.py` and edit the `TITLE` and `ROWS` constants at the top, then re-run `make_info_card.py`.
