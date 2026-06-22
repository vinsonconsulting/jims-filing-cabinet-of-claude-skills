# Setup, creation & lifecycle

## Install / entry points

**npm + ESM** (bundler or importmap):

```bash
npm install textmode.js
```

```js
import { textmode } from "textmode.js";
```

**UMD / CDN** — no build step; the library attaches a global `textmode`:

```html
<script src="https://cdn.jsdelivr.net/npm/textmode.js@latest/dist/textmode.umd.js"></script>
<script>
  const t = textmode.create({ width: 800, height: 600, fontSize: 16, frameRate: 60 });
</script>
```

There is also a hosted web editor (editor.textmode.art) for zero-setup
experiments. Node 20.8.1+ is needed only for tooling/bundling, not to run a
sketch in the browser.

## `textmode.create(options)`

Returns a `Textmodifier` instance **synchronously** and (unless you supply a
canvas) creates a `<canvas>` and inserts it into the page. Common options:

| Option | Meaning |
| --- | --- |
| `width` | canvas width in **pixels** |
| `height` | canvas height in **pixels** |
| `fontSize` | glyph size in pixels (drives the cell size, hence cols/rows) |
| `frameRate` | target FPS for the draw loop |

```js
const t = textmode.create({
  width: window.innerWidth,
  height: window.innerHeight,
  fontSize: 16,
  frameRate: 60,
});
```

`width`/`height` are pixels; the **grid** (cols × rows) is derived from those and
`fontSize`. Read the grid in `setup`/`draw`, never before `setup` runs.

By default `create()` builds its own `<canvas>` and inserts it into the page. To
mount the sketch in a specific container instead, set the corresponding option on
`create()` — consult the live API reference for the exact option name rather than
guessing one.

## WebGL2

textmode.js renders with **WebGL2**. On a browser without it, creation/rendering
fails — guard production embeds and surface a fallback message. Check
`document.createElement("canvas").getContext("webgl2")` if you need to detect it.

## Lifecycle

Register callbacks on the instance:

```js
t.setup(() => { /* once, after renderer + grid exist; load assets here */ });
t.draw(() => { /* every frame */ });
t.windowResized(() => t.resizeCanvas(window.innerWidth, window.innerHeight));
```

- **`setup(cb)`** runs once after init — the place for `await t.loadImage(...)`,
  `await t.loadFont(...)`, `await t.createMaterialShader(...)`, and one-time state.
- **`draw(cb)`** runs each frame (or on demand when looping is paused).
- **`windowResized(cb)`** fires on viewport changes; call `t.resizeCanvas(w, h)`
  inside it to recompute the grid.

## Loop & timing control

| Call | Effect |
| --- | --- |
| `t.noLoop()` | pause the automatic draw loop |
| `t.loop()` | resume it |
| `t.redraw(n?)` | render one (or `n`) frames on demand — pair with `noLoop()` |
| `t.isLooping()` | whether the loop is active |
| `t.frameCount` | frames elapsed (property) |
| `t.frameRate(fps?)` | set target FPS with an arg; read measured FPS with none |

```js
t.noLoop();
exporter.on("tick", () => t.redraw(1)); // drive frames from an external clock
```

## Teardown

`t.destroy()` disposes the renderer, listeners, and internal layers — call it when
unmounting a sketch (e.g. a component teardown) to free GPU resources.

## Gotchas

- `create()` is synchronous, but **asset loaders are async** — `await` them in
  `setup`, not at module top level before the instance is ready.
- Don't read `t.grid.cols/rows` before `setup` runs; the grid isn't sized yet.
- One `Textmodifier` owns one canvas. For multiple sketches, create multiple
  instances and pass/attach distinct canvases.
