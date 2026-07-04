#!/usr/bin/env python3
"""Site builder: generate a static picture book website from book.json using templates."""

import argparse
import json
import os
import random
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

SITE_BUILDER_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SITE_BUILDER_DIR / "templates"
REPO_ROOT = SITE_BUILDER_DIR.parent


def load_json(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        sys.exit(f"Error: {path} contains invalid JSON: {e}")
    except OSError as e:
        sys.exit(f"Error: cannot read {path}: {e}")


def load_template_manifest(template_name: str) -> dict:
    manifest_path = TEMPLATES_DIR / template_name / "template.json"
    if not manifest_path.exists():
        sys.exit(f"Error: template '{template_name}' not found at {manifest_path}")
    return load_json(manifest_path)


def classify_page(page: dict) -> int:
    """Return the image count bucket for a page."""
    return len(page.get("images", []))


def get_orientations(images: list) -> list:
    """Return the list of orientations for a set of images."""
    return [img.get("orientation", "landscape") for img in images]


def slot_matches(slot: str, orientation: str) -> bool:
    """Check if an image orientation matches a slot constraint."""
    if slot == "*":
        return True
    return slot == orientation


def select_fragment(manifest: dict, images: list, rng: random.Random) -> str:
    """Select a fragment filename based on image count and orientations.

    Matching priority:
    1. Exact orientation match (slot constraints match image orientations)
    2. Wildcard slots that accept the right number of images
    3. Any fragment with the right slot count (fallback)
    """
    fragments = manifest.get("fragments", [])
    image_count = len(images)
    orientations = get_orientations(images)

    # Filter to fragments with the right number of slots
    candidates = [f for f in fragments if len(f["slots"]) == image_count]

    if not candidates:
        # Fall back to closest slot count
        all_counts = sorted(set(len(f["slots"]) for f in fragments))
        if not all_counts:
            sys.exit("Error: template has no page fragments defined")
        best = max((c for c in all_counts if c <= image_count), default=max(all_counts))
        candidates = [f for f in fragments if len(f["slots"]) == best]

    # Filter to fragments whose slots accept these orientations
    compatible = [
        f for f in candidates
        if all(slot_matches(s, o) for s, o in zip(f["slots"], orientations))
    ]

    if compatible:
        return rng.choice(compatible)["file"]

    # Last resort: any candidate with the right slot count
    return rng.choice(candidates)["file"]


def build_attribution_map(content: dict) -> dict:
    """Build a map from image filename to attribution info."""
    attr_map = {}
    for img in content.get("images", []):
        filename = img.get("filename", "")
        attr_map[filename] = {
            "author": img.get("author", "Unknown"),
            "license": img.get("license", ""),
            "license_url": img.get("license_url", ""),
            "source_url": img.get("source_url", ""),
            "description": img.get("description", ""),
        }
    return attr_map


def get_image_caption(image_src: str, attribution_map: dict) -> str:
    """Get a short attribution caption for an image."""
    info = attribution_map.get(image_src, {})
    if not info:
        return ""
    author = info.get("author", "")
    license_name = info.get("license", "")
    if author and license_name:
        return f"Photo: {author} / {license_name}"
    if author:
        return f"Photo: {author}"
    return ""


def build_index() -> None:
    """Regenerate the root index.html from all books/*/book.json files."""
    books_dir = REPO_ROOT / "books"
    books = []

    for book_json_path in sorted(books_dir.glob("*/book.json")):
        book = load_json(book_json_path)
        cover = book.get("cover", {})
        theme = book.get("theme", {})
        books.append({
            "slug": book.get("slug", book_json_path.parent.name),
            "title": cover.get("title", book.get("title", "")),
            "subtitle": cover.get("subtitle", ""),
            "cover_image": cover.get("image", ""),
            "cover_alt": cover.get("alt", cover.get("title", "")),
            "primary_color": theme.get("primaryColor", "#333"),
        })

    books.sort(key=lambda b: b["title"].lower())

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
        keep_trailing_newline=True,
    )
    template = env.get_template("index.html.j2")
    html = template.render(books=books)

    index_path = REPO_ROOT / "index.html"
    index_path.write_text(html, encoding="utf-8")
    print(f"Updated root index.html with {len(books)} book(s)")


def build(slug: str, template_name: str, seed: int | None, strict: bool) -> None:
    book_dir = REPO_ROOT / "books" / slug
    book_path = book_dir / "book.json"
    content_path = book_dir / "content.json"

    if not book_path.exists():
        sys.exit(f"Error: {book_path} not found")

    book = load_json(book_path)
    if not content_path.exists():
        print(f"Warning: {content_path} not found; credits and captions will be empty", file=sys.stderr)
        content = {}
    else:
        content = load_json(content_path)

    manifest = load_template_manifest(template_name)
    template_dir = TEMPLATES_DIR / template_name

    rng = random.Random(seed)

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader([str(template_dir), str(template_dir / "fragments")]),
        autoescape=True,
        keep_trailing_newline=True,
    )

    # Build attribution map
    attribution_map = build_attribution_map(content)

    # Prepare page data with fragment selections and attribution
    pages_data = []
    warnings = []
    max_images = manifest.get("maxImagesPerPage", 2)

    for i, page in enumerate(book.get("pages", []), start=1):
        image_count = classify_page(page)
        images_to_render = page.get("images", [])

        # Check overflow
        if image_count > max_images:
            dropped = images_to_render[max_images:]
            images_to_render = images_to_render[:max_images]
            msg = (
                f"Page {i}: dropping {len(dropped)} image(s) "
                f"(template supports max {max_images}): "
                + ", ".join(img["src"] for img in dropped)
            )
            warnings.append(msg)
            print(f"Warning: {msg}", file=sys.stderr)
            image_count = max_images

        fragment_file = select_fragment(manifest, images_to_render, rng)

        # Add captions to images
        images_with_captions = []
        for img in images_to_render:
            images_with_captions.append({
                **img,
                "caption": get_image_caption(img["src"], attribution_map),
            })

        pages_data.append({
            "number": i,
            "text": page.get("text", ""),
            "extras": page.get("extras", []),
            "images": images_with_captions,
            "fragment": fragment_file,
        })

    if strict and warnings:
        sys.exit(f"Strict mode: {len(warnings)} content overflow warning(s). Aborting.")

    # Render page fragments
    rendered_pages = []
    for page_data in pages_data:
        fragment_template = env.get_template(page_data["fragment"])
        rendered = fragment_template.render(
            page=page_data,
            page_number=page_data["number"],
            theme=book.get("theme", {}),
        )
        rendered_pages.append(rendered)

    # Render cover
    cover_template = env.get_template("cover.html.j2")
    rendered_cover = cover_template.render(
        cover=book.get("cover", {}),
        theme=book.get("theme", {}),
    )

    # Render credits
    back_matter = book.get("backMatter", {})
    show_credits = back_matter.get("showCredits", True)
    show_sources = back_matter.get("showSources", True)

    rendered_credits = ""
    if show_credits or show_sources:
        credits_template = env.get_template("credits.html.j2")
        rendered_credits = credits_template.render(
            content=content,
            attribution_map=attribution_map,
            book=book,
            theme=book.get("theme", {}),
            show_credits=show_credits,
            show_sources=show_sources,
        )

    # Render base HTML
    base_template = env.get_template("base.html.j2")
    total_pages = len(rendered_pages) + 1 + (1 if rendered_credits else 0)  # cover + pages [+ credits]
    html_output = base_template.render(
        book=book,
        theme=book.get("theme", {}),
        cover_html=rendered_cover,
        pages_html=rendered_pages,
        credits_html=rendered_credits,
        total_pages=total_pages,
    )

    # Write output files
    out_dir = book_dir

    # Write index.html
    (out_dir / "index.html").write_text(html_output, encoding="utf-8")

    # Copy static CSS and JS
    css_src = template_dir / "style.css"
    js_src = template_dir / "script.js"
    if css_src.exists():
        shutil.copy2(css_src, out_dir / "style.css")
    if js_src.exists():
        shutil.copy2(js_src, out_dir / "script.js")

    print(f"Built '{book['title']}' using template '{template_name}' -> {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Build a picture book static site")
    parser.add_argument("--slug", help="Book slug (directory name under books/)")
    parser.add_argument("--template", help="Template name to use")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible fragment selection")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any content is dropped")
    parser.add_argument("--update-index", action="store_true", help="Regenerate root index.html from all books")
    parser.add_argument("--no-update-index", action="store_true", help="Skip automatic index update after build")
    args = parser.parse_args()

    if args.update_index:
        build_index()
        return

    if not args.slug or not args.template:
        parser.error("--slug and --template are required when not using --update-index")

    build(args.slug, args.template, args.seed, args.strict)

    if not args.no_update_index:
        build_index()


if __name__ == "__main__":
    main()
