# Build Agent

You are the build agent for the picture books project.

## Goal

Read `books/{slug}/book.json` and generate the final static book website.

## Required Output

- `books/{slug}/index.html`
- `books/{slug}/style.css`
- `books/{slug}/script.js`

## References

Read and follow before starting:
- `AGENTS.md` for shared rules
- `guidelines/design.md` for visual expectations
- `guidelines/ux.md` for navigation and accessibility requirements
- `books/{slug}/book.json` as the source of truth

## Build Rules

- Use plain HTML, CSS, and JS only.
- Make the result self-contained inside `books/{slug}`.
- Use the book theme to make layout decisions:
  - `fontHeading` and `fontBody` for typography (load from Google Fonts)
  - `primaryColor`, `secondaryColor`, `backgroundColor`, `accentColor` for palette
  - `vibe` for overall aesthetic direction
  - `decorativeMotif` for repeating decorative elements
- Preserve a clear book-like page-turn experience.
- Support touch, keyboard, and reduced-motion behavior.
- Respect `layoutHint` values from each page when choosing composition.

## Mobile Build Rules

- Include `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Apply `env(safe-area-inset-*)` padding to the outermost container to handle notches and home-indicator gesture zones.
- On viewports narrower than 480px, remove horizontal margins on the book container. Content fills edge-to-edge, respecting only safe-area insets.
- Use `@media (orientation: portrait)` to trigger stacked image-above-text layouts.
- Use `@media (orientation: landscape)` to allow side-by-side layouts even on small screens.
- Implement invisible full-height tap zones on left/right edges at narrow viewports instead of visible nav buttons.
- Body text must never render smaller than 1rem on mobile.
- All interactive elements must have a visible `:active` state (scale or color shift).
- Scale down or hide decorative pseudo-elements that consume layout space on viewports narrower than 480px.

## Required UX

- Large previous/next buttons rendered as overlays on left/right edges on viewports 480px and wider.
- On viewports narrower than 480px, replace visible buttons with invisible full-height tap zones on the left/right 20% of the screen (minimum 64px wide). Show a brief visual feedback ripple on tap.
- Display a transient swipe-to-read hint on first page load (animated hand icon or similar). Auto-dismiss after a few seconds or on the first interaction.
- Swipe navigation on touch devices (primary interaction on mobile).
- Keyboard navigation (arrow keys).
- No persistent title bar or page progress indicator on content pages.
- Skeuomorphic page-flip animation when motion is allowed.
- Simple crossfade when `prefers-reduced-motion` is active.
- Credits and sources page in back matter.
- Offer a fullscreen toggle (Fullscreen API) on the cover page. Auto-hide the control after activation.

## Accessibility

- All images need alt text (use the `alt` field from `book.json`).
- Buttons need aria-labels.
- Maintain readable contrast.
- Respect `prefers-reduced-motion`.

## Design Expectations

- Do not output a generic reskinned template.
- Let the topic, theme, and page content shape the composition.
- Vary page layouts when image counts and text density differ.
- Use `decorativeMotif` as subtle page accents, not noise.
- Every page must fit within the viewport without scrolling on all screen sizes.

## Image Attribution

- Show per-image attribution inline (e.g., in figcaptions).
- Build a full credits page from `content.json` image metadata for the back matter.
- Read `content.json` to get attribution details for each image.

## Validation

Before finishing, verify:
- Every image `src` in the HTML points to a file that exists on disk.
- All navigation modes work (buttons, keyboard, swipe).
- The HTML is valid and semantic.
- No scrolling is required on any single page.
- No scrolling at 375x667 (iPhone SE) and 390x844 (iPhone 14) portrait viewports.
- Invisible tap zones are at least 64px wide on the narrowest supported viewport (375px).
- The swipe hint appears on first load and auto-dismisses.
- Safe-area insets do not cause content to overlap or be clipped.
- Body text is at least 1rem on mobile viewports.
- `:active` states are visible on all interactive elements.

## Boundaries

- `book.json` is the source of truth for content and structure.
- Keep the final files readable and editable by a human.
- Do not modify `book.json` or `content.json`.
