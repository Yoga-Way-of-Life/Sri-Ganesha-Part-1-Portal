#!/usr/bin/env python3
"""
Sri Gaṇeśa — Part 1 Portal
Single Image Optimiser

Purpose:
    Convert one source image into a web-ready WebP asset.

Usage:
    python scripts/image_optimizer.py <filename.extension>

Example:
    python scripts/image_optimizer.py sri-ganesh-panoramic-1.jfif

Input:
    source-assets/images/<filename>

Output:
    assets/images/<filename>.webp

Design principle:
    Keep source assets untouched.
    Generate optimised web assets separately.

Project philosophy:
    Clean, green and lean engineering.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_ROOT / "source-assets" / "images"
OUTPUT_DIR = PROJECT_ROOT / "assets" / "images"

DEFAULT_QUALITY = 82
MAX_SIZE = (1920, 1920)

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".jfif",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


def format_size(size_bytes: int) -> str:
    """Return a human-readable file size."""
    size = float(size_bytes)

    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} TB"


def optimise_image(source_path: Path, output_path: Path) -> None:
    """Convert one source image to an optimised WebP image."""
    original_size = source_path.stat().st_size

    with Image.open(source_path) as image:
        print(f"Input:  {source_path}")
        print(f"Format: {image.format}")
        print(f"Size:   {image.width} x {image.height}")

        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")

        original_dimensions = image.size
        image.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)

        if image.size != original_dimensions:
            print(
                f"Resize: {original_dimensions[0]} x "
                f"{original_dimensions[1]} → "
                f"{image.width} x {image.height}"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        image.save(
            output_path,
            "WEBP",
            quality=DEFAULT_QUALITY,
            method=6,
        )

    final_size = output_path.stat().st_size
    reduction = (1 - final_size / original_size) * 100

    print()
    print(f"Output: {output_path}")
    print(f"Original: {format_size(original_size)}")
    print(f"WebP:    {format_size(final_size)}")
    print(f"Reduced: {reduction:.1f}%")
    print()
    print("Image optimisation completed.")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert one source image to an optimised WebP asset."
    )

    parser.add_argument(
        "filename",
        help="Source filename located in source-assets/images/",
    )

    return parser.parse_args()


def main() -> int:
    """Run the image optimisation utility."""
    args = parse_arguments()

    filename = Path(args.filename)

    if filename.name != args.filename:
        print(
            "Error: provide only the filename, not a directory path.",
            file=sys.stderr,
        )
        return 1

    if filename.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        print(
            f"Error: unsupported image type '{filename.suffix}'.",
            file=sys.stderr,
        )
        print(f"Supported types: {supported}", file=sys.stderr)
        return 1

    source_path = SOURCE_DIR / filename.name
    output_path = OUTPUT_DIR / f"{filename.stem}.webp"

    if not source_path.is_file():
        print(
            f"Error: source image not found:\n{source_path}",
            file=sys.stderr,
        )
        return 1

    if output_path.exists():
        print(
            f"Error: output already exists:\n{output_path}",
            file=sys.stderr,
        )
        print(
            "Delete the existing WebP first if you want to regenerate it.",
            file=sys.stderr,
        )
        return 1

    try:
        optimise_image(source_path, output_path)
    except Exception as exc:
        print(
            f"Error: image optimisation failed: {exc}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())