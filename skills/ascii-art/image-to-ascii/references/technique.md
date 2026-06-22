# The shape-vector technique (implementation notes)

Background reading: Alex Harri, "[ASCII characters are not pixels: a deep dive into
ASCII rendering](https://alexharri.com/blog/ascii-rendering)". The geometry and
contrast math below are ported from the MIT-licensed
[`ascii-img-react`](https://github.com/mrmartineau/ascii-img-react) (`src/lib/`), so
this converter and that React component produce visually consistent output. This file
documents what `scripts/image_to_ascii.py` actually does, so you can extend or debug
it.

## Why not a brightness ramp

A brightness ramp maps a cell's average lightness to one character on a scale like
`" .:-=+*#%@"`. That is nearest-neighbour downsampling: each cell is a pixel, so
edges staircase. Supersampling (averaging more samples per cell) just blurs it into a
low-res grey image. Both ignore that a glyph has **shape** — `/`, `_`, and `^` carry
their ink in different places. The fix is to compare shapes, not scalars.

## 6D shape vectors

Each cell gets six sampling circles in a staggered 2×3 grid. Positions are fractions
of the cell (left column dropped, right column raised — this stagger is what lets the
vector distinguish `p` from `q` and `^` from `_`):

```
CIRCLE_POSITIONS = [
  (0.25, 0.17), (0.75, 0.25),   # top    (L lower, R higher)
  (0.25, 0.50), (0.75, 0.50),   # middle
  (0.25, 0.75), (0.75, 0.83),   # bottom (L higher, R lower)
]
```

Circle radius is `0.25 × (cellW + cellH) / 2`. Each circle's value is the average of
sample points inside it — sample offsets are a `ceil(sqrt(n))×ceil(sqrt(n))` grid
clipped to the unit circle (with `n=9` that is the 5-point plus pattern, matching the
package). A glyph's value per circle is the fraction of sample points landing on ink;
an image cell's value is the average **density** of those points.

## Glyph vectors: rasterized, then normalized

`compute_char_vectors` renders each glyph white-on-black in its true monospace cell
(`advance × (ascent+descent)` at a large font size for smooth fractions), samples the
six circles over the ink mask, then **normalizes by the per-component maximum across
all glyphs** so the vectors span `[0,1]` (raw overlaps cluster low otherwise). Results
are cached in the temp dir keyed by font + charset + geometry, since they only depend
on those.

This is deliberately *more* faithful than `ascii-img-react`, which ships ~95
hand-approximated vectors. Rasterizing real glyphs means any `--charset` or `--font`
works, and the `png`/`svg` renderers draw with the same font.

## Image cells and polarity

The image is resized so the sampling grid is `cols × rows` of `6 × round(6×aspect)`
pixel cells. Lightness uses **Rec.709 relative luminance**:

```
L = (0.2126·R + 0.7152·G + 0.0722·B) / 255
```

The per-circle value is a **density**: `1 − L` by default (dark → dense, correct for
dark text on a light page) or `L` with `--invert` (bright → dense, for light-on-dark).
Out-of-bounds samples read as 0, matching the package.

## Contrast enhancement

**Global** (`--contrast`, default 1.5; `1` = off) sharpens light/dark separation by
crunching the darker components while leaving the lightest and near-uniform vectors
(smooth gradients) almost untouched:

```
m = max(vector); v -> (v/m)**exponent * m   # per component
```

**Directional** (`--directional`, off by default; exponent `--directional-exp`,
default 2.0) fixes staircasing at hard boundaries where a cell has no light samples
left for global contrast to act on. Ten external circles reach into neighbouring
cells; each internal component takes the `max` with its affecting external components
before the same normalize/exponent/denormalize. The mapping (ported verbatim, using
the package's external-circle ordering — note this differs from the blog's ordering):

```
AFFECTING_EXTERNAL_INDICES = [
  [0, 1, 2, 8], [0, 1, 3, 8],
  [2, 4, 0, 6], [3, 5, 1, 7],
  [4, 6, 9, 2], [5, 7, 9, 3],
]
```

Directional is applied first, then global (matching `applyFullContrast`).

## Lookup

For each cell, pick the glyph with the smallest **squared** Euclidean distance to the
(contrast-enhanced) cell vector — squared, because skipping `sqrt` gives the same
argmin. Brute force over ~95 glyphs × cells is trivially fast for a one-shot. The
package also keeps a 5-bit-quantized cache key (`(key << 5) | floor(v·32)`) for its
real-time loop; this converter does not need it but the structure is there if you
animate.

## Extending

- **Different look:** pass `--charset` (e.g. block characters, a custom ramp) — vectors
  recompute and re-cache automatically.
- **Higher fidelity sampling:** raise `--samples` (image grid) or `GLYPH_SAMPLES` (glyph
  vectors) in the script.
- **Match `ascii-img-react` exactly:** it defaults to `contrast 1.5`,
  `directionalContrast 2` with directional **on**; the polarity differs (it maps
  lightness → density, i.e. our `--invert`).
