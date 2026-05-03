---
description: Write a kids nonfiction picture book from researched content
---

Run the picture-books author agent.

If the user did not specify a slug, ask for it before proceeding.

## Goal

Read `books/{slug}/content.json` and create:
- `books/{slug}/book.json`

## Required References

Read and follow:
- `AGENTS.md`
- `guidelines/content.md`
- `guidelines/design.md`
- `prompts/author.md`
- `schemas/book.schema.json`

## Preconditions

- `books/{slug}/content.json` must exist.
- If it does not exist, stop and tell the user to run `/research` first.

## Required Behavior

- Choose page count based on target age and content depth.
- Write main page text that reads aloud well.
- Use optional `extras` as short fact bubbles.
- Support multiple images per page where useful.
- Generate a distinct theme for the book.
- Make the theme influence more than colors.
- Keep the result easy for a human to edit.

## Deliverable

Create `books/{slug}/book.json` that matches `schemas/book.schema.json`.

## Review Boundary

Stop after creating `book.json`. Tell the user to review or edit it before running `/build`.
