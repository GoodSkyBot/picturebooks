# Editor Agents

Editor agents review phase outputs in an editor-gated workflow. They do not create phase artifacts. They decide whether a phase output is ready to advance, needs revision by the responsible phase agent, or is blocked.

## Shared Verdicts

Return exactly one verdict:

- `APPROVED` - No blocking or major findings remain. The workflow may advance.
- `REVISE` - Actionable blocking or major findings remain and the responsible phase agent can fix them.
- `BLOCKED` - The issue requires unavailable information, credentials, licensing resolution, human judgment, or upstream work the current phase cannot safely perform.

Minor findings may be reported but must not cause endless iteration.

## Shared Review Rules

- Inspect the artifact itself, not just the previous agent's summary.
- Use `AGENTS.md`, the phase instructions in `agents/`, relevant guidelines, and schemas as the review contract.
- Provide evidence for every failed or uncertain criterion.
- Do not average away hard failures. Strong prose, appealing images, or good layout cannot offset licensing, missing-file, schema, factual-support, or broken-site failures.
- Do not rewrite the phase output yourself.
- Do not pass full debate transcripts back to phase agents. Pass only accepted, actionable findings.
- Prefer concrete required changes over broad taste preferences.

Each finding should use this shape:

```json
{
  "criterion": "image-text fit",
  "result": "pass | fail | uncertain",
  "severity": "blocking | major | minor",
  "evidence": ["page 4 uses images/reef.jpg, but the text describes a rainforest canopy."],
  "requiredChange": "Assign a rainforest image or revise the page text to match the reef image.",
  "preserve": ["Keep the page's question-and-answer rhythm."]
}
```

## Response Shape

Return a concise structured review:

```json
{
  "verdict": "APPROVED | REVISE | BLOCKED",
  "summary": "One or two sentences.",
  "strengthsToPreserve": ["..."],
  "requiredChanges": [
    {
      "criterion": "...",
      "severity": "blocking | major | minor",
      "evidence": ["..."],
      "requiredChange": "...",
      "preserve": ["..."]
    }
  ],
  "notesForUserIfBlocked": "Only present when verdict is BLOCKED."
}
```

Use empty arrays when there are no items.

## Research Editorial Review

Review `books/{slug}/content.json` and the image files in `books/{slug}/images/`.

Emphasize objective validation and specialist review rather than advocate/critic debate.

Check:

- `content.json` appears to follow `schemas/content.schema.json`.
- The dossier has enough independent, reputable sources for the topic.
- Research notes are substantial enough to support an interesting book for the target age.
- Notes provide several possible throughlines, not just disconnected facts.
- Important caveats, sensitivities, or age constraints are called out.
- Every referenced image file exists.
- Image metadata includes attribution, license, dimensions, and useful `contentTags`.
- Images are appropriate for the topic and target age.
- The image set has a coherent visual direction plus useful variance in subject, scale, composition, orientation, and page-making potential.
- Images are useful for nonfiction storytelling, not merely decorative.

Incomplete licensing, missing image files, invalid required metadata, or an insufficient research base should force `REVISE` or `BLOCKED`.

## Author Editorial Review

Review `books/{slug}/book.json` against `content.json` and the approved images.

Use the preservation/diagnostic pattern:

- Preserve the strongest throughline, curiosity hook, page moments, read-aloud rhythm, image-text pairings, and distinct voice or theme.
- Diagnose defects in opening, page progression, transitions, ending, age fit, factual support, repetition, weak pages, image assignment, and alt text.

Check:

- `book.json` appears to follow `schemas/book.schema.json`.
- The book has a clear beginning, progression, and satisfying ending.
- Page text is age-appropriate, factual, and good read-aloud copy.
- Every factual claim traces to the approved research dossier or its sources.
- Every page image supports the assigned page text.
- Images are not reused unless the schema or instructions explicitly allow it.
- Alt text is meaningful.
- Theme fields are complete and topic-specific.
- The book has visual and narrative variety without becoming incoherent.

If a page needs a generated image because the approved image pool cannot support the intended moment, suggest a specific child-friendly prompt and explain why the existing pool is insufficient. The author agent owns generation and artifact updates.

## Build Editorial Review

Review the generated static site after the builder completes.

The build editor owns visual QA:

```bash
npm run visual-qa -- {slug}
```

Review both `tmp/screenshots/{slug}/report.json` and every generated screenshot. Do not rely only on the JSON report.

Check:

- Visual QA exits cleanly.
- Text is readable and not crowded at mobile, tablet, and desktop sizes.
- Images are not cropped in ways that hide essential subjects, labels, maps, diagrams, or faces.
- Controls, captions, narration buttons, and navigation do not cover meaningful content.
- Credits are readable and not visually overwhelming.
- The final site feels like a coherent picture book, not a generic reskin.

If build QA reveals a layout issue, return `REVISE` with source-level guidance for the builder. The builder must fix templates, fragments, or builder logic and rebuild; it must not manually edit generated `index.html`, `style.css`, or `script.js`.

If build QA reveals a content problem in `book.json` or `content.json`, return `BLOCKED` or identify the upstream phase that must revise it. The builder must not silently rewrite approved content artifacts.

After approval, remove `tmp/screenshots/{slug}/`. If blocked, leave QA artifacts available and report their paths.
