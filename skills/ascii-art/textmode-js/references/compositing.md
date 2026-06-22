# Layers, framebuffers, filters & shaders

Reach for this layer only when a single draw pass isn't enough — stacked passes,
post-processing, or custom GPU work.

## Layers

Every sketch has a base layer (`t.layers.base`); add more for independent passes
that composite together:

```js
const glow = t.layers.add({ opacity: 0.75, blendMode: "screen", fontSize: 8 });

glow.draw(() => {
  t.clear();
  t.char("*"); t.charColor(120, 220, 255);
  t.rect(24, 10);
});
```

Layer options: `visible`, `opacity` (0–1), `blendMode`, `offsetX`/`offsetY`,
`rotationZ`, `fontSize`, `fontSource`. Manipulate at runtime with
`glow.opacity(n)`, `glow.offset(x, y)`, `glow.rotateZ(deg)`, `glow.hide()`,
`glow.show()`. Manage the stack with `t.layers.move(layer, index)`,
`t.layers.swap(a, b)`, `t.layers.remove(layer)`, `t.layers.clear()`.

**Blend modes:** `normal`, `additive`, `multiply`, `screen`, `overlay`,
`difference` (enumerated in `TEXTMODE_LAYER_BLEND_MODES`).

## Framebuffers (`TextmodeFramebuffer`)

Render to an off-screen target and reuse it as a texture (feedback, ping-pong
effects):

```js
fb.begin();   // render into the framebuffer
// ... draw ...
fb.end();
fb.resize(w, h);
fb.readPixels();
fb.dispose();
```

Accessors: `width`, `height`, `textures`, `attachmentCount`, `framebuffer`.

## Filters

Post-processing passes over the rendered ASCII. Built-ins include `invert`,
`grayscale`, `sepia`, `threshold`; the companion `textmode.filters.js` package
adds bloom, glitch, scanlines, vignette, film grain, pixelation, chromatic
aberration, and more.

```js
t.draw(() => {
  t.background(0); t.char("@"); t.rect(20, 12);
  t.filter("threshold", { threshold: 0.5 }); // global filter
});
```

Apply per-layer (`layer.filter(...)`, before compositing) or after everything in
`t.finalDraw(() => t.filter("invert"))`. Register a **custom** GLSL filter:

```js
await t.filters.register("vignette", "./vignette.frag", {
  u_intensity: ["intensity", 0.5], // uniform -> [paramName, default]
});
t.draw(() => t.filter("vignette", { intensity: 0.8 }));
```

Manage with `t.filters.has(name)` / `t.filters.unregister(name)`.

## Custom shaders (GLSL ES 3.00)

textmode.js runs on WebGL2, so custom shaders are **GLSL ES 3.00**. A material
shader writes the cell grid via three MRT outputs:

| Output | Encodes |
| --- | --- |
| `o_character` | glyph index (R/G pack 0–65535), transform flags (B), rotation (A) |
| `o_primaryColor` | glyph (foreground) color, RGBA |
| `o_secondaryColor` | cell (background) color, RGBA |

```js
let mat;
t.setup(async () => { mat = await t.createMaterialShader("./material.frag"); });

t.draw(() => {
  t.shader(mat);
  t.setUniform("u_time", t.secs());
  t.setUniforms({ u_center: [0.5, 0.5] });
  // ... draw ...
  t.resetShader(); // back to the default pipeline
});
```

Pack a glyph index inside the fragment shader like:

```glsl
int glyph = 65;                               // 'A'
float low  = float(glyph % 256) / 255.0;      // R
float high = float(glyph / 256) / 255.0;      // G
o_character = vec4(low, high, 0.0, 0.0);
```

Common inputs: `v_uv` (cell UV) and any uniforms you set. Keep heavy generation in
the shader and let textmode.js handle glyph rasterization.

## 3D camera

A `TextmodeCamera` supports `setPosition(x,y,z)`, `lookAt(x,y,z)`, `move(x,y,z)`,
`setUp(x,y,z)`, with `eye*`/`target*`/`up*` accessors — pair it with the 3D
rotation transforms (`rotateX/Y`, `translateZ`). For mesh/lighting specifics
beyond the camera, consult the live API reference.
