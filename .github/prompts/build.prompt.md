---
agent: agent
description: Build the final static kids picture-book site from book.json
---

If the user did not specify a slug, ask for it before proceeding.

## Preconditions

- `books/{slug}/book.json` must exist.
- If it does not exist, stop and tell the user to run the author prompt first.

## Instructions

Read and follow these files in order:
1. `AGENTS.md` (shared rules)
2. `agents/build.md` (full agent instructions)

## Completion

After building, summarize what was generated and note any missing assets or unresolved issues.
