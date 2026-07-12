---
description: Write a kids nonfiction picture book from researched content
agent: author
subtask: true
---

If the user did not specify a slug, ask for it before proceeding.

## Preconditions

- `books/{slug}/content.json` must exist.
- If it does not exist, stop and tell the user to run `/research` first.

## Instructions

Run the `author` subagent for the provided slug.

## Stop Condition

Stop after creating `books/{slug}/book.json`.
Tell the user to review or edit it before running `/build`.
