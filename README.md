# Picture Books

Create nonfiction picture-book websites for kids ages 3-8 using OpenCode agents.

Each book is published as a self-contained static site. The initial deploy scaffold serves books at paths such as `/books/frogs/` or `/books/snakes/`.

## Workflow

1. Run the research agent to gather sourced facts and Creative Commons images.
2. Review `books/{slug}/content.json` and downloaded images.
3. Run the author agent to write the book and generate a theme.
4. Review or edit `books/{slug}/book.json`.
5. Run the build agent to generate the final static site.
6. Deploy to Dokku.

## Repository Layout

```text
.
├── AGENTS.md
├── README.md
├── books/
├── deploy/
├── examples/
├── guidelines/
├── prompts/
└── schemas/
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

Image references stored in JSON should use relative paths with folders, for example `images/tree-frog.jpg`.

## Agents

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

### Build Agent

Reads `book.json` and generates plain HTML, CSS, and JS.

It must:
- preserve the skeuomorphic page-flip interaction
- support large touch-friendly navigation
- work on phones and tablets
- produce a visually distinct book instead of a generic reskin

## Slash Commands

Project-local OpenCode slash commands live in `.opencode/commands/`:
- `/research`
- `/author`
- `/build`

Use them in order with human review between stages.

## JSON Contracts

Schemas live in `schemas/`:
- `content.schema.json`
- `book.schema.json`

## Deployment

Dokku serves the generated `books/` directory as a static site.

Current path routing:
- `/` lists available books
- `/books/{slug}/` serves `books/{slug}/index.html`

Clean `/{slug}` routing can be added later with explicit nginx rewrites or a publish step that mirrors generated book folders to the repo root.

Deployment notes live in `deploy/deploy.md`.

## Development Strategy

Start with one book, then generate a second very different topic to prove the prompts, schemas, and build constraints are not overfit to the first example.
