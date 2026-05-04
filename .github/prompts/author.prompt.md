---
agent: agent
description: Write a kids nonfiction picture book from researched content
tools: [execute, read, agent, edit, search, web/fetch, todo]
---

If the user did not specify a slug, ask for it before proceeding.

## Preconditions

- `books/{slug}/content.json` must exist.
- If it does not exist, stop and tell the user to run the research prompt first.

## Instructions

Read and follow these files in order:
1. `AGENTS.md` (shared rules)
2. `agents/author.md` (full agent instructions)

## Stop Condition

Stop after creating `books/{slug}/book.json`.
Tell the user to review or edit it before running the build prompt.
