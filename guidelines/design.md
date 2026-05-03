# Design Guidelines

## Core Principles

Each book should feel designed for its topic, not generated from the same template.

Every page must fit entirely within the viewport without scrolling. This applies to all screen sizes including mobile. Layouts should use the full available screen space rather than leaving large empty areas. Never require the reader to scroll to see content or controls on a single page.

## Theme Expectations

The theme should define:
- primary and supporting colors
- heading and body fonts
- overall mood
- decorative motif
- layout density and rhythm

## Visual Variation

- Vary cover composition by topic.
- Vary page layouts based on image count and text density.
- Let the topic influence decorative details.
- Do not rely on color swapping alone.

## Typography

- Use readable, kid-friendly Google Fonts.
- Headings can be playful.
- Body text must stay highly legible.
- Do not use more than two font families in a book unless there is a clear reason.

## Color and Contrast

- Maintain readable contrast for all text.
- Avoid harsh pure-white backgrounds when a warmer tone fits better.
- Accent colors should support navigation and callouts.

## Decorative Elements

- Decorations should reinforce the topic.
- Decorations should not block text or obscure photos.
- Use motifs sparingly enough that pages stay calm and readable.
- On viewports narrower than 480px, scale down or hide decorative pseudo-elements that consume layout space. Prioritize reading area over ornamentation.

## Mobile Visual Hierarchy

On small screens the image is the anchor of each page. Layout should feel like a storybook held in the hands, not a shrunken desktop page.

- Image-dominant pages should let the image span the full content width with rounded corners or a subtle inset, not a small thumbnail floating in whitespace.
- Text blocks should feel like gentle cards sitting below or overlaying the bottom of the image, not squeezed beside it.
- Keep vertical rhythm tight. Padding and gaps should shrink proportionally so content fits the viewport without scrolling.
- Body text must never render smaller than 1rem on mobile. If space is tight, reduce image height before reducing text size.
- Extras (fact bubbles) should wrap naturally and may hide on very small viewports if the page would otherwise overflow.
- Cover pages should give the hero image the majority of the viewport, with the title overlaid or placed directly below.
