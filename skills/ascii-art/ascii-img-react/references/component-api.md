# ascii-img-react — API reference

Captured from the package source (`src/`) at `0.1.0`, MIT. Pin the version; the
package is young (~1★, a handful of commits), so treat the shape-vector technique as
the stable part and re-verify props on upgrade.

## `<AsciiImage>` props

| Prop | Type | Default | Notes |
| --- | --- | --- | --- |
| `src` | `string` | — (required) | Image URL; same-origin or CORS-enabled (loaded with `crossOrigin="anonymous"`) |
| `width` | `number` | auto | Output width in **characters** |
| `height` | `number` | auto | Output height in **characters** |
| `cellWidth` | `number` | `6` | Sampling cell width in px |
| `cellHeight` | `number` | `12` | Sampling cell height in px |
| `contrast` | `number` | `1.5` | Global contrast exponent (`1` = off) |
| `directionalContrast` | `number` | `2` | Directional contrast exponent |
| `enableDirectionalContrast` | `boolean` | `true` | Toggle directional contrast |
| `fontSize` | `number` | `10` | Font size (px) |
| `lineHeight` | `number` | `0.8` | Line-height multiplier |
| `enableRipple` | `boolean` | `true` | Click-to-ripple animation |
| `rippleCount` | `number` | `1` | Ripples per click (cascade, ~200ms apart) |
| `rippleConfig` | `Partial<RippleConfig>` | — | Override ripple params |
| `enableRain` | `boolean` | `false` | Auto-spawn raindrop ripples |
| `rainConfig` | `Partial<RainConfig>` | — | Override rain params |
| `color` | `string` | `inherit` | Text color (sets `--ascii-color`) |
| `backgroundColor` | `string` | `transparent` | Background (sets `--ascii-background`) |
| `className` | `string` | — | On the `<pre>`; the hook for CSS-variable theming |
| `style` | `React.CSSProperties` | — | Inline styles (override the CSS vars) |
| `onClick` | `(e: React.MouseEvent) => void` | — | Fires after the ripple is queued |

If neither `width` nor `height` is given, the image is scaled to fit within 800×600px
before sampling. `enableRain` and `rainConfig` are present in the source but not in the
README — they work the same way as ripple.

## Config types

```ts
interface RippleConfig {
  speed: number;       // ring expansion, px/s   (default 150)
  amplitude: number;   // wave strength 0–1      (default 0.4)
  decay: number;       // fade rate, higher=faster (default 2)
  wavelength: number;  // ring width, px         (default 40)
  duration: number;    // lifetime, ms           (default 2000)
}
// DEFAULT_RIPPLE_CONFIG = { speed:150, amplitude:0.4, decay:2, wavelength:40, duration:2000 }

interface RainConfig {
  intensity: number;   // drops per second       (default 3)
  variation: number;   // 0–1 random param spread (default 0.3)
}
// DEFAULT_RAIN_CONFIG = { intensity:3, variation:0.3 }
```

## CSS variables

Set on a shared class (passed via `className`) to theme all instances; props for
`color`/`backgroundColor`/`fontSize`/`lineHeight` map onto these per-instance.

| Variable | Default |
| --- | --- |
| `--ascii-font-family` | `monospace` |
| `--ascii-font-size` | `10px` |
| `--ascii-line-height` | `0.8` |
| `--ascii-color` | `inherit` |
| `--ascii-background` | `transparent` |

The container renders as `<pre>` with `white-space: pre` and `letter-spacing: 0`.

## Exported utilities (package root)

Sampling (`src/lib/sampling.ts`):

```ts
function sampleCell(imageData, cellX, cellY, config?): number[]          // 6D internal vector
function sampleExternalCircles(imageData, cellX, cellY, config?): number[] // 10D external vector
function sampleGrid(imageData, config?): { vectors: number[][]; cols: number; rows: number }
function rgbToLightness(r, g, b): number                                  // Rec.709, /255
const DEFAULT_GRID_CONFIG: GridConfig = { cellWidth:6, cellHeight:12, samplesPerCircle:9, circleRadius:0.25 }
interface GridConfig { cellWidth; cellHeight; samplesPerCircle; circleRadius }
```

Character matching (`src/lib/lookup.ts`, `characters.ts`):

```ts
function findBestCharacter(samplingVector, characters?): string          // squared-Euclidean nearest
class CachedCharacterLookup { findBest(vector): string; clearCache(): void }
const cachedLookup: CachedCharacterLookup                                // shared instance
const CHARACTERS: CharacterData[]                                        // raw 6D vectors
const NORMALIZED_CHARACTERS: CharacterData[]                             // per-component normalized
function normalizeCharacterVectors(chars): CharacterData[]
interface CharacterData { char: string; vector: number[] }
```

Contrast (`src/lib/contrast.ts`):

```ts
function applyGlobalContrast(vector, exponent): number[]
function applyDirectionalContrast(internalVector, externalVector, exponent): number[]
function applyFullContrast(internalVector, externalVector|null, globalExp, directionalExp): number[]
```

Ripple (`src/lib/ripple.ts`):

```ts
createRipple, createRainDrop, calculateWaveValue, applyRippleToVector,
pruneExpiredRipples, hasActiveRipples, DEFAULT_RIPPLE_CONFIG, DEFAULT_RAIN_CONFIG
// types: Ripple, RippleConfig, RippleState, RainConfig
```

Note: `samplePixel` and `sampleCircle` exist in the source but are **not** exported —
use `sampleCell` / `sampleGrid`.

## Caveats

- **CORS:** external images need `Access-Control-Allow-Origin`; otherwise the canvas
  read fails and output is blank. Prefer same-origin assets.
- **Performance:** grids wider than ~150 columns can hurt animation — shrink `width`
  or disable ripple/rain.
- **Fonts:** monospace only.
