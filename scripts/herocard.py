#!/usr/bin/env python3
"""Render a skill's card as a fuller dark Textual "skill card" SVG.

The richer counterpart to the compact scorecard: a bordered card showing identity,
summary, WHEN TO USE, OUTPUT, DEPENDENCIES, QUALITY, and SECURITY — the same shape
as the README hero cards, rendered per skill. Every section below identity degrades
gracefully: a skill with no card.json yet (only a SKILL.md) renders its name and
when-to-use with the data-bearing sections marked "not yet carded"; a carded beta
skill with no metrics shows "not yet measured". So all six current skills render,
carded or not, with no invented values.

Composed with Rich renderables, rendered headless through Textual's pilot, then
exported via Rich's ``Console.export_svg`` with a chrome-free template — the same
deterministic, no-window-chrome approach as ``skillcard.scorecard`` and the repo
hero. ``render(card)`` takes a parsed card.json dict, or a sparse
``{"name", "description", ...}`` for an un-carded skill.

Requires Textual (the vendored ``tooling/califa[scorecard]`` extra installs it).
"""

from __future__ import annotations

import asyncio
import io
from typing import Any

from rich.console import Console, Group
from rich.table import Table
from rich.text import Text

NA = "grey50"

THRESHOLDS = {
    "status": {"stable": "green", "beta": "yellow", "draft": "grey50", "deprecated": "red"},
    "severity": {"LOW": "green", "MEDIUM": "yellow", "HIGH": "orange1", "CRITICAL": "red"},
    "numeric": [(0.90, "green"), (0.80, "chartreuse1"), (0.70, "yellow"), (0.60, "gold1"), (0.0, "red")],
}

SIM_WIDTH = 78
MEASURE_HEIGHT = 100
V_MARGIN = 2
PENDING = "not yet carded"


def _band_color(value: float) -> str:
    for floor, color in THRESHOLDS["numeric"]:
        if value >= floor:
            return color
    return NA


def _bar(value: float, width: int = 20) -> str:
    filled = max(0, min(width, round(value * width)))
    return "█" * filled + "░" * (width - filled)


def _metric_rows(rows: list[tuple[str, float]]) -> Table:
    t = Table.grid(expand=True)
    t.add_column(justify="left", width=13)
    t.add_column(justify="right", width=6)
    t.add_column(justify="left")
    for label, value in rows:
        t.add_row(Text("  " + label), Text(f"{value:.2f}"),
                  Text("  " + _bar(value), style=_band_color(value)))
    return t


def _kv_rows(rows: list[tuple[str, str, str]]) -> Table:
    t = Table.grid(expand=True)
    t.add_column(justify="left", width=13)
    t.add_column(justify="left")
    for label, value, style in rows:
        t.add_row(Text("  " + label), Text(value, style=style))
    return t


def _header_row(card: dict[str, Any]) -> Table:
    status = card.get("status", "draft")
    dot = THRESHOLDS["status"].get(status, NA)
    version = card.get("version")
    name_text = Text.assemble((card.get("name", "?"), "bold white"),
                              ((f"  v{version}" if version else ""), "dim"))
    t = Table.grid(expand=True)
    t.add_column(justify="left")
    t.add_column(justify="right")
    t.add_row(name_text, Text.assemble(("● ", dot), (status, "white")))
    return t


def _section(title: str) -> Text:
    return Text(title, style="bold cyan")


def _first_sentence(text: str, cap: int = 150) -> str:
    """A short summary from a long description: first sentence, capped."""
    text = " ".join((text or "").split())
    for sep in (". ", " — ", "; "):
        if sep in text:
            head = text.split(sep, 1)[0].strip().rstrip(".")
            if 20 <= len(head) <= cap:
                return head + "."
    return (text[:cap].rstrip() + "…") if len(text) > cap else text


def _when(text: str, cap: int = 240) -> str:
    """The WHEN TO USE line: the description trimmed to a sentence near *cap*.

    A card.json `description` is the full triggering blurb (often a paragraph),
    which would dwarf the card; this keeps the lead sentence or two and ends on a
    sentence boundary where possible, an ellipsis otherwise.
    """
    text = " ".join((text or "").split())
    if len(text) <= cap:
        return text
    boundary = text[:cap].rfind(". ")
    if boundary >= 80:
        return text[:boundary + 1]
    return text[:cap].rstrip() + "…"


def _body(card: dict[str, Any]) -> Group:
    summary = card.get("summary") or _first_sentence(card.get("description", ""))
    parts: list[Any] = [
        _header_row(card),
        Text(summary, style="dim italic"),
        Text(""),
    ]
    if card.get("description"):
        parts += [_section("WHEN TO USE"), Text("  " + _when(card["description"]), style="dim"), Text("")]

    out = card.get("output")
    if out:
        parts += [_section("OUTPUT"),
                  _kv_rows([("Type", out["type"], "white"), ("Format", out["format"], "white")])]
    else:
        parts += [_section("OUTPUT"), Text(f"  {PENDING}", style=f"italic {NA}")]
    parts.append(Text(""))

    deps = card.get("dependencies")
    if deps:
        parts += [_section("DEPENDENCIES"), *[Text("  " + d, style="white") for d in deps]]
    else:
        parts += [_section("DEPENDENCIES"), Text(f"  {PENDING}", style=f"italic {NA}")]
    parts.append(Text(""))

    metrics = card.get("metrics")
    parts.append(_section("QUALITY"))
    if metrics:
        rows = [("Precision", metrics["trigger_precision"]), ("Recall", metrics["trigger_recall"])]
        if metrics.get("near_miss_precision") is not None:
            rows.append(("Near-miss", metrics["near_miss_precision"]))
        rows += [("Task pass", metrics["task_completion_rate"]), ("Eval pass", metrics["eval_pass_rate"])]
        parts.append(_metric_rows(rows))
    elif card.get("scan"):
        parts.append(Text("  not yet measured — beta", style=f"italic {NA}"))
    else:
        parts.append(Text(f"  {PENDING}", style=f"italic {NA}"))
    parts.append(Text(""))

    scan = card.get("scan")
    parts.append(_section("SECURITY"))
    if scan:
        sev = scan["severity"]
        parts.append(_kv_rows([("SkillSpector", f"{scan['score']} / {sev}",
                                THRESHOLDS["severity"].get(sev, NA))]))
        if scan.get("note"):
            parts.append(Text("  " + scan["note"], style="dim"))
    else:
        parts.append(Text(f"  {PENDING}", style=f"italic {NA}"))

    footer = card.get("footer")
    if footer:
        parts += [Text(""), Text(footer, style="dim")]
    return Group(*parts)


_CARD_SVG_FORMAT = """<svg class="skill-card" viewBox="0 0 {terminal_width} {terminal_height}" xmlns="http://www.w3.org/2000/svg">
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


def _build_app(card: dict[str, Any]):
    from textual.app import App, ComposeResult
    from textual.containers import Container
    from textual.widgets import Static

    body = _body(card)

    class _Card(App):
        CSS = """
        Screen { align: center middle; }
        #card {
            width: 74;
            height: auto;
            border: round cyan;
            border-title-color: cyan;
            padding: 1 2;
            background: $surface;
        }
        """

        def compose(self) -> ComposeResult:
            container = Container(Static(body), id="card")
            container.border_title = "SKILL CARD"
            yield container

    return _Card()


def _export_clean(app) -> str:
    width, height = app.size
    console = Console(width=width, height=height, file=io.StringIO(), force_terminal=True,
                      color_system="truecolor", record=True, legacy_windows=False, safe_box=False)
    console.print(app.screen._compositor.render_update(
        full=True, screen_stack=app.app._background_screens, simplify=False))
    return console.export_svg(title="", code_format=_CARD_SVG_FORMAT)


async def _render_async(card: dict[str, Any]) -> str:
    measure = _build_app(card)
    async with measure.run_test(size=(SIM_WIDTH, MEASURE_HEIGHT)) as pilot:
        await pilot.pause()
        card_height = measure.query_one("#card").outer_size.height
    app = _build_app(card)
    async with app.run_test(size=(SIM_WIDTH, card_height + V_MARGIN)) as pilot:
        await pilot.pause()
        return _export_clean(app)


def render(card: dict[str, Any]) -> str:
    """Render a parsed card.json (or a sparse {name, description, ...}) to an SVG."""
    return asyncio.run(_render_async(card))
