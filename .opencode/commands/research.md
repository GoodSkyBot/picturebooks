---
description: Research a nonfiction topic and gather attributed images for a kids picture book
agent: research
subtask: true
---

If the user did not provide both a topic and a target age (0-99), ask before proceeding.

## Instructions

Run the `research` subagent for the provided topic and target age.

## Stop Condition

Stop after creating `books/{slug}/content.json` and the image set.
Tell the user to review the research output before running `/author`.
