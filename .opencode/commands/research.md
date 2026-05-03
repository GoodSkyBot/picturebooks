---
description: Research a nonfiction topic and gather attributed images for a kids picture book
---

Run the picture-books research agent.

If the user did not specify both a topic and a target age, ask for them before proceeding.

## Goal

Research a nonfiction topic for a children's picture book and produce:
- `books/{slug}/content.json`
- `books/{slug}/images/*`

## Inputs

- topic
- target age from 3 to 8

## Required References

Read and follow:
- `AGENTS.md`
- `guidelines/content.md`
- `prompts/research.md`
- `schemas/content.schema.json`

## Required Behavior

- Use Wikipedia as the primary source for topic discovery and overview.
- Use Wikimedia Commons for images.
- Use other reputable sources only to support or cross-check facts.
- Preserve attribution and license metadata for every image.
- Reject images with ambiguous or incomplete licensing.
- Keep facts traceable to sources.
- Treat age as a first-class input.

## Deliverable

Create `books/{slug}/content.json` that matches `schemas/content.schema.json` and populate `books/{slug}/images/` with candidate images.

Use relative image paths with folders in JSON, such as `images/tree-frog.jpg`.

## Review Boundary

Stop after creating `content.json` and the image set. Tell the user to review the research output before running `/author`.
