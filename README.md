# Picture Books

Create nonfiction picture-book websites for kids ages 3-8 using AI agents.

Each book is published as a self-contained static site under `books/{slug}/`.

## Workflow

1. Run the research agent to gather sourced facts and Creative Commons images.
2. Review `books/{slug}/content.json` and downloaded images.
3. Run the author agent to write the book and generate a theme.
4. Review or edit `books/{slug}/book.json`.
5. Run the build agent to generate audio and the final static site.

## Repository Layout

```text
.
├── AGENTS.md              # Shared agent contract and rules
├── index.html             # Home page listing all books
├── serve.sh               # Local dev server
├── agents/                # Agent instructions
│   ├── research.md
│   ├── author.md
│   └── build.md
├── guidelines/            # Writing and design standards
│   ├── content.md
│   ├── design.md
│   └── ux.md
├── schemas/               # JSON schema definitions
│   ├── content.schema.json
│   └── book.schema.json
├── scripts/               # Automation utilities
│   ├── generate_image.py
│   ├── optimize_images.py
│   └── generate_speech.py
└── books/                 # Generated books
    └── {slug}/
```

## Book Creation

Inputs:
- topic
- target age

Outputs:
- `books/{slug}/content.json`
- `books/{slug}/book.json`
- `books/{slug}/index.html`
- `books/{slug}/style.css`
- `books/{slug}/script.js`
- `books/{slug}/images/*`
- `books/{slug}/audio/*`

Image references stored in JSON should use relative paths with folders, for example `images/tree-frog.jpg`.

## Agents

Agent instructions live in `agents/`. Guidelines live in `guidelines/`.

### Research Agent

Reads external sources and produces `content.json` plus a pool of attributed images.

Primary sources:
- Wikipedia
- Wikimedia Commons
- other reputable references when needed for clarification or cross-checking

### Author Agent

Reads `content.json` and produces `book.json`.

It decides:
- page count
- age-appropriate voice
- page-by-page text
- optional fact bubbles
- image assignments
- theme metadata

Can generate missing images via `scripts/generate_image.py`.

### Build Agent

Reads `book.json` and generates plain HTML, CSS, and JS.

It must:
- preserve the skeuomorphic page-flip interaction
- support large touch-friendly navigation
- work on phones and tablets
- produce a visually distinct book instead of a generic reskin

Generates narration audio via `scripts/generate_speech.py`.

Image files checked into `books/{slug}/images/` should be web/review-sized project copies, not source-resolution originals. `content.json` preserves source URLs, attribution, and license metadata so originals can be retrieved again if needed. Use `scripts/optimize_images.py` during research, or during build for older books that still contain oversized files.

## Invocation

Agents can be invoked two ways:

- **OpenCode** slash commands in `.opencode/commands/`: `/research`, `/author`, `/build`
- **VS Code Copilot** prompt files in `.github/prompts/`: `research.prompt.md`, `author.prompt.md`, `build.prompt.md`

Use them in order with human review between stages.

## JSON Contracts

Schemas live in `schemas/`:
- `content.schema.json`
- `book.schema.json`

## Local Preview

```bash
./serve.sh [port]
```

Starts a local server (default port 8000). Visit `/` for the book listing or `/books/{slug}/` for a specific book.

## Visual QA

Install Chromium with apt, then run:

```bash
npm install
npm run visual-qa -- american-revolution
```

The QA script uses system Chromium at `/usr/bin/chromium`, flips through every `.page` at mobile, tablet, and desktop sizes, and writes screenshots plus `report.json` under `tmp/screenshots/{slug}/`.
