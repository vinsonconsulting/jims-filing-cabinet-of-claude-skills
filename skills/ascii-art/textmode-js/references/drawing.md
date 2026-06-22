# Grid, primitives, cells & transforms

## The grid

```js
t.grid.cols        // columns (cells across)
t.grid.rows        // rows (cells down)
t.grid.cellWidth   // pixel width of one cell
t.grid.cellHeight  // pixel height of one cell
```

The grid is **responsive by default** — it recomputes when the canvas size, font
size, or active font changes. To pin a fixed grid:

```js
t.grid.cols = 80;
t.grid.rows = 45;
t.grid.reset();        // recompute after manual changes
// t.grid.responsive(); // return to auto-sizing
```

## Coordinates — center origin, units in cells

`(0, 0)` is the **center** of the grid. `-x` left, `+x` right, `-y` up, `+y`
down. **All drawing coordinates and sizes are in cells**, not pixels.

To address a cell by its `(col, row)` index, translate from the center:

```js
t.translate(col - t.grid.cols / 2, row - t.grid.rows / 2);
```

## Per-cell state (sticky)

Set the glyph and its two colors; following draw calls use them until changed:

```js
t.char("@");               // glyph (a string; respects grapheme clusters)
t.charColor(255, 180, 90); // glyph/foreground color
t.cellColor(0, 0, 0);      // cell/background color
```

Color setters accept several forms: a single gray `0–255`, `(r,g,b)`, `(r,g,b,a)`,
a CSS string (`"#ff00aa"`, `"red"`), or a `TextmodeColor`. `t.colorMode("rgb"|
"hsl"|"hsb")` changes how numeric inputs are interpreted. p5-style `t.fill()`
(cell) and `t.stroke()` (glyph/line) aliases exist; pick one vocabulary and stay
consistent.

## Primitives

All take **cell** coordinates/sizes and honor the current transform + state.

| Call | Signature | Notes |
| --- | --- | --- |
| `t.background(...)` | `(gray)` or `(r,g,b)` | fill the whole active layer; call first each frame |
| `t.clear()` | `()` | clear the active layer |
| `t.point()` | `()` | stamp one cell at the transform origin |
| `t.rect(w, h)` | width, height | rectangle **centered** at the origin |
| `t.line(x1,y1,x2,y2)` | two points | straight line between cells |
| `t.ellipse(w, h)` | width, height | ellipse centered at the origin |
| `t.triangle(x1,y1,x2,y2,x3,y3)` | three points | filled triangle |
| `t.arc(w, h, start, end)` | size + angles | arc segment (angles in degrees) |
| `t.bezierCurve(x1,y1,cx1,cy1,cx2,cy2,x2,y2)` | curve | cubic Bézier |
| `t.lineWeight(n)` | thickness | set before `line`/`bezierCurve` |

Because `rect`/`ellipse`/`point` draw at the origin, position them with
`translate` (inside `push`/`pop`) rather than passing an x/y.

```js
t.push();
  t.translate(5, -3);
  t.char("#"); t.charColor(0, 255, 200);
  t.rect(8, 4);          // 8×4 cells, centered at (5,-3)
t.pop();
```

## Transforms

| Call | Units | Effect |
| --- | --- | --- |
| `t.translate(x, y[, z])` | cells | move the origin (`translateX/Y/Z` also exist) |
| `t.rotateZ(deg)` | **degrees** | rotate in-plane (2D) |
| `t.rotateX/rotateY(deg)` | degrees | 3D rotations |
| `t.rotate(x, y, z)` | degrees | combined 3-axis rotation |
| `t.scale(x[, y])` | multiplier | scale subsequent drawing |
| `t.applyMatrix(...)` / `t.resetMatrix()` | — | low-level matrix control |
| `t.push()` / `t.pop()` | — | save / restore transform **and all state** |

`push()` saves the matrix plus colors, line weight, shader, camera, and lighting;
`pop()` restores them. **Order matters** — translate-then-rotate differs from
rotate-then-translate.

```js
for (let i = 0; i < 12; i++) {
  t.push();
    t.rotateZ(i * 30);
    t.translate(0, -10);
    t.char("*"); t.point();
  t.pop();
}
```
