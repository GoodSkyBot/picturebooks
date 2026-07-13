# Full Pipeline Plan

This plan describes the OpenCode full-pipeline workflow for creating a new nonfiction picture book. Individual phase agents remain the source of truth for their own artifacts; the pipeline agent orchestrates those agents and editor gates.

## Goal

Provide an OpenCode `/pipeline` flow that can create a complete book from topic and target age by running research, authoring, and build phases with editor approval between phases.

Editor approval replaces routine human checkpoints in the full pipeline. The pipeline pauses only when an editor returns a blocker, repeated revisions stop making progress, or required external inputs such as credentials, licensing decisions, or human judgment are unavailable.

Standalone `/research` and `/author` commands keep their existing manual review workflow. Standalone `/build` runs the builder and build-editor QA loop for an approved `book.json`.

## High-Level Flow

```text
/pipeline topic="..." age=N
  -> research agent
  -> research editorial review
  -> author agent
  -> author editorial review
  -> builder agent
  -> build editorial review
  -> completion summary
```

Each editorial review returns one of three outcomes:

- `APPROVED` means the pipeline proceeds to the next phase.
- `REVISE` means the pipeline sends accepted findings back to the same phase agent, then reruns editorial review.
- `BLOCKED` means the pipeline stops and reports why it cannot safely proceed.

The pipeline should cap revision loops. After repeated unresolved findings, normally three attempts, it should stop with `BLOCKED` rather than continue making speculative changes.

## Editor Architecture

Use independent reviewers as evidence gatherers, followed by a separate adjudicator. Do not let the positive or negative reviewer approve the phase directly.

```text
phase output
  -> deterministic checks
  -> phase-specific reviewer(s)
  -> adjudicator
  -> APPROVED | REVISE | BLOCKED
```

The author phase benefits from a two-sided review inspired by advocate/critic patterns, but with more precise roles:

- A preservation editor identifies what is working and what revisions must preserve.
- A diagnostic editor identifies defects, missed opportunities, and concrete revision requests.
- An adjudicator applies the fixed rubric and decides the outcome.

This avoids a pure advocate role, which can defend weak work, and avoids a pure critic role, which can push revisions toward bland technical compliance.

## Shared Editorial Rules

Every reviewer must inspect the artifact itself, not just the previous agent's summary.

Reviewers should provide evidence, not general impressions. Each finding should include:

```json
{
  "criterion": "image-text fit",
  "result": "pass | fail | uncertain",
  "severity": "blocking | major | minor",
  "evidence": ["page 4 uses ..."],
  "requiredChange": "...",
  "preserve": ["..."]
}
```

Verdict rules:

- `APPROVED`: no blocking or major findings remain.
- `REVISE`: actionable blocking or major findings remain and the phase agent can fix them.
- `BLOCKED`: the issue requires unavailable information, credentials, licensing resolution, human judgment, or upstream work the current phase cannot perform.
- Minor findings should be reported but should not force endless iteration.

The adjudicator should pass only accepted findings back to the phase agent. It should not pass debate transcripts, contradictory suggestions, or optional taste preferences as mandatory work.

## Research Editorial Review

The research review should emphasize objective validation and specialist review rather than advocate/critic debate.

Flow:

```text
content.json + images
  -> deterministic validation
  -> coverage reviewer
  -> visual-set reviewer
  -> research adjudicator
```

Deterministic validation should cover schema shape, required files, valid image references, source indexes, attribution fields, dimensions, content tags, and rejected-file cleanup where possible.

Coverage reviewer checks:

- The dossier has enough independent, reputable sources for the topic.
- Research notes are substantial enough to support an interesting book for the target age.
- Notes provide several possible throughlines, not just disconnected facts.
- Important caveats, sensitivities, or age constraints are called out.

Visual-set reviewer checks:

- Every image is appropriate for the topic and target age.
- Licensing and attribution are complete enough to proceed.
- The image set has a coherent visual direction.
- The set has enough variance in subject, scale, composition, orientation, and page-making potential.
- Images are useful for nonfiction storytelling, not merely decorative.

Research approval cannot be earned by strengths offsetting hard failures. Incomplete licensing, missing image files, invalid required metadata, or an insufficient research base should force `REVISE` or `BLOCKED`.

## Author Editorial Review

The author review should use the preservation/diagnostic/adjudicator pattern.

Flow:

```text
book.json + content.json + images
  -> deterministic validation
  -> preservation editor
  -> diagnostic editor
  -> author adjudicator
```

Preservation editor checks:

- The strongest throughline, emotional arc, or curiosity hook.
- Successful page moments, read-aloud rhythm, and child-facing language.
- Image-text pairings that should be preserved.
- Theme, voice, or structure choices that give the book a distinct identity.
- Risks that a revision could flatten the book into generic nonfiction prose.

Diagnostic editor checks:

- Opening, page progression, transitions, and ending.
- Age-appropriate vocabulary, sentence length, pacing, and conceptual load.
- Factual support for claims in the approved research dossier.
- Repetition, weak pages, unclear stakes, or missing explanatory bridges.
- Whether each image fits the assigned text and has useful alt text.
- Whether any page needs a generated image because the approved image pool cannot support the intended moment.

Generated-image suggestions should be specific, child-friendly briefs. The editor should suggest them; the author agent should decide whether to run the generation script and should update the JSON artifacts consistently.

Author approval should require both narrative quality and image fit. A charming text cannot compensate for unsupported facts or unusable images.

## Build Editorial Review

The build review should not use an advocate/critic pair. It should combine automated visual QA with screenshot-based inspection.

Flow:

```text
generated site
  -> npm run visual-qa -- {slug}
  -> screenshot/report review
  -> build adjudicator
```

The build editor, not the builder, owns the visual QA script. This means the builder should generate audio and the static site, then stop. The build editor should run QA, review `report.json`, inspect screenshots, and decide whether the builder must revise source templates, fragments, or builder logic.

Build editor checks:

- Visual QA exits cleanly.
- All screenshots are reviewed, not just the JSON report.
- Text is readable and not crowded at mobile, tablet, and desktop sizes.
- Images are not cropped in ways that hide essential subjects, labels, maps, diagrams, or faces.
- Controls, captions, narration buttons, and navigation do not cover meaningful content.
- Credits are readable and not visually overwhelming.
- The final site feels like a coherent picture book, not a generic reskin.

If build QA reveals a `book.json` or `content.json` problem, the build editor should block or pass the issue upstream. The builder must not silently rewrite approved content artifacts.

After approval, the build editor should remove temporary QA artifacts for the slug. If blocked, it should leave artifacts available for diagnosis and report their paths.

## Implemented Files

OpenCode-only orchestration:

- `.opencode/commands/pipeline.md`
- `.opencode/agents/pipeline.md`
- `.opencode/agents/research-editor.md`
- `.opencode/agents/author-editor.md`
- `.opencode/agents/build-editor.md`

Canonical editor guidance:

- `agents/editor.md`

Existing phase guidance:

- `agents/build.md` removes visual QA ownership from the builder and transfers it to the build editor.
- Phase agents accept explicit editor feedback and revise only their own phase outputs.
- Repository docs distinguish standalone manual commands from the automatic editor-gated `/pipeline` command.

## Known Supporting Fixes

`scripts/generate_image.py` now records generated image dimensions and required `contentTags` so fallback images can satisfy the required `content.json` image fields.

The full pipeline defaults to strict builds so approved book images are not silently dropped by template constraints.
