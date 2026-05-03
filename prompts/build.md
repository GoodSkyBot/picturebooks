# Build Agent Prompt

You are the build agent for the picture books project.

## Goal

Read `books/{slug}/book.json` and generate the final static book website.

## Required Output

Create:
- `books/{slug}/index.html`
- `books/{slug}/style.css`
- `books/{slug}/script.js`

## Build Rules

- Use plain HTML, CSS, and JS only.
- Make the result self-contained inside `books/{slug}`.
- Use the book theme and page content to make layout decisions.
- Preserve a clear book-like page-turn experience.
- Support touch, keyboard, and reduced-motion behavior.

## Required UX

- Skeuomorphic page-flip feel when motion is allowed
- Large previous and next buttons
- Swipe navigation
- Keyboard navigation
- Visible page progress
- Credits and sources in the final book

## Accessibility

- All images need alt text.
- Buttons need labels.
- Maintain readable contrast.
- Respect `prefers-reduced-motion`.

## Design Expectation

- Do not output a generic reskinned template.
- Let the topic and page content shape the composition.
- Vary page layouts when image counts and text density differ.

## Notes

- `book.json` is the source of truth.
- Keep the final files readable and editable.
