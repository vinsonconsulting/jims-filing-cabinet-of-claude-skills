---
name: ascii-img-react
description: Use when rendering images as ASCII art in the browser or a React app with
  the ascii-img-react library — the shape-vector (not brightness-ramp) approach that
  keeps edges sharp. Trigger when ascii-img-react or <AsciiImage> is named; when the
  user wants an image-to-ASCII React component, a terminal/retro ASCII image effect on
  a web page, a click-ripple or rain ASCII animation over an image, or to theme ASCII
  output via CSS variables; or when they reach for the low-level utilities (sampleCell,
  sampleGrid, sampleExternalCircles, findBestCharacter, CachedCharacterLookup,
  applyGlobalContrast / applyDirectionalContrast, NORMALIZED_CHARACTERS). Covers
  install, the <AsciiImage> props, CORS/sizing/performance caveats, CSS-variable
  theming, Astro/Next integration, and the 6D shape-vector technique it implements. Not
  for converting an image file to ASCII from the command line in Python (use
  image-to-ascii), and not for real-time generative textmode graphics on a WebGL grid
  (use textmode-js).
---

# ascii-img-react

`ascii-img-react` renders an image as ASCII art in React via an `<AsciiImage>`
component. It matches each grid cell to the character whose **shape** fits best (6D
shape vectors + nearest-neighbour), so edges stay crisp — unlike a brightness ramp.
Pin a version: the package is young (`0.1.0`, MIT). Install + props live below; the
full API is in `references/component-api.md`, the algorithm in
`references/technique.md`.

## Mental model

- Characters are matched by **shape, not brightness**. Six staggered sampling circles
  per cell form a 6D vector; the nearest character (Euclidean distance) wins. That is
  why diagonals and curves render as `/`, `\`, `_` rather than a blocky ramp.
- The component samples the image on a hidden `<canvas>`, so the **image must be
  same-origin or CORS-enabled** (`img.crossOrigin = "anonymous"`). A cross-origin
  image without CORS headers renders blank.
- It outputs a `<pre>` of monospace text. **Monospace fonts only** — proportional
  fonts break the grid.
- The `contrast` and `directionalContrast` props are exactly the global and
  directional contrast-enhancement exponents from the technique (see
  `references/technique.md`).

## Install

```sh
npm add ascii-img-react@0.1.0     # or: bun add / pnpm add / yarn add
```

Peer deps: React 18 or 19 (`react`, `react-dom`).

## Usage

```tsx
import { AsciiImage } from 'ascii-img-react';

export function Hero() {
  return (
    <AsciiImage
      src="/portrait.jpg"        // same-origin or CORS-enabled
      width={100}                 // output width in CHARACTERS
      color="#39ff14"             // green
      backgroundColor="#000"
      enableRipple={false}
    />
  );
}
```

`width`/`height` are in **characters**. `cellWidth`/`cellHeight` (px, default 6×12)
set the sampling resolution. Defaults that matter: `contrast={1.5}`,
`directionalContrast={2}`, `enableDirectionalContrast`, `enableRipple`, `fontSize={10}`,
`lineHeight={0.8}`. Full prop table in `references/component-api.md`.

## Theming with CSS variables

Set the `--ascii-*` variables on a shared class and pass it via `className` to theme
every instance at once (props still win per-instance):

```css
.ascii {
  --ascii-font-family: 'Fira Code', monospace;
  --ascii-font-size: 12px;
  --ascii-line-height: 0.85;
  --ascii-color: #c8d3f5;
  --ascii-background: #1a1b26;
}
@media (prefers-color-scheme: light) {
  .ascii { --ascii-color: #1a1b26; --ascii-background: #e1e2e7; }
}
```

```tsx
<AsciiImage src="/portrait.jpg" width={120} className="ascii" />
```

`--ascii-font-family` works even though it looks commented out in the source — the
container falls back through `var(--ascii-font-family, monospace)`.

## Sharpening a mushy render

Internal edges look soft? Raise `contrast` (global, default 1.5) and/or
`directionalContrast` (default 2, needs `enableDirectionalContrast`). Global contrast
separates light/dark across the whole cell; directional contrast samples neighbouring
cells to fix staircasing at hard boundaries. See the global-vs-directional explanation
in `references/technique.md`.

## Animation: ripple and rain

- `enableRipple` (default true) makes clicks send a wave that perturbs the sampling
  vectors. Tune `rippleCount` and `rippleConfig` (`speed`, `amplitude`, `decay`,
  `wavelength`, `duration`).
- `enableRain` (default false) auto-spawns drops; tune `rainConfig` (`intensity`,
  `variation`).

Animation has a cost: **grids wider than ~150 columns can stutter.** For large output,
shrink `width` or set `enableRipple={false}`.

## Low-level utilities

For a custom pipeline (your own canvas, caching, or non-React use), import from the
package root: `sampleCell` / `sampleGrid` / `sampleExternalCircles`, `rgbToLightness`,
`DEFAULT_GRID_CONFIG`, `findBestCharacter` / `CachedCharacterLookup` / `cachedLookup`,
`CHARACTERS` / `NORMALIZED_CHARACTERS`, `applyGlobalContrast` /
`applyDirectionalContrast` / `applyFullContrast`. Reach for these only when
`<AsciiImage>` can't express what you need; otherwise the component is the path. Full
signatures in `references/component-api.md`.

## Framework notes

- **Next.js / Astro:** `<AsciiImage>` is a client component (uses `useEffect`,
  `<canvas>`). In Next App Router add `"use client"`; in Astro give it a
  `client:load`/`client:visible` directive. Serve the image same-origin (e.g. from
  `/public`) to avoid CORS entirely.

## Boundary — when NOT to use this

- Converting an **image file to ASCII on the command line / in Python** → use
  **image-to-ascii**.
- A **real-time, generative** textmode sketch on a WebGL character grid (webcam,
  shaders, VJ visuals) → use **textmode-js**.

## Attribution

Technique: Alex Harri,
"[ASCII characters are not pixels](https://alexharri.com/blog/ascii-rendering)".
Library: MIT-licensed
[`ascii-img-react`](https://github.com/mrmartineau/ascii-img-react).
