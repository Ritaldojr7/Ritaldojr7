#!/usr/bin/env python3
"""Prepare a portrait photo for ASCII conversion: remove bg, white canvas, CLAHE."""

from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path: Path, output_path: Path = Path("source-prepped.png")) -> Path:
    if not input_path.is_file():
        raise FileNotFoundError(f"Image not found: {input_path}")

    with input_path.open("rb") as handle:
        cutout = remove(handle.read())

    subject = Image.open(BytesIO(cutout)).convert("RGBA")
    canvas = Image.new("RGBA", subject.size, (255, 255, 255, 255))
    composite = Image.alpha_composite(canvas, subject)

    gray = cv2.cvtColor(np.array(composite.convert("RGB")), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(output_path)
    return output_path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/prep_photo.py <image_path>", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = prep_photo(input_path)
    print(f"Prepared {output_path} from {input_path}")


if __name__ == "__main__":
    main()
