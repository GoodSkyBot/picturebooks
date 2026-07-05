# Agent Contract

This repository is an agentic pipeline for creating nonfiction picture book websites for children. Each book is built as a self-contained static site inside `books/{slug}/`.

## Pipeline

Three agent runs produce a book, in order:

1. **research** - Gathers facts and images into `books/{slug}/content.json`.
2. **author** - Writes the book text and structure into `books/{slug}/book.json`.
3. **build** - Generates the final static site (`index.html`, `style.css`, `script.js`).

Human review happens after `content.json` and after `book.json`. The build agent should assume `book.json` is the approved source of truth.

Agents can be invoked via OpenCode (`/research`, `/author`, `/build`) or VS Code Copilot prompt files (`.github/prompts/`). Full agent instructions live in `agents/`. Guidelines live in `guidelines/`. Schemas live in `schemas/`.

## Shared Rules

These rules apply to all agents:

- Run repository Python scripts with the existing virtual environment: `.venv/bin/python`, not system `python` or `python3`.
- Treat age as a first-class input.
- Preserve attribution and license metadata for every image.
- Do not use images with ambiguous or incomplete licensing.
- Prefer ASCII in generated files unless existing files already require Unicode.
- Do not break paths inside `books/{slug}`.
- Keep the result editable by a human between stages.
