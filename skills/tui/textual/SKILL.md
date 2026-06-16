---
name: textual
description: >-
  Use this skill when building or debugging a Python terminal UI (TUI) with Textual
  (Textualize's framework) — `App`/`Screen`/`Widget`, `compose()`, `reactive`/`watch_`,
  `@work` workers, Textual CSS / TCSS (`dock`, `grid`, `fr` units), widgets like `RichLog`,
  `Markdown`, `DataTable`, `Input`, `TextArea`, `Tree`, `ListView`; testing with `Pilot` /
  `pytest-textual-snapshot`; `textual serve` / Textual Web deploy; Rich renderables inside
  Textual; or streaming LLM/agent tokens into a terminal and agentic-CLI front-ends. Triggers:
  Textual, Textualize, TUI, terminal UI, `@work`, TCSS, `RichLog`, `query_one`, Pilot,
  `textual serve`. Writes current 8.x code, not stale pre-1.0 patterns. Not for: Rust TUIs
  (→ Ratatui sibling), Go TUIs (→ Bubble Tea sibling), plain non-interactive CLI output
  (Click/argparse/Typer) with no live UI, or agent-session orchestration / tmux multiplexing.
  Note: browser deploy via `textual serve` (the same Textual app served to a browser) IS in
  scope — a general React/HTML web-app request is not.
---

# Textual

Write current, compiling Textual code (pinned to **8.2.7**, Python **≥3.9**, Rich **15.0.0**)
and refuse the pre-1.0 / 0.x patterns the model remembers from training — the 1.0 (Dec 2024)
and 2.0 (Feb 2025) releases were hard breaks. The body is the load-bearing 20%: one mental
model and one **run-verified** example per concept. Everything enumerable — the full widget
catalog, every TCSS rule, the streaming model, testing, deploy, migration — lives in
`references/`. Open the matching reference before writing nontrivial code in that area.

## Mental model

Textual is a **retained, reactive, DOM-like** framework — the opposite of Ratatui's
immediate mode and Bubble Tea's MVU. You build a tree of widget objects **once**, then mutate
their state; Textual re-renders only the affected parts, like a web framework. It is
**async-native** (asyncio) and styled with **Textual CSS (TCSS)**, not layout math.

Four nouns carry everything:

- **App** — the application and event loop; `App().run()` (or `await run_async()`). Holds screens, handles input, owns the `@work` workers.
- **Screen** — a full-window container you push/pop; the default screen hosts your `compose()`. Modals/dialogs are screens.
- **Widget** — a node in the DOM tree. **Leaf** widgets draw themselves (`render()`); **compound** widgets yield children (`compose()`).
- **DOM + TCSS** — widgets form a tree you query with `query_one`/`query` (CSS selectors) and style with TCSS. Mutating a widget's `reactive` state schedules a repaint.

## App, compose, and lifecycle

`compose()` runs **once** to build the tree; never touch widgets there — the DOM isn't mounted
yet. Wait for `on_mount`, then resolve widgets by selector with `query_one`.

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Label

class CounterApp(App):
    BINDINGS = [("a", "add", "Add"), ("q", "quit", "Quit")]   # key → action_* → footer hint

    def compose(self) -> ComposeResult:        # build the tree ONCE
        yield Header()
        yield Label("count: 0", id="lbl")
        yield Button("hit", id="btn")
        yield Footer()

    def on_mount(self) -> None:                 # DOM is live; safe to touch widgets
        self.count = 0

    def action_add(self) -> None:               # bound to "a"
        self.count += 1
        self.query_one("#lbl", Label).update(f"count: {self.count}")

if __name__ == "__main__":
    CounterApp().run()
```

`Header()`/`Footer()` auto-dock to the top/bottom. Lifecycle order is `on_mount` →
`on_ready` → (running) → `on_unmount`. Run with `App().run()`, `run_async()` inside an existing
loop, or `App().run_test()` in tests. Full event/action/BINDINGS detail: `references/architecture.md`.

## Reactivity

Declare state with `reactive(default)`. On assignment Textual runs `validate_` → `compute_` →
`watch_`, then does a smart refresh. Use `var()` for state that should **not** auto-refresh.

```python
from textual.reactive import reactive
from textual.widget import Widget

class Thermostat(Widget):
    temp = reactive(20)                                  # auto-refresh on change
    def validate_temp(self, value: int) -> int:
        return max(0, min(100, value))                   # 1. coerce/clamp
    def watch_temp(self, old: int, new: int) -> None:
        self.refresh()                                   # 3. react to the change
```

**The mutable-reactive footgun:** assigning fires watchers; mutating **in place does not**.

```python
items = reactive(list)               # factory default for mutable state
self.items.append(x)                 # SILENT — watch_items does NOT fire
self.items = [*self.items, x]        # reassign → fires
self.mutate_reactive(Thermostat.items)   # canonical: notify after an in-place change
```

Setting a reactive in `__init__` can fire a watcher against the unmounted DOM (`NoMatches`);
use `set_reactive` to set without triggering. Flags (`init`, `always_update`, `layout`,
`recompose`, `bindings`): `references/architecture.md`.

## Messages and events

Widgets communicate by **posting messages that bubble up** the DOM. Handle them with
`@on(MessageType, "selector")` (preferred since 0.23) or an `on_<message>` method — both beat a
giant `on_button_pressed` if-chain. Define custom messages as a nested `Message` subclass.

```python
from textual import on
from textual.message import Message
from textual.widgets import Button

class Stepper(Widget):
    class Changed(Message):                      # nested custom message
        def __init__(self, delta: int) -> None:
            self.delta = delta
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Button("+", id="inc")

    @on(Button.Pressed, "#inc")                  # selector-filtered handler
    def _inc(self) -> None:
        self.post_message(self.Changed(+1))      # bubbles toward the App

# in the parent App:
    @on(Stepper.Changed)
    def _on_changed(self, message: Stepper.Changed) -> None:
        self.total += message.delta
```

Call `event.stop()` to halt bubbling. `references/architecture.md` has the event taxonomy and
the `BINDINGS` → `action_*` flow.

## Layout with Textual CSS

TCSS lives in a class `CSS` string (or `CSS_PATH`). `dock` pins a widget to a non-scrolling
edge; the `fr` unit distributes leftover space; containers from `textual.containers` group
children. Selectors target type (`Button`), id (`#sidebar`), or class (`.panel`).

```python
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Static

class Dashboard(App):
    CSS = """
    #topbar  { dock: top; height: 1; background: $panel; }
    #status  { dock: bottom; height: 1; }
    #sidebar { width: 24; }                 /* fixed-width column */
    #body    { width: 1fr; }                /* fills the rest      */
    """
    def compose(self) -> ComposeResult:
        yield Static("title", id="topbar")
        with Horizontal():
            yield Static("nav", id="sidebar")
            yield VerticalScroll(id="body")
        yield Static("ready", id="status")
```

Grids use `layout: grid; grid-size: 2 2; grid-gutter: 1`. Iterate styling live with
`textual run --dev` (TCSS hot-reload). Selectors, the box model, units, grids, containers, and
themes: `references/styling-and-layout.md`.

## Custom widgets: `render()` vs `compose()`

A **leaf** widget implements `render()` (returns a string/Rich/Content renderable). A
**compound** widget implements `compose()` (yields child widgets). Pick one — never both.

```python
class Pct(Widget):                    # LEAF
    pct = reactive(0)
    def render(self) -> str:
        return f"{self.pct}%"

class Card(Widget):                   # COMPOUND
    def compose(self) -> ComposeResult:
        yield Label("title")
        yield Pct()
```

Catalog, the `*State`-free reactive pattern, and authoring guidance: `references/widgets.md`.

## Streaming LLM/agent output (the hero use-case)

Stream from a `@work` async worker so the event loop never blocks. For Markdown, **don't
remove-and-remount per token** — use `Markdown.get_stream()`, which coalesces fast updates
(~20/s) and re-renders only the last block. Pin to the bottom with `container.anchor()`.

```python
from textual import work
from textual.widgets import Markdown
from textual.containers import VerticalScroll

class Chat(App):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Markdown()

    @work                                              # async worker; never blocks the loop
    async def stream_reply(self) -> None:
        markdown_widget = self.query_one(Markdown)
        self.query_one(VerticalScroll).anchor()        # stick to bottom
        stream = Markdown.get_stream(markdown_widget)  # classmethod — pass the widget
        try:
            async for chunk in llm_client.stream(...):
                await stream.write(chunk)              # await: write AND stop are async
        finally:
            await stream.stop()
```

For colored log scrollback instead of Markdown, use
`RichLog(highlight=True, markup=True, auto_scroll=True)` + `.write(...)`. The full streaming
model (cancellation, exclusivity, RichLog vs anchored `VerticalScroll`, reference apps):
`references/agent-ui.md`.

## Golden rules

- **Never block the event loop.** Async I/O (httpx, async LLM SDKs) → `@work` async. Blocking
  or sync calls (`requests`, `time.sleep`) → `@work(thread=True)` — a bare `@work` on a sync
  `def` raises `WorkerDeclarationError`. From a **thread** worker, touch the UI only via
  `self.call_from_thread(fn, *args)`; async workers may update the UI between `await`s.
- **A list/dict `reactive` won't fire watchers on in-place change** — reassign or `mutate_reactive`.
- **`compose()` runs once.** Mutate the live DOM in `on_mount`/handlers; find widgets with `query_one`.
- **Test with Pilot.** `async with app.run_test() as pilot:` then `await pilot.pause()` before
  asserting (let pending messages drain). See `references/testing.md`.

## Stale patterns to reject

These are pre-1.0 / 0.x and break (or silently misbehave) on 8.2.7:

| Reject | Use instead |
| --- | --- |
| `TextLog` | `RichLog` (renamed) |
| bare `@work` on a sync `def` | `@work(thread=True)` (else `WorkerDeclarationError`) |
| `self.items.append(x)` expecting a watcher to fire | reassign, or `self.mutate_reactive(Cls.items)` |
| `Reactive(...)` to **declare** state | `reactive(...)` / `var(...)` (`Reactive` is the base type — fine in annotations) |
| `self.view.dock(...)` / `edge=` | `dock:` in TCSS (`App.view` is gone) |
| `Static(renderable=...)` / `.renderable` | `Static(content=...)` / `.content` |
| `Select.BLANK` as the empty value | `Select.NULL` (`BLANK` is now the bool `False` — silently breaks) |
| `Switch.action_toggle` for the toggle binding | `action_toggle_switch` (the bound action) |
| remove + remount `Markdown` per token | `Markdown.get_stream(widget)` + `await stream.write/stop` |
| `time.sleep` / blocking `requests` in a handler | `@work` async (or `@work(thread=True)`) |

Confirmed against **textual 8.2.7 / rich 15.0.0 / Python 3.14** (floor 3.9): `TextLog` is gone;
a bare `@work` on a sync fn raises `WorkerDeclarationError`; in-place `reactive` mutation does
not fire watchers; `Markdown.get_stream` is a classmethod and `write`/`stop` are awaitable;
`Select.NULL` (not `BLANK`) is the no-selection sentinel; `events.Load` still exists (do **not**
assume `on_load` was removed). The full deprecation map is in `references/versioning.md` — and
`scripts/verify.py` re-runs these checks against your installed Textual after an upgrade.

## Reference map

- `references/architecture.md` — DOM tree, compose/lifecycle, messages/events/`@on`, actions/BINDINGS, reactivity internals, workers (`@work`/`call_from_thread`/exclusivity).
- `references/styling-and-layout.md` — TCSS selectors, box model, `dock`, `grid`, `fr`/units, containers, hot-reload, themes/variables.
- `references/widgets.md` — full built-in catalog, "when to reach for each", custom-widget authoring (`render` vs `compose`).
- `references/text-and-unicode.md` — content markup, `Content`/`from_markup`, the Rich-vs-Textual boundary, wrapping/escaping (never f-string markup on untrusted input).
- `references/agent-ui.md` — streaming LLM/agent tokens in-process (`get_stream`/`MarkdownStream`, RichLog + anchor, cancellation); orchestration/tmux is out of scope.
- `references/testing.md` — Pilot, `run_test`, `pilot.pause`, `pytest-textual-snapshot`, `asyncio_mode`.
- `references/ecosystem.md` — Rich, textual-dev, pytest-textual-snapshot, textual-plotext, third-party widgets.
- `references/versioning.md` — pinned versions, Python floor, maintenance status, and the reject-list / deprecation map.
- `references/web-deploy.md` — `textual serve` / textual-serve / Textual Web; what works in the browser; the honest "self-host on a VM/container/PaaS, not edge/serverless" read.
- `scripts/verify.py` — re-run the load-bearing snippets against your installed Textual to confirm the skill still holds after an upgrade.
