This repository is an agentic children's picture book authoring pipeline.

Read `AGENTS.md` for the shared contract that governs all agent behavior.

The pipeline has three stages run in order: research, author, build.
Agent instructions live in `agents/`. Guidelines live in `guidelines/`. Schemas live in `schemas/`.

Do not break paths inside `books/{slug}`.
