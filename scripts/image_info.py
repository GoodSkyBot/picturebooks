#!/usr/bin/env python3
"""Report width and height for image files.

Usage:
    python scripts/image_info.py books/{slug}/images/photo.jpg
    python scripts/image_info.py books/{slug}/images/*.png

Outputs one line per file: filename width height
Supports JPEG, PNG, GIF, WebP, and SVG (viewBox-based).
No external dependencies required.
"""

import struct
import sys
import re
from pathlib import Path


def jpeg_dimensions(path: Path) -> tuple[int, int] | None:
    with open(path, "rb") as f:
        data = f.read(2)
        if data != b"\xff\xd8":
            return None
        while True:
            marker = f.read(2)
            if len(marker) < 2 or marker[0] != 0xFF:
                return None
            if marker[1] == 0xD9:
                return None
            length_data = f.read(2)
            if len(length_data) < 2:
                return None
            length = struct.unpack(">H", length_data)[0]
            if marker[1] in (0xC0, 0xC2, 0xC1, 0xC3):
                block = f.read(5)
                if len(block) < 5:
                    return None
                h = struct.unpack(">H", block[1:3])[0]
                w = struct.unpack(">H", block[3:5])[0]
                return w, h
            f.read(length - 2)


def png_dimensions(path: Path) -> tuple[int, int] | None:
    with open(path, "rb") as f:
        header = f.read(24)
        if len(header) < 24:
            return None
        if header[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        w = struct.unpack(">I", header[16:20])[0]
        h = struct.unpack(">I", header[20:24])[0]
        return w, h


def gif_dimensions(path: Path) -> tuple[int, int] | None:
    with open(path, "rb") as f:
        header = f.read(10)
        if len(header) < 10:
            return None
        if header[:4] not in (b"GIF8", b"GIF8"):
            return None
        w = struct.unpack("<H", header[6:8])[0]
        h = struct.unpack("<H", header[8:10])[0]
        return w, h


def webp_dimensions(path: Path) -> tuple[int, int] | None:
    with open(path, "rb") as f:
        header = f.read(30)
        if len(header) < 30:
            return None
        if header[:4] != b"RIFF" or header[8:12] != b"WEBP":
            return None
        # VP8 lossy
        if header[12:16] == b"VP8 ":
            # Skip to frame header
            w = struct.unpack("<H", header[26:28])[0] & 0x3FFF
            h = struct.unpack("<H", header[28:30])[0] & 0x3FFF
            return w, h
        # VP8L lossless
        if header[12:16] == b"VP8L":
            bits = struct.unpack("<I", header[21:25])[0]
            w = (bits & 0x3FFF) + 1
            h = ((bits >> 14) & 0x3FFF) + 1
            return w, h
        return None


def svg_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        text = path.read_text(encoding="utf-8")[:4096]
    except (UnicodeDecodeError, OSError):
        return None
    # Try viewBox first
    match = re.search(r'viewBox=["\'][\s]*[\d.]+[\s,]+[\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', text)
    if match:
        w = int(float(match.group(1)))
        h = int(float(match.group(2)))
        if w > 0 and h > 0:
            return w, h
    # Try width/height attributes
    w_match = re.search(r'\bwidth=["\'](\d+)', text)
    h_match = re.search(r'\bheight=["\'](\d+)', text)
    if w_match and h_match:
        return int(w_match.group(1)), int(h_match.group(1))
    return None


def get_dimensions(path: Path) -> tuple[int, int] | None:
    suffix = path.suffix.lower()
    if suffix in (".jpg", ".jpeg"):
        return jpeg_dimensions(path)
    elif suffix == ".png":
        return png_dimensions(path)
    elif suffix == ".gif":
        return gif_dimensions(path)
    elif suffix == ".webp":
        return webp_dimensions(path)
    elif suffix == ".svg":
        return svg_dimensions(path)
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/image_info.py <image_path> [...]", file=sys.stderr)
        sys.exit(1)

    errors = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"ERROR: {arg} not found", file=sys.stderr)
            errors += 1
            continue
        dims = get_dimensions(path)
        if dims:
            w, h = dims
            print(f"{arg} {w} {h}")
        else:
            print(f"ERROR: {arg} unsupported or unreadable", file=sys.stderr)
            errors += 1

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
