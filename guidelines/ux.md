# UX Guidelines

## Navigation

Every book must support:
- previous and next buttons
- swipe navigation on touch devices
- keyboard navigation with left and right arrows

## Navigation Chrome

- Do not show a persistent title bar or page progress indicator on every page. Maximize content area.
- Render previous/next buttons as overlays on the left and right edges of the content area.
- Buttons should be semi-transparent and unobtrusive but still easily tappable by young children.
- Do not add a separate header or footer bar that consumes vertical space.

## Touch Targets

- Navigation controls should be easy for small children to tap.
- Aim for at least 64x64 CSS pixels for the button hit area.

## Page Flip

- Default interaction should feel like turning pages in a book.
- Use a skeuomorphic flip treatment when motion is allowed.
- Keep animation short enough to stay responsive.

## Reduced Motion

- Respect `prefers-reduced-motion`.
- Replace page flips with a simpler transition when reduced motion is enabled.

## Responsive Layout

- The book should work on phones, tablets, and desktop screens.
- Tablet use is a primary target.
- Avoid hover-only interactions.

## Accessibility

- Add alt text to every image.
- Label buttons and interactive controls.
- Ensure keyboard navigation works.
- Maintain readable contrast.

## Credits and Sources

- Show source and image attribution information in the final book.
- Keep page-level credit display unobtrusive but present.
- Include a dedicated credits or sources page in the back matter.
