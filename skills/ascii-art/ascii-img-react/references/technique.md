# The shape-vector technique (and how the props map onto it)

Source: Alex Harri,
"[ASCII characters are not pixels](https://alexharri.com/blog/ascii-rendering)".
`ascii-img-react` implements it (`src/lib/`). This note explains what the component
does under the hood so you can reason about the `contrast` / `directionalContrast`
props instead of guessing.

## Why edges stay sharp

A brightness ramp maps a cell's average lightness to one glyph on a `" .:-=+*#%@"`
scale — nearest-neighbour downsampling, so edges staircase. `<AsciiImage>` instead
reduces each cell to a **6D shape vector**: six sampling circles in a staggered 2×3
grid (left column lowered, right raised), each circle's value being the average
lightness inside it. It then picks the character whose own 6D vector is closest
(squared Euclidean). Because the comparison is over *shape*, a diagonal edge selects
`/` or `\`, a top bar `"`/`^`, a base `_`.

Geometry (from `DEFAULT_GRID_CONFIG`): `cellWidth 6`, `cellHeight 12`,
`samplesPerCircle 9`, `circleRadius 0.25`. `cellWidth`/`cellHeight` props change the
sampling resolution, not the character count (that is `width`/`height`).

## `contrast` — global contrast enhancement

`contrast` is the exponent in: normalize the cell's vector by its max, raise each
component to the exponent, denormalize.

```
m = max(vector); v -> (v/m)**contrast * m
```

It crushes the darker components toward zero while leaving the brightest and any
near-uniform vector (a smooth gradient) almost untouched — a cel-shading-like
sharpening. `1` disables it; the default `1.5` is gentle; push to `3`–`6` for hard,
poster-like edges. Too high flattens gradients.

## `directionalContrast` — fixing staircases

Once a boundary cell has no light samples left, global contrast can't do more and
edges staircase. Directional contrast (`enableDirectionalContrast`, exponent
`directionalContrast`, default `2`) samples **ten external circles** reaching into
neighbouring cells; each internal component takes the `max` with its affecting
external components before the same normalize/exponent/denormalize step. This
"spreads" contrast along edges so hard colour boundaries (logos, 3D renders) stay
crisp. It is applied **before** global contrast.

If a render looks soft inside shapes: raise `contrast` first; if hard *edges between
regions* staircase, raise `directionalContrast` (and confirm
`enableDirectionalContrast` is on). On soft photographic content, heavy directional
contrast can over-sharpen — back it off.

## Character vectors

The package ships ~95 hand-approximated character vectors (`CHARACTERS`) and uses the
per-component-normalized `NORMALIZED_CHARACTERS` for matching. They are tuned for a
typical monospace font; results "look best with monospace fonts" for exactly this
reason. (The sibling `image-to-ascii` CLI instead rasterizes real glyphs for its
vectors — useful context if you ever want to regenerate or extend the set.)

## Animation

Ripple/rain perturb each cell's sampling vector by a wave value before lookup, so the
chosen glyph shifts as the wave passes — the ASCII itself ripples, not a CSS overlay.
This re-runs the per-cell lookup every frame, which is why wide grids (>~150 cols)
can stutter.

## Doing it yourself

The same pipeline is exported as utilities (`sampleCell` → `applyFullContrast` →
`cachedLookup.findBest`) for custom canvases or non-React use — see
`references/component-api.md`.
