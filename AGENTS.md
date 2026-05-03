# Agent Contract

This repository uses three manual OpenCode agent runs per book:

1. research
2. author
3. build

All agents must follow these rules.

## Shared Rules

- Treat age as a first-class input.
- Prefer Wikipedia for topic discovery and Wikimedia Commons for images.
- Use other reputable sources only to support or cross-check facts.
- Preserve attribution and license metadata for every image.
- Do not use images with ambiguous or incomplete licensing.
- Prefer ASCII in generated files unless existing files already require Unicode.
- Do not break paths inside `books/{slug}`.
- Keep the result editable by a human between stages.

## Content Rules

- Facts must remain traceable to sources.
- Do not invent factual claims.
- Avoid overly technical explanations for younger audiences.
- Use a gentle tone when describing predator-prey or defensive behavior.
- Main page text should be readable aloud.
- `extras` are optional short fact bubbles, not mini paragraphs.

## Design Rules

- Every book needs its own visual identity.
- Theme must affect more than colors; it should influence typography, decoration, and layout choices.
- Do not output the same layout pattern for every page.
- Keep decorative elements supportive, not noisy.
- Use Google Fonts when custom fonts are needed.

## UX Rules

- Every final book must support previous/next buttons.
- Buttons must be large enough for young children to use.
- Support swipe gestures and keyboard navigation.
- Include page progress.
- Respect `prefers-reduced-motion`.
- Include image alt text.
- Include visible credits and sources in the book.

## Output Rules

### Research Agent

Must produce:
- `books/{slug}/content.json`
- `books/{slug}/images/*`

### Author Agent

Must produce:
- `books/{slug}/book.json`

### Build Agent

Must produce:
- `books/{slug}/index.html`
- `books/{slug}/style.css`
- `books/{slug}/script.js`

Optional:
- additional assets inside `books/{slug}/`

## Review Boundaries

- Human review happens after `content.json` and after `book.json`.
- The build agent should assume `book.json` is the approved source of truth.
