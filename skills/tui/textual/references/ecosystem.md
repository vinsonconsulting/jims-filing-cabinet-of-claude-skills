# Ecosystem

The packages around Textual and what each is for. Versions are what resolved on **2026-06-16**;
re-check with `pip show`.

## Rich (the foundation)

**rich 15.0.0.** Textual renders on top of Rich. You meet Rich whenever you pass a renderable
(`rich.table.Table`, `Panel`, `Syntax`, `Text`, `rich.markdown.Markdown`) to a `Static` or
`RichLog`. Use Rich renderables for one-shot richly-formatted *content*; use Textual widgets for
live, interactive, CSS-styled UI. Rich also provides the cell-width math (`rich.cells.cell_len`)
behind Textual's wrapping — see `text-and-unicode.md`.

## textual-dev (the dev CLI — separate package)

**textual-dev 1.8.0.** Installs the `textual` command. Not needed at runtime; install it for
development.

| Command | Use |
| --- | --- |
| `textual run --dev app.py` | run with TCSS **hot-reload** + debug features |
| `textual console` | live devtools console: `print`/log output, events, timings (run the app with `--dev` in another pane) |
| `textual serve app.py` | serve the app in a browser over a local web server (see `web-deploy.md`) |
| `textual colors` | browse the theme/design-system palette |
| `textual borders` | preview border styles |
| `textual keys` | inspect key events (find the right key name for a binding) |
| `textual diagnose` | dump environment info for bug reports |

## Testing

- **pytest-textual-snapshot 1.1.0** — the `snap_compare` fixture for SVG snapshot tests (separate package; see `testing.md`).
- **pytest-asyncio** (or `anyio`) — run the `async def` Pilot tests; set `asyncio_mode = "auto"`.

## Plotting & widgets

- **textual-plotext** — embed Plotext charts (line/scatter/bar) as a Textual widget; the idiomatic way to plot in a Textual app.
- **textual-autocomplete**, **textual-pandas**, **textual-fspicker**, **textual-image** (terminal image protocols) — common third-party widgets. Pin them and check they track your Textual version before relying on them.

## Maintenance note

Textualize (the company) wound down in mid-2025, but Will McGugan maintains both Textual and
Rich and ships briskly (7.0.0 in Jan 2026 → 8.2.7 in May 2026) and builds his own app (Toad) on
it. Treat it as healthy to build against; pin versions and re-verify after upgrades with
`scripts/verify.py`. Star count is order-of-magnitude ~35k.
