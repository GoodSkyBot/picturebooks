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
- On mobile, invisible tap zones replace visible buttons but must still meet the 64px minimum width.
- All interactive elements need a visible `:active` state (scale change or color shift) since `:hover` is meaningless on touch devices.

## Page Flip

- Default interaction should feel like turning pages in a book.
- Use a skeuomorphic flip treatment when motion is allowed.
- Keep animation short enough to stay responsive.

## Reduced Motion

- Respect `prefers-reduced-motion`.
- Replace page flips with a simpler transition when reduced motion is enabled.

## Responsive Layout

- The book should work on phones, tablets, and desktop screens.
- Tablet and phone use are primary targets.
- Avoid hover-only interactions.
- The smallest supported viewport is 412x915 (Pixel 7). Every page must fit without scrolling at this size.

## Mobile Layout

On viewports narrower than 480px:

- Remove horizontal margins around the book container. Content should fill edge-to-edge, respecting safe areas only.
- Use portrait-aware composition: image occupies roughly 45-55% of viewport height on top, text sits below.
- Do not force desktop side-by-side layouts onto portrait phones. Let grid columns collapse to a single column with intentional vertical proportions, not just a stack of whatever fits.
- Image pairs should remain side-by-side when both images are small, but stack vertically if each image needs more space.
- Cover pages should stack the image above the title and call-to-action, giving the image most of the viewport.

## Mobile Navigation

Swiping is the primary interaction on touch devices. Buttons are a secondary affordance.

- On viewports narrower than 480px, replace visible nav buttons with invisible full-height tap zones covering the left and right 20% of the screen. This preserves full content width for the child.
- Each tap zone must be at least 64 CSS pixels wide regardless of viewport width.
- Show a brief visual ripple or highlight when the child taps a zone, so the interaction feels responsive.
- On the first page load, display a transient swipe-to-read hint (e.g., an animated hand icon with "Swipe" label). Auto-dismiss after a few seconds or on the first interaction.
- On viewports 480px and wider, continue using visible overlay buttons as described in Navigation Chrome.

## Safe Areas

- Use `env(safe-area-inset-left)`, `env(safe-area-inset-right)`, and `env(safe-area-inset-bottom)` to pad content away from notches, camera cutouts, and home-indicator gesture zones.
- Navigation tap zones and interactive controls must not sit behind system gesture areas.
- Apply safe-area padding to the outermost container so inner layout math stays clean.

## Orientation

- Use `@media (orientation: portrait)` to trigger stacked image-above-text layouts.
- Use `@media (orientation: landscape)` to allow side-by-side layouts even on phones.
- A phone held landscape should feel closer to a tablet reading experience, not a squished version of the portrait layout.
- Test both orientations; do not assume readers will stay in one.

## Fullscreen

- Offer a fullscreen toggle using the Fullscreen API so children can read without browser chrome.
- Show the toggle on the cover page. Once activated, auto-hide the control to maximize content space.
- Provide a way to exit fullscreen (e.g., tap a corner icon or press Escape).
- Do not require fullscreen for the book to work correctly.

## Accessibility

- Add alt text to every image.
- Label buttons and interactive controls.
- Ensure keyboard navigation works.
- Maintain readable contrast.

## Credits and Sources

- Show source and image attribution information in the final book.
- Keep page-level credit display unobtrusive but present.
- Include a dedicated credits or sources page in the back matter.
