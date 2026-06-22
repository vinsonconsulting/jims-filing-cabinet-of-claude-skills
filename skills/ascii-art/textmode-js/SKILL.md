---
name: textmode-js
description: Use when building real-time ASCII or textmode graphics in the browser
  with the textmode.js library — generative glyph-grid sketches, retro/terminal
  visuals, audio-reactive or VJ textmode, or turning images and video into ASCII on
  a WebGL2 character grid. Trigger whenever textmode.js is named, when a sketch calls
  textmode.create, t.setup/t.draw, t.grid, t.char/charColor/cellColor, glyph ramps,
  or character-cell rendering, or when the user wants to build, debug, or export a
  grid-of-characters visual. Covers UMD/ESM setup, the setup/draw/resize lifecycle,
  drawing primitives, char and color cells, print and glyph ramps, animation and
  noise, layers, filters, custom GLSL ES 3.00 shaders, media conversion, and export
  to TXT/SVG/PNG/GIF/MP4/WebM. Not for generic ASCII art or Python image-to-ASCII —
  this is specifically the textmode.js JavaScript/TypeScript library.
---

# textmode-js

`textmode.js` is a zero-dependency TypeScript creative-coding library for real-time
ASCII / textmode graphics. It renders to a **grid of character cells** on a WebGL2
canvas with p5.js-like ergonomics. Use it to author, debug, and export
glyph-grid sketches.

## Mental model

- The canvas is a grid of **cells**, not pixels. Each cell holds one **glyph**, a
  **char color** (the glyph's foreground), and a **cell color** (its background).
- You draw with p5-style primitives, but coordinates and sizes are in **cells**.
- **The origin `(0,0)` is the grid CENTER.** +x is right, +y is **down**, -y is up.
  This is the single biggest trip-up — a `rect`/`point` with no transform lands at
  the center, not the top-left.
- A sketch is a lifecycle: `create()` once → `setup()` once → `draw()` every frame.
  State setters (`char`, `charColor`, `cellColor`, transforms) are **sticky** —
  they apply to every draw call until changed or until `pop()` restores them.

## Minimal sketch (ESM)

```js
import { textmode } from "textmode.js";

const t = textmode.create({
  width: window.innerWidth,
  height: window.innerHeight,
  fontSize: 16,
  frameRate: 60,
});

t.setup(() => {
  // Runs once after the renderer + grid exist.
  // Load fonts / images / shaders here (these are async — await them).
});

t.draw(() => {
  t.background(18, 20, 28);        // clear the grid every frame
  t.char("@");                     // glyph used by following draw calls
  t.charColor(120, 220, 160);      // glyph (foreground) color
  t.cellColor(0, 0, 0);            // cell (background) color
  // (0,0) is the grid CENTER; rect(w,h) is centered there, sized in CELLS.
  t.rect(t.grid.cols / 2, t.grid.rows / 2);
});

t.windowResized(() => t.resizeCanvas(window.innerWidth, window.innerHeight));
```

**UMD** is identical minus the import — load the script, then use the global
`textmode`:

```html
<script src="https://cdn.jsdelivr.net/npm/textmode.js@latest/dist/textmode.umd.js"></script>
<script>
  const t = textmode.create({ width: 800, height: 600, fontSize: 16, frameRate: 60 });
  t.draw(() => { t.background(0); t.char("#"); t.charColor(0, 255, 0); t.rect(10, 6); });
</script>
```

## Generative idiom (per-cell noise + glyph ramp)

A glyph ramp maps a value in `[0,1]` to a character (dark → light). Stamp one cell
at a time by translating to it and drawing a `point()`:

```js
let ramp;
t.setup(() => { ramp = t.createGlyphRamp(" .:-=+*#%@"); });

t.draw(() => {
  t.background(0);
  const t0 = t.frameCount * 0.01;
  for (let y = 0; y < t.grid.rows; y++) {
    for (let x = 0; x < t.grid.cols; x++) {
      const n = t.noise(x * 0.08, y * 0.12, t0);   // 0..1
      t.push();
      t.translate(x - t.grid.cols / 2, y - t.grid.rows / 2); // cell -> centered coords
      t.char(ramp.at(n));
      t.charColor(60 + n * 180, 120, 220 - n * 140);
      t.point();
      t.pop();
    }
  }
});
```

## Authoring workflow

1. **Pick a target and entry point.** Browser ESM (bundler/importmap) or a single
   UMD HTML file. See `references/setup.md`.
2. **Stand up the lifecycle** — `create` → `setup` (load assets) → `draw`. Wire
   `windowResized` to `resizeCanvas`. Confirm a blank `background()` renders before
   adding logic.
3. **Draw.** Set `char` + `charColor` + `cellColor`, then primitives or `print`.
   Remember: cells, center origin, sticky state, `push`/`pop` to isolate.
   See `references/drawing.md` and `references/text-and-ramps.md`.
4. **Animate / generate.** Use `frameCount`, `noise`, seeded `random`, `map`/`lerp`.
   See `references/animation-and-generative.md`.
5. **Composite** only when one pass isn't enough — layers, filters, custom shaders.
   See `references/compositing.md`.
6. **Export** to text, vector, image, or video — `t.saveStrings`/`t.saveSVG`/
   `t.saveCanvas`/`t.saveGIF`/`t.saveVideo`. See `references/media-and-export.md`.

## Which reference to open

| You're working on… | Open |
| --- | --- |
| Install, `create()` options, canvas/WebGL2, lifecycle, loop control | `references/setup.md` |
| Grid & coordinates, primitives, `char`/`charColor`/`cellColor`, transforms | `references/drawing.md` |
| `print`, alignment, inline markup, `TextmodeGlyphRamp` value→glyph | `references/text-and-ramps.md` |
| Timing, seeded random & streams, noise, vectors, easing, math helpers | `references/animation-and-generative.md` |
| Layers & blend modes, framebuffers, filters, GLSL shaders, 3D camera | `references/compositing.md` |
| Loading images/video, media→ASCII conversion, exporting TXT/SVG/PNG/GIF/MP4 | `references/media-and-export.md` |

## Debugging checklist

- **Nothing renders / black canvas.** Confirm WebGL2 (a very old browser fails).
  Confirm `draw()` actually runs and `background()` is called each frame. Check
  the console for a renderer-init error.
- **Drawing is off-screen or "in the corner."** You assumed top-left origin. The
  center is `(0,0)`; offset cell loops by `-cols/2, -rows/2` (see the idiom above).
- **Everything is one color / wrong glyph.** State is sticky and global to the
  active layer — a `charColor` set once persists. Wrap isolated changes in
  `push()`/`pop()`.
- **Assets are blank.** `loadImage`/`loadVideo`/`loadFont`/`createMaterialShader`
  are async — `await` them in `setup()`, and call `video.play()` for video.
- **Resize looks wrong.** Only `resizeCanvas()` in `windowResized` updates the
  grid; read `t.grid.cols/rows` after resize to get the new dimensions.

## Conventions

- Keep media and font files local to the project; reference paths, not data URLs.
- No secrets in a sketch. If a sketch hits an API for live data, name where the key
  lives (env/secret store) and read it at runtime — never inline it.
