# Animation, timing & generative helpers

## Timing

| API | Kind | Meaning |
| --- | --- | --- |
| `t.frameCount` | property | frames since start; drive cyclic motion (`frameCount % N`) |
| `t.frameRate(fps?)` | method | set target FPS with an arg; read measured FPS with none |
| `t.millis()` | method | elapsed time in milliseconds |
| `t.secs()` | method | elapsed time in seconds |
| `t.deltaTime` | property/method | ms since the previous frame — use for frame-rate-independent motion |

Prefer `t.frameCount` for simple deterministic cycles; use `deltaTime`/`secs` when
motion must be time-based regardless of FPS.

```js
const angle = (t.frameCount * 2) % 360;
```

## Loop control

`t.loop()` / `t.noLoop()` / `t.redraw(n?)` / `t.isLooping()` — see
`references/setup.md`. Pair `noLoop()` + `redraw(1)` to render on an external
clock (e.g. a frame-accurate exporter).

## Seeded randomness

`t.random()` is overloaded:

```js
t.random();          // [0, 1)
t.random(max);       // [0, max)
t.random(min, max);  // [min, max)
t.random(array);     // a random element
t.randomGaussian(mean = 0, sd = 1); // normal distribution
```

`t.randomSeed(seed)` makes the sequence deterministic (same seed → same numbers) —
essential for reproducible generative art. For **independent** deterministic
streams that don't perturb each other, use named streams or your own instances:

```js
t.randomSeed("poster-v3");
const clouds = t.randomStream("clouds");   // independent stream
const terrain = new TextmodeRandom("terrain");
clouds.random(); terrain.random();         // each reproducible on its own seed
```

## Noise

Multi-octave Perlin-style noise, deterministic for a given seed:

```js
const n = t.noise(x);          // 1D
const n2 = t.noise(x, y);      // 2D
const n3 = t.noise(x, y, z);   // 3D (use z = time for evolving fields)
t.noiseSeed("landscape");
t.noiseDetail(octaves, falloff); // more octaves = more fine detail
```

Treat the output as roughly `[0,1]` for ramp mapping; if you need exact bounds,
normalize empirically or check the live API. Scale inputs down (e.g. `x * 0.08`)
for smooth fields — raw cell indices change too fast.

## Vectors (`TextmodeVector`)

```js
const v = t.createVector(3, 4);     // or new TextmodeVector(3, 4)
v.normalize().mult(10);             // mutating + chainable
v.mag();                            // 5 before, 10 after
```

Mutating + chainable: `add`, `sub`, `mult`, `div`, `normalize`, `limit`,
`setMag`, `set`. Read-only: `mag`, `magSq`, `dot`, `cross`, `heading` (degrees),
`dist`, `copy`. Components are public `x`, `y`, `z`.

## Math & easing

```js
t.map(v, a1, b1, a2, b2); // re-map between ranges
t.lerp(a, b, k);          // linear interpolate (k in 0..1)
t.constrain(v, lo, hi);   // clamp
t.dist(x1, y1, x2, y2);   // euclidean distance
t.radians(deg); t.degrees(rad);
t.ease(name, k);          // eased 0..1, e.g. "inOutCubic", "outQuad"
```

`t.ease(name, k)` applies a named easing curve to a normalized `k`
(`"linear"`, `"inQuad"`/`"outQuad"`/`"inOutQuad"`, cubic and sine variants, …).

```js
const k = t.ease("inOutCubic", (t.frameCount % 120) / 120);
const px = t.lerp(-20, 20, k);
```
