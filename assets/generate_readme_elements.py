#!/usr/bin/env python3
"""Render the README's static explainer elements as dark Textual-card SVGs.

Three pieces that were plain markdown — the score-band table, the "worked card"
field table, and the skill-folder layout tree — rendered in the same dark Textual
card style as the per-skill cards and the hero, so the README reads as one piece.
Each is a Rich renderable (Table / Tree) wrapped in a one-screen Textual card and
exported via Rich's chrome-free `export_svg` (no fake terminal window), the same
approach as `scripts/herocard.py`. Output is deterministic; height-cropped.

These are *static* elements (no card.json input), so this is a hand-run asset step,
not wired into make check — re-run it when the copy changes. The catalog tables are
deliberately NOT converted: an `<img>` SVG would drop their clickable per-skill links.

Requires Textual (`pip install textual==8.2.7`). Run:
    python3 assets/generate_readme_elements.py
"""

from __future__ import annotations

import asyncio
import io
from pathlib import Path

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

OUT_DIR = Path(__file__).resolve().parent / "readme-elements"

SEVERITY = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "orange1", "CRITICAL": "red"}

_FMT = """<svg class="readme-element" viewBox="0 0 {terminal_width} {terminal_height}" xmlns="http://www.w3.org/2000/svg">
    <style>
    @font-face {{
        font-family: "Fira Code";
        src: local("FiraCode-Regular"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Regular.woff2") format("woff2"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Regular.woff") format("woff");
        font-style: normal;
        font-weight: 400;
    }}
    @font-face {{
        font-family: "Fira Code";
        src: local("FiraCode-Bold"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Bold.woff2") format("woff2"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Bold.woff") format("woff");
        font-style: bold;
        font-weight: 700;
    }}
    .{unique_id}-matrix {{
        font-family: Fira Code, monospace;
        font-size: {char_height}px;
        line-height: {line_height}px;
        font-variant-east-asian: full-width;
    }}
    {styles}
    </style>
    <defs>
    <clipPath id="{unique_id}-clip-terminal">
      <rect x="0" y="0" width="{terminal_width}" height="{terminal_height}" />
    </clipPath>
    {lines}
    </defs>
    <g clip-path="url(#{unique_id}-clip-terminal)">
    {backgrounds}
    <g class="{unique_id}-matrix">
    {matrix}
    </g>
    </g>
</svg>
"""


def _build_app(renderable, title: str, width: int):
    from textual.app import App, ComposeResult
    from textual.containers import Container
    from textual.widgets import Static

    class _Element(App):
        CSS = """
        Screen { align: center middle; }
        #card {
            width: %d;
            height: auto;
            border: round cyan;
            border-title-color: cyan;
            padding: 1 2;
            background: $surface;
        }
        """ % width

        def compose(self) -> ComposeResult:
            container = Container(Static(renderable), id="card")
            container.border_title = title
            yield container

    return _Element()


def _export_clean(app) -> str:
    width, height = app.size
    console = Console(width=width, height=height, file=io.StringIO(), force_terminal=True,
                      color_system="truecolor", record=True, legacy_windows=False, safe_box=False)
    console.print(app.screen._compositor.render_update(
        full=True, screen_stack=app.app._background_screens, simplify=False))
    return console.export_svg(title="", code_format=_FMT)


async def _render(renderable, title: str, width: int, out: Path) -> None:
    measure = _build_app(renderable, title, width)
    async with measure.run_test(size=(width + 4, 80)) as pilot:
        await pilot.pause()
        height = measure.query_one("#card").outer_size.height
    app = _build_app(renderable, title, width)
    async with app.run_test(size=(width + 4, height + 2)) as pilot:
        await pilot.pause()
        out.write_text(_export_clean(app), encoding="utf-8")


# --- the three elements --------------------------------------------------------

def score_bands() -> Table:
    """The SkillSpector score → gate table, with each band in its threshold colour."""
    t = Table(box=box.SIMPLE_HEAD, expand=True, header_style="bold cyan", pad_edge=False)
    t.add_column("Band", justify="left", width=10)
    t.add_column("Score", justify="left", width=9)
    t.add_column("Gate", justify="left", ratio=1)
    rows = [
        ("LOW", "0–20", "Passes."),
        ("MEDIUM", "21–50", "Passes only if every finding is recorded on the card as accepted, with a written note."),
        ("HIGH", "51–80", "Hard fail. Does not merge."),
        ("CRITICAL", "81–100", "Hard fail. Does not merge."),
    ]
    for band, score, gate in rows:
        t.add_row(Text(band, style=f"bold {SEVERITY[band]}"),
                  Text(score, style="white"), Text(gate, style="dim"))
    return t


def worked_card() -> Table:
    """The `textual` worked example at a glance (mirrors skills/tui/textual/card.json)."""
    t = Table(box=box.SIMPLE_HEAD, expand=True, header_style="bold cyan", pad_edge=False)
    t.add_column("Field", justify="left", width=13)
    t.add_column("Value", justify="left", ratio=1)
    t.add_row(Text("Scan"), Text.assemble(("LOW", "bold green"), (" (0/100), no findings", "white")))
    t.add_row(Text("Permissions"), Text("shell, file (no network, env, or MCP)", style="white"))
    t.add_row(Text("Dependencies"), Text("textual>=8.2,<9 · rich>=15.0 · python>=3.9", style="white"))
    t.add_row(Text("Source"), Text("pinned to a content_hash of the skill folder", style="dim"))
    t.add_row(Text("Status"), Text.assemble(("● ", "yellow"), ("beta", "white")))
    return t


def skill_layout() -> Tree:
    """The skills/<category>/<skill-name>/ folder layout."""
    tree = Tree(Text("skills/<category>/<skill-name>/", style="bold white"), guide_style="grey37")
    items = [
        ("SKILL.md", "required: frontmatter (name + description) + instructions"),
        ("README.md", "this skill's page (card blocks rendered from card.json)"),
        ("card.json", "the Skill Card: scan, triggers, metrics, provenance"),
        ("skill-card.md", "human-readable view of the card"),
        ("report.sarif", "SkillSpector findings"),
        ("evals/", "trigger + functional eval cases"),
        ("references/", "optional: docs the skill points to"),
        ("scripts/", "optional: helper scripts the skill runs"),
        ("assets/", "optional: templates, fonts, samples"),
    ]
    for name, note in items:
        tree.add(Text.assemble((name.ljust(15), "white"), ("# " + note, "dim")))
    return tree


async def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    await _render(score_bands(), "SCORE BANDS", 84, OUT_DIR / "score-bands.svg")
    await _render(worked_card(), "A WORKED CARD: textual", 72, OUT_DIR / "worked-card.svg")
    await _render(skill_layout(), "SKILL LAYOUT", 90, OUT_DIR / "skill-layout.svg")
    print(f"wrote 3 elements to {OUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
