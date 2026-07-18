---
description: Create a complete kids nonfiction picture book with editor-gated research, author, and build phases
agent: pipeline
subtask: true
---

If the user did not provide both a topic and a target age (0-99), ask before proceeding.

## Instructions

Run the `pipeline` subagent for the provided topic and target age. If the user provides build preferences such as template, seed, or strict mode, pass them through to the builder phase when reached. Default to strict builds in the full pipeline unless the user explicitly requests non-strict mode.

The pipeline must use editor approval between phases and should proceed automatically after approval. Pause only when an editor returns `BLOCKED`, when repeated revisions stop making progress, or when required credentials, licensing decisions, or human judgment are unavailable.

Do not pause for routine minor findings. The pipeline should try actionable minor findings during the first revision pass for the relevant phase, then proceed from the approved state if a minor finding persists after two attempted fixes.

If following minor or major findings would require generating more than three AI images for one book, the pipeline subagent must return `PAUSED_FOR_PERMISSION` before image four or later. The parent agent should ask the human the supplied question, then re-invoke or resume the pipeline with the user's answer. Resumption should be based on existing artifacts under `books/{slug}/`, not on hidden subagent memory.

## Completion

After a successful pipeline run, summarize the slug, generated files, editor approvals, and any non-blocking minor findings. If blocked, summarize the exact blocker, the phase where it occurred, and the artifact paths the user should inspect.
