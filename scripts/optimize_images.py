#!/usr/bin/env python3
"""Optimize book images for web delivery.

By default, the script optimizes the local image files in place. This keeps the
git repository small: ``content.json`` preserves the source URL and license
metadata, while ``books/{slug}/images`` contains the chosen project copy.

Use ``--derivatives`` to preserve local files and write optimized browser-facing
assets under ``books/{slug}/images/optimized``. In that mode the script also
writes a manifest used by the site builder to swap image paths at render time.

Usage:
    python scripts/optimize_images.py --slug frogs
    python scripts/optimize_images.py --slug frogs --max-width 2200 --quality 84
    python scripts/optimize_images.py --slug frogs --derivatives
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover - exercised only when dependency missing
    Image = None
    ImageOps = None


REPO_ROOT = Path(__file__).resolve().parents[1]
RASTER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
COPY_EXTENSIONS = {".svg"}


def fail_if_pillow_missing() -> None:
    if Image is None or ImageOps is None:
        sys.exit(
            "Error: Pillow is required for image optimization. "
            "Install dependencies with: pip install -r site-builder/requirements.txt"
        )


def collect_book_image_paths(book: dict) -> list[str]:
    """Return unique image paths referenced by book.json, preserving order."""
    paths: list[str] = []
    cover_image = book.get("cover", {}).get("image")
    if cover_image:
        paths.append(cover_image)

    for page in book.get("pages", []):
        for image in page.get("images", []):
            src = image.get("src")
            if src:
                paths.append(src)

    seen = set()
    unique_paths = []
    for path in paths:
        if path not in seen:
            unique_paths.append(path)
            seen.add(path)
    return unique_paths


def collect_content_image_paths(content: dict) -> list[str]:
    """Return unique image paths referenced by content.json, preserving order."""
    paths = [image.get("filename") for image in content.get("images", []) if image.get("filename")]
    seen = set()
    unique_paths = []
    for path in paths:
        if path not in seen:
            unique_paths.append(path)
            seen.add(path)
    return unique_paths


def optimized_relative_path(src: str, output_format: str) -> str:
    src_path = Path(src)
    suffix = ".webp" if output_format == "webp" else src_path.suffix.lower()
    return str(Path("images") / "optimized" / src_path.with_suffix(suffix).name)


def in_place_output_format(src_path: Path, output_format: str) -> str:
    if output_format == "webp":
        sys.exit("Error: --format webp cannot be used for in-place optimization because paths would change")
    return "original"


def resize_dimensions(width: int, height: int, max_width: int, max_height: int) -> tuple[int, int]:
    scale = min(max_width / width, max_height / height, 1.0)
    return max(1, round(width * scale)), max(1, round(height * scale))


def is_up_to_date(src_path: Path, out_path: Path) -> bool:
    return out_path.exists() and out_path.stat().st_mtime >= src_path.stat().st_mtime


def optimize_raster(
    src_path: Path,
    out_path: Path,
    output_format: str,
    max_width: int,
    max_height: int,
    quality: int,
    force: bool,
) -> dict:
    same_file = src_path.resolve() == out_path.resolve()
    if not same_file and is_up_to_date(src_path, out_path) and not force:
        return {
            "status": "skipped",
            "originalBytes": src_path.stat().st_size,
            "optimizedBytes": out_path.stat().st_size,
        }

    original_bytes = src_path.stat().st_size

    with Image.open(src_path) as image:
        image = ImageOps.exif_transpose(image)
        original_width, original_height = image.size
        width, height = resize_dimensions(original_width, original_height, max_width, max_height)
        resized = (width, height) != image.size
        if (width, height) != image.size:
            image = image.resize((width, height), Image.Resampling.LANCZOS)

        save_kwargs = {"optimize": True}
        if output_format == "webp":
            save_format = "WEBP"
            save_kwargs.update({"quality": quality, "method": 6})
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        elif src_path.suffix.lower() in (".jpg", ".jpeg"):
            save_format = "JPEG"
            save_kwargs.update({"quality": quality, "progressive": True})
            if image.mode != "RGB":
                image = image.convert("RGB")
        else:
            save_format = "PNG"
            if image.mode == "P":
                image = image.convert("RGBA")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        if same_file:
            with tempfile.NamedTemporaryFile(
                dir=out_path.parent,
                prefix=f".{out_path.name}.",
                suffix=out_path.suffix,
                delete=False,
            ) as tmp:
                tmp_path = Path(tmp.name)
            try:
                image.save(tmp_path, save_format, **save_kwargs)
                tmp_size = tmp_path.stat().st_size
                if not resized and tmp_size >= original_bytes:
                    return {
                        "status": "kept",
                        "originalBytes": original_bytes,
                        "optimizedBytes": original_bytes,
                        "width": width,
                        "height": height,
                    }
                os.replace(tmp_path, out_path)
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()
        else:
            image.save(out_path, save_format, **save_kwargs)

    return {
        "status": "optimized",
        "originalBytes": original_bytes,
        "optimizedBytes": out_path.stat().st_size,
        "width": width,
        "height": height,
    }


def copy_asset(src_path: Path, out_path: Path, force: bool) -> dict:
    if is_up_to_date(src_path, out_path) and not force:
        return {
            "status": "skipped",
            "originalBytes": src_path.stat().st_size,
            "optimizedBytes": out_path.stat().st_size,
        }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, out_path)
    return {
        "status": "copied",
        "originalBytes": src_path.stat().st_size,
        "optimizedBytes": out_path.stat().st_size,
    }


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: {path} contains invalid JSON: {exc}")
    except OSError as exc:
        sys.exit(f"Error: cannot read {path}: {exc}")


def optimize_book(
    slug: str,
    source: str,
    derivatives: bool,
    max_width: int,
    max_height: int,
    quality: int,
    output_format: str,
    force: bool,
) -> None:
    fail_if_pillow_missing()

    book_dir = REPO_ROOT / "books" / slug
    json_path = book_dir / f"{source}.json"
    if not json_path.exists():
        sys.exit(f"Error: {json_path} not found")

    data = load_json(json_path)
    image_paths = collect_book_image_paths(data) if source == "book" else collect_content_image_paths(data)
    if not image_paths:
        sys.exit(f"Error: no image paths found in {json_path}")

    if not derivatives:
        in_place_output_format(Path(image_paths[0]), output_format)

    manifest = {
        "version": 1,
        "slug": slug,
        "settings": {
            "maxWidth": max_width,
            "maxHeight": max_height,
            "quality": quality,
            "format": output_format,
            "source": source,
            "mode": "derivatives" if derivatives else "in-place",
        },
        "images": {},
    }

    total_original = 0
    total_optimized = 0
    optimized_count = 0
    skipped_count = 0
    dimensions_by_src = {}

    for src in image_paths:
        src_path = book_dir / src
        if not src_path.exists():
            print(f"Warning: {src} does not exist; skipping", file=sys.stderr)
            continue

        suffix = src_path.suffix.lower()
        if suffix not in RASTER_EXTENSIONS and suffix not in COPY_EXTENSIONS:
            print(f"Warning: {src} has unsupported extension; skipping", file=sys.stderr)
            continue

        target_format = output_format if derivatives and suffix in RASTER_EXTENSIONS else suffix.lstrip(".")
        optimized_src = optimized_relative_path(src, target_format) if derivatives else src
        out_path = book_dir / optimized_src

        if suffix in COPY_EXTENSIONS:
            result = copy_asset(src_path, out_path, force) if derivatives else {
                "status": "unchanged",
                "originalBytes": src_path.stat().st_size,
                "optimizedBytes": src_path.stat().st_size,
            }
        else:
            result = optimize_raster(
                src_path=src_path,
                out_path=out_path,
                output_format=target_format,
                max_width=max_width,
                max_height=max_height,
                quality=quality,
                force=force,
            )

        original_bytes = result["originalBytes"]
        optimized_bytes = result["optimizedBytes"]
        total_original += original_bytes
        total_optimized += optimized_bytes
        if result["status"] in ("skipped", "unchanged", "kept"):
            skipped_count += 1
        else:
            optimized_count += 1

        if "width" in result and "height" in result:
            dimensions_by_src[src] = (result["width"], result["height"])

        if derivatives:
            manifest["images"][src] = {
                "src": optimized_src,
                "originalBytes": original_bytes,
                "optimizedBytes": optimized_bytes,
            }
            if "width" in result and "height" in result:
                manifest["images"][src]["width"] = result["width"]
                manifest["images"][src]["height"] = result["height"]

        savings = 0 if original_bytes == 0 else 100 * (1 - optimized_bytes / original_bytes)
        print(
            f"{result['status']}: {src}"
            + (f" -> {optimized_src}" if derivatives else "")
            + " "
            f"({optimized_bytes / 1024:.0f} KiB, {savings:.0f}% smaller)"
        )

    total_savings = 0 if total_original == 0 else 100 * (1 - total_optimized / total_original)
    if derivatives:
        manifest_path = book_dir / "images" / "optimized" / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        target = f"Wrote {manifest_path.relative_to(REPO_ROOT)}"
    else:
        if source == "content":
            content_changed = False
            for image in data.get("images", []):
                filename = image.get("filename")
                if filename in dimensions_by_src:
                    width, height = dimensions_by_src[filename]
                    if image.get("width") != width or image.get("height") != height:
                        image["width"] = width
                        image["height"] = height
                        content_changed = True
            if content_changed:
                json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        target = f"Optimized files from {json_path.relative_to(REPO_ROOT)} in place"

    print(
        f"{target}; "
        f"{optimized_count} changed, {skipped_count} up to date, "
        f"{total_original / 1048576:.1f} MiB -> {total_optimized / 1048576:.1f} MiB "
        f"({total_savings:.0f}% smaller)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimize book images for web delivery")
    parser.add_argument("--slug", required=True, help="Book slug under books/")
    parser.add_argument(
        "--source",
        choices=("content", "book"),
        default="content",
        help="JSON file to read image paths from. Use content during research, book during build.",
    )
    parser.add_argument(
        "--derivatives",
        action="store_true",
        help="Write optimized files to images/optimized and emit a manifest instead of overwriting local image files",
    )
    parser.add_argument("--max-width", type=int, default=2200, help="Maximum output width in pixels")
    parser.add_argument("--max-height", type=int, default=2200, help="Maximum output height in pixels")
    parser.add_argument("--quality", type=int, default=84, help="JPEG/WebP quality, 1-95")
    parser.add_argument(
        "--format",
        choices=("webp", "original"),
        default="original",
        help="Output raster format. 'original' keeps JPEG/PNG extensions. WebP requires --derivatives.",
    )
    parser.add_argument("--force", action="store_true", help="Rebuild optimized files even when up to date")
    args = parser.parse_args()

    if not 1 <= args.quality <= 95:
        parser.error("--quality must be between 1 and 95")
    if args.max_width < 1 or args.max_height < 1:
        parser.error("--max-width and --max-height must be positive")

    optimize_book(
        slug=args.slug,
        source=args.source,
        derivatives=args.derivatives,
        max_width=args.max_width,
        max_height=args.max_height,
        quality=args.quality,
        output_format=args.format,
        force=args.force,
    )


if __name__ == "__main__":
    main()
