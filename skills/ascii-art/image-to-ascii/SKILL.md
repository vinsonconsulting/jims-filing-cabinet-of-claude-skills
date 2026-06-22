---
name: image-to-ascii
description: Use when converting an image file to ASCII art outside the browser — a
  command-line or script run that turns a photo, logo, screenshot, or render into
  text, saved as .txt or rendered to .png/.svg. Trigger on "make ASCII art of this
  image/photo/cat", "convert this picture/logo to ASCII", "turn this PNG into an
  ASCII text file for my README", batch-converting a folder of images to ASCII, or
  any Python/Pillow image-to-ASCII task. Produces sharp, shape-aware output by
  matching each cell to the glyph whose shape fits best (6D shape vectors +
  nearest-neighbour, optional contrast enhancement) rather than a naive brightness
  ramp, and bundles a monospace font for deterministic results. Runs
  scripts/image_to_ascii.py. Not for ASCII graphics on a web page or in React (use
  ascii-img-react), not the real-time textmode.js library (use textmode-js), and not
  figlet-style text banners (this converts images, not words).
version: 0.1.0
summary: Convert an image file to ASCII art from the command line with shape-aware glyph matching (6D
  shape vectors, not a brightness ramp), output as .txt or a rendered .png/.svg, using a bundled monospace
  font for deterministic results.
output:
  type: ASCII art
  format: .txt, .png, or .svg produced by scripts/image_to_ascii.py (a shell invocation)
dependencies:
- Pillow
- python>=3.9
external_endpoints: none
permissions:
  network: false
  shell: true
  file: true
  env: false
  mcp: false
card_version: '1.0'
inputs:
- 'An image file (PNG/JPG/etc.) plus options: --cols, --out/--format, --invert, --contrast.'
triggers:
  positive:
  - make ASCII art of this photo
  - convert this logo PNG to an ASCII text file for my README
  - turn this screenshot into ASCII art saved as a .txt
  - batch-convert a folder of images to ASCII art
  - render this image as an ASCII .png, white text on black
  - sharpen the edges on my logo's image-to-ASCII conversion
  negative:
  - prompt: render an image as ASCII art in a React component or on a web page
    use_instead: ascii-img-react
  - prompt: build a real-time generative textmode sketch (webcam, animation, WebGL)
    use_instead: textmode-js
  - prompt: make a figlet-style ASCII banner from a word
    use_instead: figlet/toilet text-banner tools (this converts images, not words)
---

# image-to-ascii

Convert an image file to ASCII art from the command line — to stdout, a `.txt` file,
or a rendered `.png`/`.svg` — using shape-aware glyph matching. The converter is
`scripts/image_to_ascii.py`: Pillow-only, pure-Python, Python 3.9+.

## Mental model

- A naive ASCII converter picks one glyph per cell off a brightness ramp
  (`" .:-=+*#%@"`). That is nearest-neighbour downsampling — every cell is treated as
  a pixel, so edges come out jagged and curves look like staircases.
- This converter instead reduces **both** each glyph **and** each image cell to a
  **6D shape vector** (six staggered sampling circles in a 2×3 grid) and matches the
  glyph whose *shape* is closest. A diagonal edge picks `/` or `\`, a top bar picks
  `"`/`^`, a base picks `_`. Edges stay crisp because shape, not just average
  brightness, drives the choice.
- Glyph vectors are computed by **actually rasterizing the bundled font**, so the
  match reflects the real ink — and `png`/`svg` output draws with that same font, so
  the rendered image is self-consistent with the text.
- **Polarity:** by default **dark pixels → dense glyphs** (`@`, `#`), which looks
  right as text on a light background (a README, a `.txt`). For light-on-dark output
  (terminal style, e.g. white-on-black), add `--invert`.

For the full technique — circle geometry, the contrast-enhancement formulas, the
luminance coefficients, caching — read `references/technique.md`.

## Setup

The converter needs Pillow (nothing else):

```sh
python3 -m pip install Pillow
```

The monospace font ships in `assets/DejaVuSansMono.ttf` (with its license), so output
is deterministic on any machine. No system fonts are required.

## Usage

```sh
# Print 80-column ASCII to stdout
python3 scripts/image_to_ascii.py photo.jpg --cols 80

# Save a .txt for a README
python3 scripts/image_to_ascii.py logo.png --cols 100 --out logo.txt

# Render a PNG, white text on black (terminal look — note --invert for correct tones)
python3 scripts/image_to_ascii.py photo.jpg --cols 120 --invert \
  --format png --fg white --bg black --out photo.png

# Sharper edges on a high-contrast logo / 3D render
python3 scripts/image_to_ascii.py render.png --cols 100 --contrast 4 --directional
```

Run from the skill directory, or pass an absolute path to the script. Batch a folder
with a shell loop over the files, reusing the same flags.

## Flags

| Flag | Default | What it does |
| --- | --- | --- |
| `--cols` / `--width` | 80 | Output width in characters (rows follow from image aspect) |
| `--contrast` | 1.5 | Global contrast exponent (`1` = off); separates light/dark |
| `--directional` | off | Sample neighbours too, to sharpen hard edges (see below) |
| `--directional-exp` | 2.0 | Exponent for directional contrast |
| `--invert` | off | Map **bright** pixels to dense glyphs (light-on-dark output) |
| `--charset` | printable ASCII 32–126 | Glyph set to match against |
| `--cell-aspect` | from font (~1.94) | Character height/width; the default keeps the picture undistorted |
| `--out` | stdout | Output file (format inferred from extension) |
| `--format` | `txt` (or from `--out`) | `txt`, `png`, or `svg` |
| `--fg` / `--bg` | `#000000` / `transparent` | Colors for `png`/`svg` (name or `#hex`) |
| `--color` | off (mono) | Colorize each cell with the image's average color |
| `--font` | bundled DejaVu Sans Mono | Override the `.ttf` |
| `--font-size` / `--line-height` | 14 / 1.0 | `png`/`svg` rendering size and line spacing |

## Choosing output and options

- **Plain text / README** → `txt` (the default), default polarity. Keep `--cols` ≤ the
  width you can display; 80–120 is typical.
- **An image to embed** → `png`. Use `--invert --fg white --bg black` for a terminal
  aesthetic, or default `--fg` dark on a light `--bg` for print.
- **Crisp, scalable** → `svg` (vector, themeable later via the font-family).
- **Edges look mushy** on a logo or 3D render → raise `--contrast` first (e.g. `4`),
  then add `--directional`. Directional contrast mainly helps hard colour
  boundaries; on soft photos it can over-sharpen, so it is off by default.
- **`--color`** writes ANSI escapes for `txt` to stdout (terminal only — saved `.txt`
  stays clean), and per-glyph colors for `png`/`svg`.

## Boundary — when NOT to use this

- Rendering an image as ASCII **in a web page or React** → use **ascii-img-react**.
- A **real-time, generative** textmode/ASCII sketch (webcam, animation, WebGL) → use
  **textmode-js**.
- A **text banner** of a word (figlet/toilet) → that draws letters from words; this
  converts pictures.

## Attribution

The shape-vector technique is from Alex Harri's
"[ASCII characters are not pixels](https://alexharri.com/blog/ascii-rendering)". The
circle geometry and contrast math are ported from the MIT-licensed
[`ascii-img-react`](https://github.com/mrmartineau/ascii-img-react) package. The
bundled font is DejaVu Sans Mono (license in `assets/DejaVuSansMono-LICENSE.txt`).
