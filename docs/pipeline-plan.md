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

Minor findings should not create routine human checkpoints. During the first review iteration for a phase, the orchestrator should ask the phase agent to address actionable minor findings along with blocking and major findings when those fixes are safe, local to the phase, and unlikely to flatten the book. If the same minor finding persists after two attempted fixes, the pipeline should proceed from the current approved state and include the unresolved minor finding in the completion summary instead of looping indefinitely.

Generated-image use is allowed as part of this minor-fix pass, especially for cover or image-text fit recommendations, but it needs a volume guardrail. If the pipeline would generate more than three AI images for a single book, it must pause for human permission before generating image four or later. Because the pipeline runs as a subagent, this should be a controlled `PAUSED_FOR_PERMISSION` return to the parent agent, not an inner subagent question. The pause payload should include the slug, phase, generated image count so far, proposed extra generated-image briefs, which pages they would replace or support, and the exact question the parent should ask.

Pipeline resume should be artifact-based rather than dependent on hidden subagent memory. After the parent obtains the user's answer, it may re-invoke or resume the pipeline with explicit permission. The pipeline should inspect existing files under `books/{slug}/`, determine the last completed phase from artifacts and any supplied editor context, and continue from the paused phase without redoing completed work unless a revision is required.

## Editor Architecture

Use specialized reviewers with separate context windows. Each editor loads only its phase-specific definition and the artifacts needed for that review.

```text
phase output
  -> deterministic checks
  -> phase-specific reviewer(s)
  -> APPROVED | REVISE | BLOCKED
```

The author phase uses two independent reviews inspired by advocate/critic patterns, but with more precise roles:

- A preservation editor identifies what is working and what revisions must preserve.
- A diagnostic editor identifies defects, missed opportunities, and concrete revision requests.

The diagnostic editor supplies the author gate verdict. When revision is required, the orchestrator sends the diagnostic findings and the preservation editor's `mustPreserve` brief to the author. The two reviewers do not see each other's reports.

This avoids a pure advocate role, which can defend weak work, and prevents diagnostic revisions from pushing the book toward bland technical compliance.

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

Minor findings are still useful. The orchestrator should include actionable minor findings in the first revision request for the relevant phase, provided they are safe to fix within that phase. After two unsuccessful attempts to resolve a minor finding, treat it as non-blocking: proceed if the artifact is otherwise approved and record the residual issue in the final summary.

The orchestrator should pass only actionable findings back to the phase agent. It should not pass debate transcripts, contradictory suggestions, or optional taste preferences as mandatory work.

## Research Editorial Review

The research editor combines dossier sufficiency and image-pool breadth review in one specialized context.

Flow:

```text
content.json + images
  -> deterministic validation
  -> research editor
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

The author review uses independent preservation and diagnostic editors.

Flow:

```text
book.json + content.json + images
  -> deterministic validation
  -> preservation editor (independent)
  -> diagnostic editor (independent, supplies verdict)
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

When the diagnostic editor returns generated-image briefs with a minor severity, the orchestrator should normally ask the author agent to try those briefs during the first author revision pass rather than ignoring them. If the author can resolve the issue with an existing approved image instead, that is acceptable. If the minor generated-image recommendation persists after two attempts, proceed with the approved book state and report the tradeoff in the completion summary.

The orchestrator must track generated images per book across research and author revisions. Generating up to three AI images may proceed without a human checkpoint when supported by editor findings or missing visual coverage. Before generating a fourth AI image, return `PAUSED_FOR_PERMISSION` to the parent agent with the proposed image briefs and a concise permission question.

## Build Editorial Review

The build review should not use an advocate/critic pair. It should combine automated visual QA with screenshot-based inspection.

Flow:

```text
generated site
  -> npm run visual-qa -- {slug}
  -> screenshot/report review
  -> build editor verdict
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
- `.opencode/agents/author-preservation-editor.md`
- `.opencode/agents/author-diagnostic-editor.md`
- `.opencode/agents/build-editor.md`

Specialized canonical editor guidance:

- `agents/research-editor.md`
- `agents/author-preservation-editor.md`
- `agents/author-diagnostic-editor.md`
- `agents/build-editor.md`

Existing phase guidance:

- `agents/build.md` removes visual QA ownership from the builder and transfers it to the build editor.
- Phase agents accept explicit editor feedback and revise only their own phase outputs.
- Repository docs distinguish standalone manual commands from the automatic editor-gated `/pipeline` command.

## Known Supporting Fixes

`scripts/generate_image.py` now records generated image dimensions and required `contentTags` so fallback images can satisfy the required `content.json` image fields.

The full pipeline defaults to strict builds so approved book images are not silently dropped by template constraints.
