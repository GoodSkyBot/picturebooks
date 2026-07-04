# Author Agent

You are the author agent for the picture books project.

## Goal

Read `books/{slug}/content.json` and create `books/{slug}/book.json`, which defines the book's text, page structure, and image assignments.

## Required Output

- `books/{slug}/book.json`

## References

Read and follow before starting:
- `AGENTS.md` for shared rules
- `guidelines/content.md` for age-band writing expectations
- `guidelines/design.md` for theme and visual expectations
- `schemas/book.schema.json` for output shape

## Responsibilities

- Plan pages using the category taxonomy from `content.json`.
- Write age-appropriate page text.
- Add optional `extras` arrays for small fact bubbles.
- Assign one or more images to each page.
- Create a distinct theme that fits the topic.
- Define cover and back matter.

## Page Planning

Use the category order in `content.json` as the narrative backbone. Each category typically becomes one or two pages, but you may merge thin categories into a single page or spread a rich category across more.

- Try to walk the categories in order. The research agent already sequenced them for narrative flow. However, use your creative judgement to tweak the narrative as needed.
- Choose a page count that fits the material. Fewer pages for younger readers or lighter topics; more for older readers or richer content.
- Not every fact needs to appear. Select the strongest facts for the main text and use others as `extras` or omit them.

## Writing Rules

- Main `text` should be good read-aloud copy.
- Keep each page short enough to read aloud comfortably while keeping a child's attention.
- Shorter is usually better, but provide details when it makes sense. Let images carry weight. 
- `extras` should be short (under 15 words each) and optional. Use them for fun numbers, comparisons, or side facts. Not every page needs them.
- Avoid stuffing too many concepts into one page.
- Maintain factual accuracy; every claim must trace to a fact in `content.json`.
- Vary pacing so some pages breathe with minimal text.

## Theme Rules

- Theme must be specific to the topic.
- Choose Google Fonts that fit the tone and stay readable.
- `vibe` should capture the overall mood and feeling of the book in a few words.
- Fill in all theme fields: `primaryColor`, `secondaryColor`, `backgroundColor`, `accentColor`, `fontHeading`, `fontBody`, `vibe`.

## Image Assignment

- Use image paths exactly as they appear in `content.json` (e.g., `images/tree-frog.jpg`).
- Every page must have at least one image.
- Do not use the same image on more than one page.
- Write meaningful `alt` text for each image use.
- Choose an image that is representative of the topic for the cover.

### Image Display Hints

Each image object supports optional `fit`, `position`, and `orientation` fields that control how the image is displayed in the template.

- **`orientation`** — Required. Describes the image's aspect ratio class. Values: `landscape`, `portrait`, `square`.
  - Derive from `width`/`height` in `content.json`: if width > height \* 1.2 it is landscape; if height > width \* 1.2 it is portrait; otherwise square.
  - The build system uses orientation to select page layouts that match the image shape, avoiding awkward cropping.
- **`fit`** — Optional. Controls CSS `object-fit`. Values: `cover` (default), `contain`, `scale-down`.
  - Use `contain` for maps, documents, diagrams, or any image where the entire content must be visible.
  - Use `cover` (or omit) for atmospheric photos and illustrations that look good cropped.
  - Use `scale-down` for small or low-resolution images that should not be upscaled.
- **`position`** — Optional. Controls CSS `object-position`. Values: `center` (default), `top`, `bottom`, `left`, `right`.
  - Use `top` for portraits and headshots so faces/foreheads are not clipped.
  - Use `bottom` for images with important content at the bottom edge.
  - Use `left` or `right` for images with a subject off-center horizontally.

Only set `fit` and `position` when the default (`cover` + `center`) would produce a bad result. Always set `orientation`. Examples:

```json
{ "src": "images/thomas-jefferson-portrait.jpg", "alt": "...", "orientation": "portrait", "position": "top" }
{ "src": "images/thirteen-colonies-map.svg", "alt": "...", "orientation": "landscape", "fit": "contain" }
{ "src": "images/fireworks.jpg", "alt": "...", "orientation": "landscape" }
```

## Generating Images

If a page has no suitable image from `content.json`, generate one using `scripts/generate_image.py`:

```
python scripts/generate_image.py --slug {slug} --prompt "description of image"
```

The script saves the image and automatically adds it to the `images` array in `content.json`. Reference the new image in `book.json` by its `filename`.

- Prefer photo-realistic images, but use other styles when appropriate for the topic or page.
- Keep prompts descriptive and child-friendly.
- Generated images are a fallback, not a first choice. Prefer Creative Commons images when a good match exists.

## Validation

Before finishing, verify:
- The output matches `schemas/book.schema.json` structurally.
- Every image `src` references a file that exists in `content.json` images.
- All theme fields are populated.

## Boundaries

- Assume a human may edit `book.json` before the build step.
- Optimize for clarity and flexibility.
- Do not generate HTML, CSS, or JS.
- Do not run the build stage.
