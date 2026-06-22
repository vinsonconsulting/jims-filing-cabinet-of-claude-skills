# Text, alignment, markup & glyph ramps

## Printing text

```js
t.print(text, x, y, options?);
```

Writes `text` into the active layer starting at cell `(x, y)`, honoring the
current `charColor`/`cellColor`/transform. Options:

| Option | Meaning |
| --- | --- |
| `leading` | line spacing in cells (for multi-line strings) |
| `letterSpacing` | extra cells between characters |
| `tabSize` | spaces per tab |
| `markup` | enable inline formatting tags (default `true`) |

## Alignment

`t.printAlign(horizontal, vertical?)` sets how the `print` coordinate anchors the
text for subsequent calls:

- horizontal: `"left"` · `"center"` · `"right"`
- vertical: `"top"` · `"middle"` · `"bottom"`

```js
t.printAlign("center", "middle");
t.charColor("#00ff88");
t.print("HELLO", 0, 0);   // centered on the grid center
```

## Inline markup

When `markup` is on, `print` understands BBCode-style tags that style spans of
text without breaking the string into separate calls:

| Tag | Effect |
| --- | --- |
| `[fg=#rrggbb]…[/fg]` | glyph (foreground) color |
| `[bg=#rrggbb]…[/bg]` | cell (background) color |
| `[inv]…[/inv]` | invert colors |
| `[rot=deg]…[/rot]` | rotate glyphs |
| `[fx]…[/fx]` / `[fy]…[/fy]` | flip glyphs horizontally / vertically |

```js
t.print("[fg=#ff5555]ERR[/fg] [bg=#003300]ok[/bg]", 0, 0);
```

Colors accept hex or CSS names. Tags nest. Set `markup: false` to print literal
brackets.

## Glyph ramps (`TextmodeGlyphRamp`)

A ramp maps a value to a character along a low→high intensity sequence — the core
trick for converting brightness/noise/distance into ASCII.

```js
const ramp = t.createGlyphRamp(" .:-=+*#%@"); // dark -> light
// or: new TextmodeGlyphRamp(" .:-=+*#%@")
```

Map a value to a glyph:

```js
ramp.at(0.0);          // first char (" ")
ramp.at(1.0);          // last char ("@")
ramp.at(value);        // value clamped to [0,1]
ramp.at(value, lo, hi); // normalize from a custom range first
```

```js
const n = t.noise(x * 0.07, y * 0.1, t.frameCount * 0.01); // 0..1
t.char(ramp.at(n));
```

Ramps are **immutable**. `ramp.shift(k)` returns a rotated copy (cycle the
character assignment, e.g. for animation). `ramp.characters` and `ramp.length`
expose the sequence. Build the string from **darkest to brightest** so values map
intuitively; reverse it for light-on-dark output.
