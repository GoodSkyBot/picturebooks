---
description: Build the final static kids picture-book site from book.json and run build-editor QA
agent: build-runner
subtask: true
---

If the user did not specify a slug, ask for it before proceeding.

## Preconditions

- `books/{slug}/book.json` must exist.
- If it does not exist, stop and tell the user to run `/author` first.

## Instructions

Run the `build-runner` subagent for the provided slug.

## Completion

After building and build-editor review, summarize what was generated and note any missing assets or unresolved issues.
