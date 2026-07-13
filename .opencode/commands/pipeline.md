---
description: Create a complete kids nonfiction picture book with editor-gated research, author, and build phases
agent: pipeline
subtask: true
---

If the user did not provide both a topic and a target age (0-99), ask before proceeding.

## Instructions

Run the `pipeline` subagent for the provided topic and target age. If the user provides build preferences such as template, seed, or strict mode, pass them through to the builder phase when reached. Default to strict builds in the full pipeline unless the user explicitly requests non-strict mode.

The pipeline must use editor approval between phases and should proceed automatically after approval. Pause only when an editor returns `BLOCKED`, when repeated revisions stop making progress, or when required credentials, licensing decisions, or human judgment are unavailable.

## Completion

After a successful pipeline run, summarize the slug, generated files, editor approvals, and any non-blocking minor findings. If blocked, summarize the exact blocker, the phase where it occurred, and the artifact paths the user should inspect.
