#!/usr/bin/env python3
"""Generate an image using OpenAI's Images API for use in a picture book.

Usage:
    python scripts/generate_image.py --slug SLUG --prompt "A colorful tree frog on a leaf"

Environment:
    OPENAI_API_KEY must be set in a .env file at the repo root or as an
    environment variable.

The script saves the image into books/{slug}/images/ and prints a JSON object
compatible with the content.json images array schema.
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

from image_info import get_dimensions


def load_dotenv(path: Path) -> None:
    """Load key=value pairs from a .env file into os.environ."""
    if not path.is_file():
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def slugify(text: str) -> str:
    """Convert text to a kebab-case filename-safe string."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].strip("-")


def generate_image(prompt: str, model: str, size: str, quality: str) -> bytes:
    """Call OpenAI Images API and return the image bytes."""
    repo_root = Path(__file__).resolve().parent.parent
    load_dotenv(repo_root / ".env")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env or environment.", file=sys.stderr)
        sys.exit(1)

    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality,
        "output_format": "png",
    }).encode()

    req = Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read())
    except HTTPError as e:
        body_text = e.read().decode(errors="replace")
        print(f"Error calling OpenAI Images API: {e}", file=sys.stderr)
        if body_text:
            print(f"Response: {body_text}", file=sys.stderr)
        sys.exit(1)
    except (URLError, OSError) as e:
        print(f"Error calling OpenAI Images API: {e}", file=sys.stderr)
        sys.exit(1)

    b64 = data["data"][0]["b64_json"]
    return base64.b64decode(b64)


def save_image(image_bytes: bytes, dest: Path) -> None:
    """Write image bytes to destination path."""
    dest.write_bytes(image_bytes)

    if dest.stat().st_size == 0:
        print("Error: generated image is empty.", file=sys.stderr)
        dest.unlink()
        sys.exit(1)


def parse_tags(value: str | None) -> list[str]:
    if not value:
        return []
    tags = []
    seen = set()
    for raw in value.split(","):
        tag = raw.strip()
        if tag and tag not in seen:
            tags.append(tag)
            seen.add(tag)
    return tags


def main():
    parser = argparse.ArgumentParser(
        description="Generate a picture book image via OpenAI Images API."
    )
    parser.add_argument(
        "--slug", required=True, help="Book slug (directory name under books/)"
    )
    parser.add_argument(
        "--prompt", required=True, help="Image generation prompt"
    )
    parser.add_argument(
        "--filename",
        help="Override output filename (without images/ prefix or extension)",
    )
    parser.add_argument(
        "--model", default="gpt-image-2", help="Model to use (default: gpt-image-2)"
    )
    parser.add_argument(
        "--size",
        default="1024x1024",
        choices=["1024x1024", "1536x1024", "1024x1536", "auto"],
        help="Image size (default: 1024x1024, square)",
    )
    parser.add_argument(
        "--quality",
        default="auto",
        choices=["low", "medium", "high", "auto"],
        help="Image quality (default: auto)",
    )
    parser.add_argument(
        "--content-tags",
        help="Comma-separated content tags for content.json metadata",
    )
    parser.add_argument(
        "--style-tags",
        help="Comma-separated visual style tags for content.json metadata",
    )
    parser.add_argument(
        "--image-type",
        default="illustration",
        choices=["photo", "illustration", "painting", "diagram", "map", "document", "other"],
        help="Image type metadata value (default: illustration)",
    )
    args = parser.parse_args()

    # Resolve paths relative to repo root
    repo_root = Path(__file__).resolve().parent.parent
    images_dir = repo_root / "books" / args.slug / "images"

    if not images_dir.parent.exists():
        print(
            f"Error: book directory books/{args.slug}/ does not exist.",
            file=sys.stderr,
        )
        sys.exit(1)

    images_dir.mkdir(exist_ok=True)

    # Determine filename
    stem = args.filename if args.filename else slugify(args.prompt)
    if not stem:
        stem = "generated-image"
    dest = images_dir / f"{stem}.png"

    # Avoid overwriting
    counter = 1
    while dest.exists():
        dest = images_dir / f"{stem}-{counter}.png"
        counter += 1

    # Generate and save
    print(f"Generating image: {args.prompt}", file=sys.stderr)
    image_bytes = generate_image(args.prompt, args.model, args.size, args.quality)

    print(f"Saving to {dest.relative_to(repo_root)}", file=sys.stderr)
    save_image(image_bytes, dest)

    dimensions = get_dimensions(dest)
    if dimensions is None:
        print(f"Error: could not read dimensions from {dest.relative_to(repo_root)}", file=sys.stderr)
        dest.unlink()
        sys.exit(1)
    width, height = dimensions

    # Output content.json-compatible metadata
    relative_path = f"images/{dest.name}"
    content_tags = parse_tags(args.content_tags) or ["generated image"]
    style_tags = parse_tags(args.style_tags)
    metadata = {
        "filename": relative_path,
        "description": args.prompt,
        "source_url": "https://openai.com/policies/terms-of-use",
        "author": f"OpenAI {args.model}",
        "license": "Generated (non-redistributable without rights)",
        "license_url": "https://openai.com/policies/terms-of-use",
        "width": width,
        "height": height,
        "imageType": args.image_type,
        "contentTags": content_tags,
    }
    if style_tags:
        metadata["styleTags"] = style_tags

    # Auto-update content.json if it exists
    content_path = repo_root / "books" / args.slug / "content.json"
    if content_path.is_file():
        with open(content_path) as f:
            content = json.load(f)
        content["images"].append(metadata)
        with open(content_path, "w") as f:
            json.dump(content, f, indent=2)
            f.write("\n")
        print(f"Updated {content_path.relative_to(repo_root)}", file=sys.stderr)
    else:
        print(f"No content.json found at {content_path.relative_to(repo_root)}, skipping auto-update.", file=sys.stderr)

    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
