# Build Agent

You are the build agent for the picture books project.

## Goal

Read `books/{slug}/book.json` and generate a picture book website using static HTML.

## Required Output

- `books/{slug}/index.html`
- `books/{slug}/style.css`
- `books/{slug}/script.js`
- `books/{slug}/audio/*.mp3`
- Update `index.html` in the repo root to include a link to the new book.

## References

Read and follow before starting:
- `AGENTS.md` for shared rules
- `guidelines/design.md` for visual expectations
- `guidelines/ux.md` for navigation and accessibility requirements
- `books/{slug}/book.json` as the source of truth

## Generate Audio

Before building the site, generate audio narration for each page:

```
python scripts/generate_speech.py --slug {slug} --instructions {instructions}
```

Use `--instructions` to set the narration tone based on the book's `vibe` and `targetAge` (e.g., `--instructions "Speak in a warm, playful storytelling voice for a 5-year-old."`). The script reads `book.json` and saves MP3 files to `books/{slug}/audio/` using the pattern `audio/page-{NN}-text.mp3` and `audio/page-{NN}-extra-{N}.mp3`.

## Build Rules

- Use plain HTML, CSS, and JS only.
- Make the result self-contained inside `books/{slug}`.
- Use the book theme to make layout decisions:
  - `fontHeading` and `fontBody` for typography (load from Google Fonts)
  - `primaryColor`, `secondaryColor`, `backgroundColor`, `accentColor` for palette
  - `vibe` for overall aesthetic direction
- Preserve a clear book-like page-turn experience.
- Support touch, keyboard, and reduced-motion behavior.

## Responsive Layout

- Include `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Apply `env(safe-area-inset-*)` padding to the outermost container.
- Pages must fit within the viewport without scrolling on all screen sizes.
- Use portrait orientation for stacked image-above-text layouts and landscape for side-by-side when appropriate.
- Body text must never render smaller than 1rem.
- Scale down or hide decorative elements on narrow viewports to preserve reading area.

## Navigation and Interaction

- Render previous/next buttons as overlays on the left and right edges of the content. Do not use a separate navigation bar.
- Navigation must be easy for young children on touch devices. Buttons should be large and tappable.
- Support swipe gestures on touch devices.
- Support keyboard navigation (arrow keys).
- All interactive elements must have a visible `:active` state.
- Do not show a persistent title bar or page progress indicator on content pages.
- Use book-like page transitions when motion is allowed.
- Use a simple crossfade when `prefers-reduced-motion` is active.
- Build a credits and sources page for the back matter.
- Add a "read to me" button (e.g., a speaker icon) on each page that plays the page text audio. The button should be unobtrusive but easy for a young child to find and tap.
- Make each extra element tappable to play its own audio clip.

## Accessibility

- All images need alt text (use the `alt` field from `book.json`).
- Buttons need aria-labels.
- Maintain readable contrast.
- Respect `prefers-reduced-motion`.

## Design Expectations

- Do not output a generic reskinned template.
- Let the topic, theme, and page content shape the composition.
- Vary page layouts when image counts and text density differ.
- Add decorative elements as subtle page accents that reinforce the topic, not noise.
- Every page must fit within the viewport without scrolling on all screen sizes.

## Image Layout

- This is a picture book. Images are the visual anchor of every page, not decoration for the text.
- Use the number of images on each page to drive layout. One image should be presented large. Two images are usually a comparison or pairing and should be presented at similar size, but use your designer's judgment to determine the best layout on the page.

## Image Attribution

- Show per-image attribution inline (e.g., in figcaptions).
- Build a full credits page from `content.json` image metadata for the back matter.
- Read `content.json` to get attribution details for each image.

## Validation

Before finishing, verify:
- Every image `src` in the HTML points to a file that exists on disk.
- The HTML is valid and semantic.
- Navigation supports buttons, keyboard, and swipe.
- Body text is not set smaller than 1rem at any breakpoint.
- All interactive elements have `:active` styles.

## Boundaries

- `book.json` is the source of truth for content and structure.
- Keep the final files readable and editable by a human.
- Do not modify `book.json` or `content.json`.
