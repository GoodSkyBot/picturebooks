---
mode: agent
description: Research a nonfiction topic and gather attributed images for a kids picture book
tools:
  - fetch_webpage
  - run_in_terminal
---

If the user did not provide both a topic and a target age (3-8), ask before proceeding.

## Instructions

Read and follow these files in order:
1. `AGENTS.md` (shared rules)
2. `agents/research.md` (full agent instructions)

## Stop Condition

Stop after creating `books/{slug}/content.json` and the image set.
Tell the user to review the research output before running the author prompt.
