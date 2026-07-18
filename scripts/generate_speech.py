#!/usr/bin/env python3
"""Generate speech audio using OpenAI's TTS API for picture book voice-overs.

Usage:
    python scripts/generate_speech.py --slug frogs
    python scripts/generate_speech.py --slug frogs --voice nova --speed 0.9
    python scripts/generate_speech.py --batch batch.json

The --slug mode reads books/{slug}/book.json and generates audio for every
page text and extra, saving files to books/{slug}/audio/.

The --batch mode accepts a custom JSON file with an array of items:
    [
      {
        "text": "Frogs are amphibians.",
        "output": "books/frogs/audio/page-01-text.mp3",
                "voice": "nova",
                "speed": 0.95,
        "instructions": "Speak in a warm storytelling voice for a 5-year-old."
      }
    ]

Each item requires "text" and "output". The "instructions" field is optional
and overrides the global --instructions flag for that item. The "voice" and
"speed" fields are also optional and override the global flags for that item.

Environment:
    OPENAI_API_KEY must be set in a .env file at the repo root or as an
    environment variable.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request


GPT_4O_MINI_TTS_VOICES = [
    "alloy",
    "ash",
    "ballad",
    "coral",
    "echo",
    "fable",
    "nova",
    "onyx",
    "sage",
    "shimmer",
    "verse",
    "marin",
    "cedar",
]

LEGACY_TTS_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


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


def get_api_key() -> str:
    """Return the OpenAI API key or exit with an error."""
    repo_root = Path(__file__).resolve().parent.parent
    load_dotenv(repo_root / ".env")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env or environment.", file=sys.stderr)
        sys.exit(1)
    return api_key


def voices_for_model(model: str) -> list[str]:
    if model in {"tts-1", "tts-1-hd"}:
        return LEGACY_TTS_VOICES
    return GPT_4O_MINI_TTS_VOICES


def resolve_voice(voice: str, model: str, seed: str) -> str:
    """Resolve an explicit voice or choose a stable automatic voice."""
    voices = voices_for_model(model)
    if voice != "auto":
        if voice not in voices:
            print(
                f"Error: voice '{voice}' is not supported for model '{model}'. Options: {', '.join(voices)}.",
                file=sys.stderr,
            )
            sys.exit(1)
        return voice

    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return voices[int(digest, 16) % len(voices)]


def generate_speech(
    text: str,
    api_key: str,
    model: str,
    voice: str,
    response_format: str,
    speed: float,
    instructions: str | None = None,
) -> bytes:
    """Call OpenAI TTS API and return the audio bytes."""
    body: dict = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": response_format,
        "speed": speed,
    }

    if instructions and model == "gpt-4o-mini-tts":
        body["instructions"] = instructions

    req = Request(
        "https://api.openai.com/v1/audio/speech",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req) as resp:
            return resp.read()
    except HTTPError as e:
        error_body = e.read().decode(errors="replace")
        print(f"Error calling OpenAI TTS API: {e}", file=sys.stderr)
        if error_body:
            print(f"Response: {error_body}", file=sys.stderr)
        sys.exit(1)
    except (URLError, OSError) as e:
        print(f"Error calling OpenAI TTS API: {e}", file=sys.stderr)
        sys.exit(1)


def process_batch(batch: list[dict], args: argparse.Namespace) -> None:
    """Process each item in the batch, generating and saving audio."""
    api_key = get_api_key()
    total = len(batch)

    for i, item in enumerate(batch, start=1):
        text = item.get("text")
        output = item.get("output")

        if not text or not output:
            print(
                f"Error: batch item {i} missing required 'text' or 'output' field.",
                file=sys.stderr,
            )
            sys.exit(1)

        if len(text) > 4096:
            print(
                f"Error: batch item {i} text exceeds 4096 character limit ({len(text)} chars).",
                file=sys.stderr,
            )
            sys.exit(1)

        instructions = item.get("instructions") or args.instructions
        item_voice = resolve_voice(
            item.get("voice") or args.voice,
            args.model,
            item.get("voiceSeed") or item.get("output") or text,
        )
        item_speed = item.get("speed", args.speed)

        if not isinstance(item_speed, (int, float)) or not 0.25 <= item_speed <= 4.0:
            print(
                f"Error: batch item {i} speed must be between 0.25 and 4.0.",
                file=sys.stderr,
            )
            sys.exit(1)

        dest = Path(output)
        dest.parent.mkdir(parents=True, exist_ok=True)

        print(f"[{i}/{total}] Generating: {dest} ({item_voice})", file=sys.stderr)

        audio_bytes = generate_speech(
            text=text,
            api_key=api_key,
            model=args.model,
            voice=item_voice,
            response_format=args.format,
            speed=item_speed,
            instructions=instructions,
        )

        dest.write_bytes(audio_bytes)

        if dest.stat().st_size == 0:
            print(f"Error: generated audio file is empty: {dest}", file=sys.stderr)
            dest.unlink()
            sys.exit(1)

        print(f"[{i}/{total}] Saved: {dest} ({dest.stat().st_size} bytes)", file=sys.stderr)


def batch_from_book(slug: str, audio_format: str) -> list[dict]:
    """Build a batch list from a book.json file."""
    repo_root = Path(__file__).resolve().parent.parent
    book_path = repo_root / "books" / slug / "book.json"

    if not book_path.is_file():
        print(f"Error: book.json not found at {book_path}", file=sys.stderr)
        sys.exit(1)

    with open(book_path) as f:
        book = json.load(f)

    narration = book.get("narration", {})
    voice_seed = ":".join([
        slug,
        book.get("title", ""),
        str(book.get("targetAge", "")),
        book.get("theme", {}).get("vibe", ""),
    ])
    audio_dir = f"books/{slug}/audio"
    batch: list[dict] = []

    for page_num, page in enumerate(book.get("pages", []), start=1):
        page_label = f"{page_num:02d}"

        if page.get("text"):
            item = {
                "text": page["text"],
                "output": f"{audio_dir}/page-{page_label}-text.{audio_format}",
                "voiceSeed": voice_seed,
            }
            item.update(narration)
            batch.append(item)

        for extra_num, extra in enumerate(page.get("extras", []), start=1):
            item = {
                "text": extra,
                "output": f"{audio_dir}/page-{page_label}-extra-{extra_num}.{audio_format}",
                "voiceSeed": voice_seed,
            }
            item.update(narration)
            batch.append(item)

    if not batch:
        print("Error: no text found in book.json pages.", file=sys.stderr)
        sys.exit(1)

    return batch


def main():
    parser = argparse.ArgumentParser(
        description="Generate picture book voice-over audio via OpenAI TTS API."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--slug",
        help="Book slug. Reads books/{slug}/book.json and generates audio for all pages.",
    )
    source.add_argument(
        "--batch",
        help="Path to a JSON file containing an array of {text, output, instructions?} items.",
    )
    parser.add_argument(
        "--voice",
        default="auto",
        help="Voice to use (default: auto). Options: auto, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse, marin, cedar.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini-tts",
        help="TTS model (default: gpt-4o-mini-tts). Options: gpt-4o-mini-tts, tts-1, tts-1-hd.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed from 0.25 to 4.0 (default: 1.0).",
    )
    parser.add_argument(
        "--format",
        default="mp3",
        choices=["mp3", "opus", "aac", "flac", "wav", "pcm"],
        help="Audio output format (default: mp3).",
    )
    parser.add_argument(
        "--instructions",
        help="Global tone instructions (only gpt-4o-mini-tts). Overridden by per-item instructions.",
    )
    args = parser.parse_args()

    if not 0.25 <= args.speed <= 4.0:
        print("Error: --speed must be between 0.25 and 4.0.", file=sys.stderr)
        sys.exit(1)

    if args.slug:
        batch = batch_from_book(args.slug, args.format)
    else:
        batch_path = Path(args.batch)
        if not batch_path.is_file():
            print(f"Error: batch file not found: {batch_path}", file=sys.stderr)
            sys.exit(1)

        try:
            batch = json.loads(batch_path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error reading batch file: {e}", file=sys.stderr)
            sys.exit(1)

        if not isinstance(batch, list) or not batch:
            print("Error: batch file must contain a non-empty JSON array.", file=sys.stderr)
            sys.exit(1)

    process_batch(batch, args)
    print(f"Done. Generated {len(batch)} audio file(s).", file=sys.stderr)


if __name__ == "__main__":
    main()
