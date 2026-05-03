---
description: Build the final static kids picture-book site from book.json
---

Run the picture-books build agent.

If the user did not specify a slug, ask for it before proceeding.

## Goal

Read `books/{slug}/book.json` and create:
- `books/{slug}/index.html`
- `books/{slug}/style.css`
- `books/{slug}/script.js`

## Required References

Read and follow:
- `AGENTS.md`
- `guidelines/design.md`
- `guidelines/ux.md`
- `prompts/build.md`

## Preconditions

- `books/{slug}/book.json` must exist.
- If it does not exist, stop and tell the user to run `/author` first.

## Required Behavior

- Use plain HTML, CSS, and JS only.
- Keep the result self-contained inside `books/{slug}`.
- Preserve the required UX rules: large previous/next buttons, swipe gestures, keyboard navigation, page progress, reduced-motion support, visible credits and sources, and image alt text.
- Create a visually distinct result for the book instead of a generic reskin.
- Let page structure respond to image count, text density, and extras.

## Deliverable

Create the final static book files in `books/{slug}/`.

## Completion

After building, summarize what was generated and note any missing assets or unresolved issues.
