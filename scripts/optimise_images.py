"""
Optimise source images for the Sri Gaṇeśa GitHub Pages portal.

This module converts the project's original source images into web-ready
WebP assets while preserving the original files.

Directory flow:

    source-assets/images/
        ├── author/
        ├── book/
        └── iconography/
                │
                ▼
        scripts/optimise_images.py
                │
                ▼
    assets/images/
        ├── author/
        ├── book/
        └── iconography/

Design principles
-----------------
1. Original source images are never modified.
2. Source directory structure is mirrored in the output directory.
3. JPEG and PNG source images are converted to WebP.
4. Oversized images are resized before WebP conversion.
5. Images with transparency retain their alpha channel.
6. Existing generated files may be safely regenerated.
7. The script reports source size, output size, and reduction percentage.
8. The implementation uses Pillow rather than heavier image-processing
   frameworks because this project only requires straightforward web
   image optimisation.

Usage
-----

From the repository root:

    python scripts/optimise_images.py

Optional command-line arguments are available for changing the source,
output, quality, and maximum dimensions.

Examples:

    python scripts/optimise_images.py

    python scripts/optimise_images.py --quality 82

    python scripts/optimise_images.py --max-width 1600 --max-height 1600

    python scripts/optimise_images.py --quality 85 --max-width 1920

Requirements
------------

Pillow is required:

    python -m pip install Pillow

The script intentionally has no dependency on the web portal, XAMPP,
GitHub Pages, Bootstrap, or any other project component.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps, UnidentifiedImageError


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = SCRIPT_DIR.parent

SOURCE_ROOT = REPOSITORY_ROOT / "source-assets" / "images"
OUTPUT_ROOT = REPOSITORY_ROOT / "assets" / "images"


# ---------------------------------------------------------------------------
# Optimisation configuration
# ---------------------------------------------------------------------------

# WebP quality provides a practical balance between visual quality and file
# size. 82 is a good default for artwork and photographic material.
DEFAULT_QUALITY = 82

# Images larger than these dimensions are resized proportionally.
#
# We do not force small images to become larger. Upscaling would increase
# file size without adding meaningful visual information.
DEFAULT_MAX_WIDTH = 1920
DEFAULT_MAX_HEIGHT = 1920

# Source formats currently expected in the project.
SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}

# Output format for the web portal.
OUTPUT_EXTENSION = ".webp"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def format_bytes(size: int) -> str:
    """
    Convert a byte count into a human-readable size.

    Parameters
    ----------
    size:
        File size in bytes.

    Returns
    -------
    str
        Human-readable representation such as ``"842.3 KB"`` or
        ``"3.01 MB"``.
    """
    units = ("B", "KB", "MB", "GB")

    value = float(size)

    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"

        value /= 1024

    return f"{value:.2f} GB"


def calculate_reduction(source_size: int, output_size: int) -> float:
    """
    Calculate the percentage reduction achieved by optimisation.

    Parameters
    ----------
    source_size:
        Original file size in bytes.

    output_size:
        Optimised file size in bytes.

    Returns
    -------
    float
        Percentage reduction.

    Notes
    -----
    A negative value is possible when an output file is larger than the
    original. This is intentionally preserved in the calculation so that
    the optimisation report does not hide such cases.
    """
    if source_size == 0:
        return 0.0

    return ((source_size - output_size) / source_size) * 100


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------


def iter_source_images(source_root: Path) -> Iterable[Path]:
    """
    Yield supported image files beneath the source directory.

    The directory tree is searched recursively so that additional image
    categories can be added later without changing this script.

    Parameters
    ----------
    source_root:
        Root directory containing original images.

    Yields
    ------
    Path
        Each supported source image path, sorted for deterministic output.
    """
    for path in sorted(source_root.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def build_output_path(source_path: Path, source_root: Path) -> Path:
    """
    Build the corresponding WebP output path.

    The relative directory structure beneath ``source_root`` is preserved.

    Example
    -------
    ::

        source-assets/images/iconography/large-ears.jpg

    becomes:

        assets/images/iconography/large-ears.webp

    Parameters
    ----------
    source_path:
        Full path to the original source image.
    source_root:
        Root of the source image tree.

    Returns
    -------
    Path
        Corresponding output path.
    """
    relative_path = source_path.relative_to(source_root)
    output_relative_path = relative_path.with_suffix(OUTPUT_EXTENSION)

    return OUTPUT_ROOT / output_relative_path


def resize_if_needed(
    image: Image.Image,
    max_width: int,
    max_height: int,
) -> tuple[Image.Image, bool]:
    """
    Resize an image only when it exceeds the configured dimensions.

    Aspect ratio is preserved automatically.

    Smaller images are never upscaled.

    Parameters
    ----------
    image:
        Pillow image object.
    max_width:
        Maximum permitted width in pixels.
    max_height:
        Maximum permitted height in pixels.

    Returns
    -------
    tuple[Image.Image, bool]
        The processed image and a boolean indicating whether resizing
        occurred.
    """
    original_width, original_height = image.size

    if original_width <= max_width and original_height <= max_height:
        return image, False

    resized = image.copy()

    resized.thumbnail(
        (max_width, max_height),
        Image.Resampling.LANCZOS,
    )

    return resized, True


def prepare_image(
    image: Image.Image,
    max_width: int,
    max_height: int,
) -> tuple[Image.Image, bool]:
    """
    Prepare an image for WebP encoding.

    EXIF orientation is applied before resizing so that images captured or
    edited with orientation metadata are displayed correctly.

    Transparency is preserved for PNG images containing an alpha channel.

    Parameters
    ----------
    image:
        Source Pillow image.
    max_width:
        Maximum output width.
    max_height:
        Maximum output height.

    Returns
    -------
    tuple[Image.Image, bool]
        Prepared image and resize status.
    """
    corrected = ImageOps.exif_transpose(image)

    return resize_if_needed(
        corrected,
        max_width=max_width,
        max_height=max_height,
    )


def save_as_webp(
    image: Image.Image,
    output_path: Path,
    quality: int,
) -> None:
    """
    Save a prepared Pillow image as a WebP file.

    Parameters
    ----------
    image:
        Prepared Pillow image.
    output_path:
        Destination WebP file.
    quality:
        WebP quality from 1 to 100.

    Notes
    -----
    Images containing transparency are saved with their alpha channel
    intact. Images without transparency are saved in RGB mode where
    appropriate.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    has_alpha = (
        image.mode in {"RGBA", "LA"}
        or "transparency" in image.info
    )

    if has_alpha:
        prepared = image.convert("RGBA")
    else:
        prepared = image.convert("RGB")

    prepared.save(
        output_path,
        format="WEBP",
        quality=quality,
        method=6,
    )

    # Avoid retaining references to temporary converted image objects.
    if prepared is not image:
        prepared.close()


# ---------------------------------------------------------------------------
# Optimisation
# ---------------------------------------------------------------------------


def optimise_image(
    source_path: Path,
    source_root: Path,
    output_root: Path,
    quality: int,
    max_width: int,
    max_height: int,
) -> tuple[int, int, bool]:
    """
    Optimise one source image.

    Parameters
    ----------
    source_path:
        Path to the original image.
    source_root:
        Root directory containing original images.
    output_root:
        Root directory for generated images.
    quality:
        WebP quality from 1 to 100.
    max_width:
        Maximum output width.
    max_height:
        Maximum output height.

    Returns
    -------
    tuple[int, int, bool]
        Original size, output size, and resize status in that order.

    Raises
    ------
    OSError
        If the source image cannot be opened or the output cannot be saved.
    """
    output_path = (
        output_root
        / source_path.relative_to(source_root)
    ).with_suffix(OUTPUT_EXTENSION)

    source_size = source_path.stat().st_size

    try:
        with Image.open(source_path) as source_image:
            prepared_image, resized = prepare_image(
                source_image,
                max_width=max_width,
                max_height=max_height,
            )

            save_as_webp(
                prepared_image,
                output_path,
                quality=quality,
            )

            if prepared_image is not source_image:
                prepared_image.close()

    except (OSError, UnidentifiedImageError) as exc:
        raise OSError(
            f"Unable to process image: {source_path}"
        ) from exc

    output_size = output_path.stat().st_size

    return source_size, output_size, resized


def print_image_result(
    source_path: Path,
    source_root: Path,
    output_size: int,
    source_size: int,
    resized: bool,
) -> None:
    """
    Print a formatted result for one processed image.

    Parameters
    ----------
    source_path:
        Source image path.
    source_root:
        Root source directory.
    output_size:
        Optimised file size.
    source_size:
        Original file size.
    resized:
        Whether the image dimensions were reduced.
    """
    relative_path = source_path.relative_to(source_root)
    reduction = calculate_reduction(source_size, output_size)
    resize_marker = " [resized]" if resized else ""

    print(
        f"  {relative_path}{resize_marker}\n"
        f"      {format_bytes(source_size)}"
        f" -> {format_bytes(output_size)}"
        f"  ({reduction:.1f}% reduction)"
    )


def run_optimisation(
    source_root: Path,
    output_root: Path,
    quality: int,
    max_width: int,
    max_height: int,
) -> int:
    """
    Optimise all supported images beneath the source directory.

    Parameters
    ----------
    source_root:
        Root directory containing original images.
    output_root:
        Root directory for generated WebP assets.
    quality:
        WebP quality.
    max_width:
        Maximum output width.
    max_height:
        Maximum output height.

    Returns
    -------
    int
        Process exit code. ``0`` indicates success; ``1`` indicates that
        one or more images could not be processed.
    """
    if not source_root.exists():
        print(f"ERROR: Source directory does not exist: {source_root}")
        return 1

    source_images = list(iter_source_images(source_root))

    if not source_images:
        print(f"ERROR: No supported images found in: {source_root}")
        return 1

    output_root.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 72)
    print("Sri Gaṇeśa Portal — Image Optimisation")
    print("=" * 72)
    print(f"Source : {source_root}")
    print(f"Output : {output_root}")
    print(f"Quality: {quality}")
    print(
        f"Maximum dimensions: {max_width} x {max_height} px"
    )
    print(f"Images found: {len(source_images)}")
    print("=" * 72)

    total_source_size = 0
    total_output_size = 0
    processed_count = 0
    failed_count = 0
    resized_count = 0

    for source_path in source_images:
        try:
            source_size, output_size, resized = optimise_image(
                source_path=source_path,
                source_root=source_root,
                output_root=output_root,
                quality=quality,
                max_width=max_width,
                max_height=max_height,
            )

            total_source_size += source_size
            total_output_size += output_size
            processed_count += 1

            if resized:
                resized_count += 1

            print_image_result(
                source_path=source_path,
                source_root=source_root,
                source_size=source_size,
                output_size=output_size,
                resized=resized,
            )

        except OSError as exc:
            failed_count += 1
            print(f"\n  ERROR: {exc}")

    total_reduction = calculate_reduction(
        total_source_size,
        total_output_size,
    )

    print()
    print("=" * 72)
    print("Optimisation Summary")
    print("=" * 72)
    print(f"Processed : {processed_count}")
    print(f"Resized   : {resized_count}")
    print(f"Failed    : {failed_count}")
    print(f"Original  : {format_bytes(total_source_size)}")
    print(f"Web-ready : {format_bytes(total_output_size)}")
    print(f"Reduction : {total_reduction:.1f}%")
    print("=" * 72)
    print()

    return 1 if failed_count else 0


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed command-line configuration.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Convert Sri Gaṇeśa portal source images "
            "to optimised WebP assets."
        )
    )

    parser.add_argument(
        "--quality",
        type=int,
        default=DEFAULT_QUALITY,
        help=(
            "WebP quality from 1 to 100 "
            f"(default: {DEFAULT_QUALITY})."
        ),
    )

    parser.add_argument(
        "--max-width",
        type=int,
        default=DEFAULT_MAX_WIDTH,
        help=(
            "Maximum output width in pixels "
            f"(default: {DEFAULT_MAX_WIDTH})."
        ),
    )

    parser.add_argument(
        "--max-height",
        type=int,
        default=DEFAULT_MAX_HEIGHT,
        help=(
            "Maximum output height in pixels "
            f"(default: {DEFAULT_MAX_HEIGHT})."
        ),
    )

    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """
    Validate command-line configuration.

    Parameters
    ----------
    args:
        Parsed command-line arguments.

    Raises
    ------
    ValueError
        If any supplied optimisation setting is invalid.
    """
    if not 1 <= args.quality <= 100:
        raise ValueError(
            "Quality must be between 1 and 100."
        )

    if args.max_width <= 0:
        raise ValueError(
            "Maximum width must be greater than zero."
        )

    if args.max_height <= 0:
        raise ValueError(
            "Maximum height must be greater than zero."
        )


def main() -> int:
    """
    Execute the image optimisation command.

    Returns
    -------
    int
        Process exit code.
    """
    args = parse_arguments()
    validate_arguments(args)

    return run_optimisation(
        source_root=SOURCE_ROOT,
        output_root=OUTPUT_ROOT,
        quality=args.quality,
        max_width=args.max_width,
        max_height=args.max_height,
    )


if __name__ == "__main__":
    raise SystemExit(main())