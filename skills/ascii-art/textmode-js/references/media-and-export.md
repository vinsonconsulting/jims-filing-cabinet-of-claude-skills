# Loading media, converting to ASCII & exporting

## Loading assets (async — call in `setup`)

```js
let img, vid, tex;
t.setup(async () => {
  img = await t.loadImage("./poster.png");   // TextmodeImage
  vid = await t.loadVideo("./loop.mp4");      // TextmodeVideo
  await vid.play();                           // video needs an explicit play
  tex = t.createTexture(someCanvasOrVideoEl); // TextmodeTexture (sync wrapper)
});
```

`loadImage`/`loadVideo` are Promise-based; `createTexture` synchronously wraps an
existing `HTMLCanvasElement` or `HTMLVideoElement` (it refreshes each frame —
the route for live/webcam input via a `<video>` element you control). Fonts load
similarly (`await t.loadFont(...)` or `await layer.loadFont(...)` for a
layer-local font).

## Media → textmode conversion

Images, videos, and textures share a converter API. Configure how source pixels
become glyphs and colors, then draw the source like any other content:

```js
img
  .characters(" .:-=+*#%@")        // brightness ramp, dark -> light
  .conversionMode("brightness")     // mapping strategy (default)
  .charColorMode("sampled")         // glyph color from the source
  .cellColorMode("fixed").cellColor(0, 0, 0); // fixed background

img.flipX(true).invert(true).charRotation(90); // non-destructive transforms
```

Shared source controls: `characters()`, `conversionMode()`, `charColorMode()` /
`cellColorMode()`, `invert()`, `flipX()`/`flipY()`, `charRotation()`, plus `width`
/`height` (grid cells, aspect preserved) and `dispose()`. Register a **custom**
conversion strategy with a shader:

```js
t.conversions.register({
  id: "edges",
  createShader: (ctx) => myShader,
  createUniforms: (ctx) => ({ u_image: ctx.source.texture }),
});
img.conversionMode("edges");
```

## Exporting

### Text / data (synchronous — reads one layer's grid)

```js
const txt = t.toString({ layer, emptyCharacter, preserveTrailingSpaces });
t.saveStrings({ filename: "art.txt", layer });

const json = t.toJSON({ target: "all", includeMetadata: true });
t.saveJSON({ filename: "art.json", target: "all", pretty: true });
```

### SVG (synchronous, vector)

```js
const svg = t.toSVG({ includeBackgroundRectangles: true, strokeWidth: 1 });
t.saveSVG({ filename: "art.svg" });
```

### Raster image (async — captures the final composited canvas)

```js
await t.saveCanvas({ filename: "art.png", format: "png", scale: 2 }); // png | jpg | webp
await t.copyCanvas({ format: "png" });                                 // to clipboard
```

### Animated GIF (async)

```js
await t.saveGIF({
  filename: "loop.gif",
  frameCount: 120,
  frameRate: 30,
  scale: 1,
  repeat: 0,                       // 0 = loop forever
  onProgress: (p) => console.log(p),
});
```

### Video MP4 / WebM (async)

```js
await t.saveVideo({
  filename: "clip.mp4",
  format: "mp4",                   // "mp4" | "webm" (webm supports transparency)
  frameCount: 300,
  frameRate: 60,
  bitrate: "medium",
  onProgress: (p) => console.log(p),
});
```

## Which exporter to choose

- **TXT / JSON / SVG** read a single **layer's** grid data — exact glyphs/colors,
  resolution-independent, no compositing/filters.
- **PNG / JPG / WebP / GIF / MP4 / WebM** capture the **final presented canvas** —
  includes every layer, blend mode, shader, and filter.

GIF/MP4/WebM render `frameCount` frames; with a deterministic seed and
`frameCount % period == 0`, the export loops cleanly. For frame-accurate capture,
`noLoop()` + `redraw(1)` per exported frame.
