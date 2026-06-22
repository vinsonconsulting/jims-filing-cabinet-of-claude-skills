#!/usr/bin/env python3
"""Convert an image file to shape-aware ASCII art.

This is a port of the shape-vector ASCII technique
(Alex Harri, https://alexharri.com/blog/ascii-rendering) and the circle geometry of
the `ascii-img-react` package (https://github.com/mrmartineau/ascii-img-react, MIT).

Unlike a naive brightness ramp -- which picks one glyph per cell off a " .:-=+*#%@"
scale and produces jagged edges -- this matches each image cell to the glyph whose
*shape* fits best. Each glyph and each image cell is reduced to a 6D vector by
sampling six staggered circles arranged in a 2x3 grid; the closest glyph (squared
Euclidean distance) wins. Glyph vectors are computed by genuinely rasterizing the
bundled monospace font, so the match reflects the real ink the user will see -- and
PNG/SVG output draws with the same font, so it is self-consistent.

Dependencies: Pillow only. Pure-Python vector math (no numpy). Python 3.9+.
Install Pillow with:  python3 -m pip install Pillow
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from typing import Dict, List, Optional, Tuple

try:
    from PIL import Image, ImageColor, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - guidance only
    sys.stderr.write(
        "error: Pillow is required. Install it with:  python3 -m pip install Pillow\n"
    )
    raise SystemExit(1)

# --- Geometry, ported verbatim from ascii-img-react/src/lib/sampling.ts -------------
# Fractions of the cell's width/height. Left column sits lower, right column higher;
# this stagger is what lets the 6D vector tell 'p' from 'q' and '^' from '_'.
CIRCLE_POSITIONS: List[Tuple[float, float]] = [
    (0.25, 0.17),  # 0 top-left
    (0.75, 0.25),  # 1 top-right
    (0.25, 0.50),  # 2 middle-left
    (0.75, 0.50),  # 3 middle-right
    (0.25, 0.75),  # 4 bottom-left
    (0.75, 0.83),  # 5 bottom-right
]

# Ten circles that reach into neighbouring cells, used only for directional contrast.
EXTERNAL_CIRCLE_POSITIONS: List[Tuple[float, float]] = [
    (0.25, -0.17),  # 0 above top-left
    (0.75, -0.08),  # 1 above top-right
    (-0.08, 0.33),  # 2 left of middle-left
    (1.08, 0.33),   # 3 right of middle-right
    (-0.08, 0.67),  # 4 left of bottom-left
    (1.08, 0.67),   # 5 right of bottom-right
    (0.25, 0.92),   # 6 below bottom-left
    (0.75, 1.08),   # 7 below bottom-right
    (0.50, -0.12),  # 8 above center
    (0.50, 1.00),   # 9 below center
]

# Which external circles widen each internal component (ascii-img-react ordering).
AFFECTING_EXTERNAL_INDICES: List[List[int]] = [
    [0, 1, 2, 8],
    [0, 1, 3, 8],
    [2, 4, 0, 6],
    [3, 5, 1, 7],
    [4, 6, 9, 2],
    [5, 7, 9, 3],
]

CIRCLE_RADIUS_FRAC = 0.25  # radius as a fraction of the cell, per the package

# Sampling resolution for the *image* grid (px per cell). 6x12 matches the package's
# DEFAULT_GRID_CONFIG; only affects sampling fidelity, never the output dimensions.
IMG_CELL_W = 6
# Samples per circle. 9 -> a 3x3 grid clipped to the unit circle -> 5 live points,
# exactly what ascii-img-react does.
DEFAULT_SAMPLES = 9

# Glyph rasterization: render each glyph this tall, then sample at high density so the
# overlap fractions are smooth. Resolution-independent of the image grid.
GLYPH_FONT_SIZE = 64
GLYPH_SAMPLES = 64

BUNDLED_FONT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "assets", "DejaVuSansMono.ttf"
)

CACHE_VERSION = 2  # bump when geometry / vector math changes, to invalidate caches


# --- Sampling primitives ------------------------------------------------------------
def circle_offsets(num_samples: int) -> List[Tuple[float, float]]:
    """Offsets in [-1, 1] on a square grid, clipped to the unit circle.

    Mirrors ascii-img-react's sampleCircle: gridSize = ceil(sqrt(n)), keep points with
    ox^2 + oy^2 <= 1. With n=9 this yields the 5-point plus pattern.
    """
    if num_samples <= 1:
        return [(0.0, 0.0)]
    grid = int(math.ceil(math.sqrt(num_samples)))
    pts: List[Tuple[float, float]] = []
    for gy in range(grid):
        for gx in range(grid):
            ox = (gx / (grid - 1)) * 2 - 1
            oy = (gy / (grid - 1)) * 2 - 1
            if ox * ox + oy * oy <= 1.0:
                pts.append((ox, oy))
    return pts or [(0.0, 0.0)]


def sample_field(
    field: List[List[float]],
    width: int,
    height: int,
    cx: float,
    cy: float,
    radius: float,
    offsets: List[Tuple[float, float]],
) -> float:
    """Average a [0,1] field over a circle. Out-of-bounds reads as 0 (like the package)."""
    total = 0.0
    for ox, oy in offsets:
        px = int(cx + ox * radius)
        py = int(cy + oy * radius)
        if 0 <= px < width and 0 <= py < height:
            total += field[py][px]
        # else += 0.0
    return total / len(offsets)


# --- Glyph shape vectors (rasterized from the font) ---------------------------------
def _load_font(font_path: str, size: int) -> "ImageFont.FreeTypeFont":
    return ImageFont.truetype(font_path, size)


def font_cell_aspect(font_path: str) -> float:
    """The font's natural cell aspect = line height / advance width.

    Using this for the image grid keeps the picture undistorted, since the glyph
    vectors are sampled in this same cell shape.
    """
    font = _load_font(font_path, GLYPH_FONT_SIZE)
    ascent, descent = font.getmetrics()
    advance = font.getlength("M")
    if advance <= 0:
        return 2.0
    return (ascent + descent) / advance


def compute_char_vectors(
    font_path: str, charset: str
) -> List[Tuple[str, List[float]]]:
    """Return [(char, normalized 6D vector)] by rasterizing each glyph.

    Each component is the fraction of in-circle sample points that land on ink, then
    normalized by the per-component max across all glyphs so the vectors span [0,1]
    (the blog's normalization -- raw overlaps cluster low otherwise).
    """
    font = _load_font(font_path, GLYPH_FONT_SIZE)
    ascent, descent = font.getmetrics()
    advance = font.getlength("M")
    cw = max(1, int(round(advance)))
    ch = max(1, int(ascent + descent))
    radius = CIRCLE_RADIUS_FRAC * (cw + ch) / 2.0
    offsets = circle_offsets(GLYPH_SAMPLES)

    raw: List[Tuple[str, List[float]]] = []
    for ch_char in charset:
        # Rasterize the glyph white-on-black in its monospace cell.
        img = Image.new("L", (cw, ch), 0)
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), ch_char, fill=255, font=font)
        px = img.load()
        ink = [[1.0 if px[x, y] > 127 else 0.0 for x in range(cw)] for y in range(ch)]
        vec: List[float] = []
        for fx, fy in CIRCLE_POSITIONS:
            v = sample_field(ink, cw, ch, fx * cw, fy * ch, radius, offsets)
            vec.append(v)
        raw.append((ch_char, vec))

    # Per-component max normalization.
    comp_max = [0.0] * 6
    for _, vec in raw:
        for i, val in enumerate(vec):
            if val > comp_max[i]:
                comp_max[i] = val
    norm: List[Tuple[str, List[float]]] = []
    for ch_char, vec in raw:
        norm.append(
            (ch_char, [vec[i] / comp_max[i] if comp_max[i] > 0 else 0.0 for i in range(6)])
        )
    return norm


def char_vectors_cached(font_path: str, charset: str) -> List[Tuple[str, List[float]]]:
    """Memoize char vectors on disk (temp dir); they depend only on font + geometry."""
    try:
        mtime = os.path.getmtime(font_path)
    except OSError:
        mtime = 0
    key_src = "{}|{}|{}|{}|{}|{}".format(
        os.path.abspath(font_path), mtime, charset, GLYPH_FONT_SIZE, GLYPH_SAMPLES, CACHE_VERSION
    )
    key = hashlib.sha1(key_src.encode("utf-8")).hexdigest()[:16]
    cache_path = os.path.join(tempfile.gettempdir(), "image_to_ascii_cache_{}.json".format(key))
    try:
        with open(cache_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return [(item[0], item[1]) for item in data]
    except (OSError, ValueError, IndexError):
        pass
    vectors = compute_char_vectors(font_path, charset)
    try:
        with open(cache_path, "w", encoding="utf-8") as fh:
            json.dump([[c, v] for c, v in vectors], fh)
    except OSError:
        pass
    return vectors


# --- Contrast enhancement (ported from ascii-img-react/src/lib/contrast.ts) ---------
def apply_global_contrast(vector: List[float], exponent: float) -> List[float]:
    if exponent <= 1:
        return list(vector)
    max_value = max(vector)
    if max_value <= 0:
        return list(vector)
    return [((v / max_value) ** exponent) * max_value for v in vector]


def apply_directional_contrast(
    internal: List[float], external: List[float], exponent: float
) -> List[float]:
    if exponent <= 1:
        return list(internal)
    out: List[float] = []
    for i, value in enumerate(internal):
        max_value = value
        for ext_idx in AFFECTING_EXTERNAL_INDICES[i]:
            if external[ext_idx] > max_value:
                max_value = external[ext_idx]
        if max_value <= 0:
            out.append(value)
        else:
            out.append(((value / max_value) ** exponent) * max_value)
    return out


def apply_full_contrast(
    internal: List[float],
    external: Optional[List[float]],
    global_exp: float,
    directional_exp: float,
) -> List[float]:
    result = list(internal)
    if external is not None and directional_exp > 1:
        result = apply_directional_contrast(result, external, directional_exp)
    if global_exp > 1:
        result = apply_global_contrast(result, global_exp)
    return result


# --- Lookup -------------------------------------------------------------------------
def best_char(
    vector: List[float], char_vectors: List[Tuple[str, List[float]]]
) -> str:
    best = " "
    best_dist = float("inf")
    for ch_char, cvec in char_vectors:
        dist = 0.0
        for i in range(6):
            d = vector[i] - cvec[i]
            dist += d * d
        if dist < best_dist:
            best_dist = dist
            best = ch_char
    return best


# --- The conversion -----------------------------------------------------------------
class Converted:
    def __init__(self, rows: List[str], colors: Optional[List[List[Tuple[int, int, int]]]]):
        self.rows = rows
        self.colors = colors  # per-cell RGB when --color, else None

    @property
    def cols(self) -> int:
        return len(self.rows[0]) if self.rows else 0


def convert_image(
    image_path: str,
    cols: int,
    cell_aspect: float,
    contrast: float,
    directional: bool,
    directional_exp: float,
    samples: int,
    charset: str,
    invert: bool,
    font_path: str,
    want_color: bool,
) -> Converted:
    char_vectors = char_vectors_cached(font_path, charset)

    src = Image.open(image_path).convert("RGB")
    iw, ih = src.size
    rows = max(1, int(round(cols * (ih / iw) / cell_aspect)))

    cell_w = IMG_CELL_W
    cell_h = max(1, int(round(IMG_CELL_W * cell_aspect)))
    grid_w = cols * cell_w
    grid_h = rows * cell_h
    small = src.resize((grid_w, grid_h), Image.LANCZOS)
    spx = small.load()

    # Precompute a density field (1 - lightness by default; lightness with --invert).
    field: List[List[float]] = [[0.0] * grid_w for _ in range(grid_h)]
    for y in range(grid_h):
        rowf = field[y]
        for x in range(grid_w):
            r, g, b = spx[x, y]
            lightness = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
            rowf[x] = lightness if invert else (1.0 - lightness)

    color_grid: Optional[List[List[Tuple[int, int, int]]]] = None
    if want_color:
        cg = src.resize((cols, rows), Image.LANCZOS).load()
        color_grid = [[tuple(cg[c, r]) for c in range(cols)] for r in range(rows)]

    radius = CIRCLE_RADIUS_FRAC * (cell_w + cell_h) / 2.0
    offsets = circle_offsets(samples)

    out_rows: List[str] = []
    for r in range(rows):
        base_y = r * cell_h
        line_chars: List[str] = []
        for c in range(cols):
            base_x = c * cell_w
            internal = [
                sample_field(field, grid_w, grid_h, base_x + fx * cell_w, base_y + fy * cell_h, radius, offsets)
                for fx, fy in CIRCLE_POSITIONS
            ]
            external = None
            if directional:
                external = [
                    sample_field(field, grid_w, grid_h, base_x + fx * cell_w, base_y + fy * cell_h, radius, offsets)
                    for fx, fy in EXTERNAL_CIRCLE_POSITIONS
                ]
            vec = apply_full_contrast(
                internal, external, contrast, directional_exp if directional else 1.0
            )
            line_chars.append(best_char(vec, char_vectors))
        out_rows.append("".join(line_chars))
    return Converted(out_rows, color_grid)


# --- Renderers ----------------------------------------------------------------------
def render_txt(conv: Converted) -> str:
    return "\n".join(conv.rows) + "\n"


def render_ansi(conv: Converted) -> str:
    if conv.colors is None:
        return render_txt(conv)
    out: List[str] = []
    for r, row in enumerate(conv.rows):
        parts: List[str] = []
        for c, ch_char in enumerate(row):
            cr, cg, cb = conv.colors[r][c]
            parts.append("\x1b[38;2;{};{};{}m{}".format(cr, cg, cb, ch_char))
        parts.append("\x1b[0m")
        out.append("".join(parts))
    return "\n".join(out) + "\n"


def render_png(conv: Converted, font_path: str, font_size: int, fg: str, bg: str, line_height: float) -> "Image.Image":
    font = _load_font(font_path, font_size)
    ascent, descent = font.getmetrics()
    advance = font.getlength("M")
    cw = advance
    lh = max(1, int(round((ascent + descent) * line_height)))
    width = max(1, int(math.ceil(cw * conv.cols)))
    height = max(1, lh * len(conv.rows))
    bg_rgb = ImageColor.getrgb(bg) if bg.lower() != "transparent" else (0, 0, 0)
    mode = "RGBA"
    if bg.lower() == "transparent":
        img = Image.new(mode, (width, height), (0, 0, 0, 0))
    else:
        img = Image.new(mode, (width, height), bg_rgb + (255,))
    draw = ImageDraw.Draw(img)
    fg_rgb = ImageColor.getrgb(fg)
    for r, row in enumerate(conv.rows):
        y = r * lh
        for c, ch_char in enumerate(row):
            if ch_char == " ":
                continue
            x = int(round(c * cw))
            color = conv.colors[r][c] if conv.colors is not None else fg_rgb
            draw.text((x, y), ch_char, fill=color + (255,), font=font)
    return img


def _xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(conv: Converted, font_path: str, font_size: int, fg: str, bg: str, line_height: float) -> str:
    font = _load_font(font_path, font_size)
    ascent, descent = font.getmetrics()
    advance = font.getlength("M")
    lh = (ascent + descent) * line_height
    width = advance * conv.cols
    height = lh * len(conv.rows)
    parts: List[str] = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="{:.0f}" height="{:.0f}" '
        'viewBox="0 0 {:.0f} {:.0f}">'.format(width, height, width, height)
    )
    if bg.lower() != "transparent":
        parts.append('<rect width="100%" height="100%" fill="{}"/>'.format(_xml_escape(bg)))
    parts.append(
        '<text font-family="DejaVu Sans Mono, monospace" font-size="{}" '
        'xml:space="preserve" fill="{}">'.format(font_size, _xml_escape(fg))
    )
    baseline0 = ascent * line_height
    for r, row in enumerate(conv.rows):
        y = baseline0 + r * lh
        if conv.colors is None:
            parts.append(
                '<tspan x="0" y="{:.1f}">{}</tspan>'.format(y, _xml_escape(row))
            )
        else:
            for c, ch_char in enumerate(row):
                if ch_char == " ":
                    continue
                cr, cg, cb = conv.colors[r][c]
                parts.append(
                    '<tspan x="{:.1f}" y="{:.1f}" fill="rgb({},{},{})">{}</tspan>'.format(
                        c * advance, y, cr, cg, cb, _xml_escape(ch_char)
                    )
                )
    parts.append("</text></svg>\n")
    return "".join(parts)


# --- CLI ----------------------------------------------------------------------------
def infer_format(out_path: Optional[str], explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    if out_path:
        ext = os.path.splitext(out_path)[1].lower().lstrip(".")
        if ext in ("png", "svg", "txt"):
            return ext
    return "txt"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Convert an image to shape-aware ASCII art (shape vectors, not a brightness ramp).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("image", help="input image file (any format Pillow can read)")
    p.add_argument("--cols", "--width", type=int, default=80, dest="cols",
                   help="output width in characters")
    p.add_argument("--cell-aspect", type=float, default=None,
                   help="character cell height/width ratio (default: derived from the font, ~1.94)")
    p.add_argument("--contrast", type=float, default=1.5,
                   help="global contrast exponent (1 = off); sharpens light/dark separation")
    p.add_argument("--directional", action="store_true",
                   help="enable directional contrast (samples neighbours; sharpens hard edges)")
    p.add_argument("--directional-exp", type=float, default=2.0,
                   help="directional contrast exponent (only with --directional)")
    p.add_argument("--samples", type=int, default=DEFAULT_SAMPLES,
                   help="samples per sampling circle for the image grid")
    p.add_argument("--charset", default=None,
                   help="characters to match against (default: printable ASCII 32-126)")
    p.add_argument("--invert", action="store_true",
                   help="map bright pixels to dense glyphs (for light-on-dark output, e.g. white-on-black)")
    p.add_argument("--out", default=None, help="write output to this file (else stdout)")
    p.add_argument("--format", choices=["txt", "png", "svg"], default=None,
                   help="output format (default: inferred from --out extension, else txt)")
    p.add_argument("--fg", default="#000000", help="foreground color for png/svg (name or #hex)")
    p.add_argument("--bg", default="transparent", help="background color for png/svg, or 'transparent'")
    p.add_argument("--font-size", type=int, default=14, help="font size for png/svg output")
    p.add_argument("--line-height", type=float, default=1.0, help="line-height multiplier for png/svg")
    p.add_argument("--font", default=None, help="override the bundled monospace font (.ttf)")
    color = p.add_mutually_exclusive_group()
    color.add_argument("--color", action="store_true", help="colorize output with each cell's average color")
    color.add_argument("--mono", action="store_true", help="monochrome output (default)")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    font_path = args.font or BUNDLED_FONT
    if not os.path.isfile(font_path):
        sys.stderr.write("error: font not found: {}\n".format(font_path))
        return 1
    if not os.path.isfile(args.image):
        sys.stderr.write("error: image not found: {}\n".format(args.image))
        return 1

    charset = args.charset if args.charset is not None else "".join(chr(i) for i in range(32, 127))
    cell_aspect = args.cell_aspect if args.cell_aspect is not None else font_cell_aspect(font_path)
    fmt = infer_format(args.out, args.format)
    want_color = bool(args.color)

    conv = convert_image(
        image_path=args.image,
        cols=args.cols,
        cell_aspect=cell_aspect,
        contrast=args.contrast,
        directional=args.directional,
        directional_exp=args.directional_exp,
        samples=args.samples,
        charset=charset,
        invert=args.invert,
        font_path=font_path,
        want_color=want_color,
    )

    if fmt == "png":
        img = render_png(conv, font_path, args.font_size, args.fg, args.bg, args.line_height)
        out_path = args.out or "out.png"
        img.save(out_path)
        sys.stderr.write("wrote {} ({}x{} chars)\n".format(out_path, conv.cols, len(conv.rows)))
    elif fmt == "svg":
        svg = render_svg(conv, font_path, args.font_size, args.fg, args.bg, args.line_height)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(svg)
            sys.stderr.write("wrote {} ({}x{} chars)\n".format(args.out, conv.cols, len(conv.rows)))
        else:
            sys.stdout.write(svg)
    else:  # txt
        text = render_ansi(conv) if want_color else render_txt(conv)
        if args.out:
            # Never write ANSI escapes to a file -- keep saved .txt clean.
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(render_txt(conv))
            sys.stderr.write("wrote {} ({}x{} chars)\n".format(args.out, conv.cols, len(conv.rows)))
        else:
            sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
