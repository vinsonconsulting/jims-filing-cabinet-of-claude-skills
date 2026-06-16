# Architecture

The retained, reactive, DOM-like core of Textual. Read this before non-trivial work on
lifecycle, events, reactivity, or workers. All APIs here are verified against **8.2.7**.

## The DOM tree

`App` → `Screen` → `Widget` … `Widget`. Every node is a `Widget` (a `Screen` is a top-level
widget; the `App` owns a screen stack). Children are produced by `compose()`; the resulting
tree is **retained** — you mutate nodes and Textual repaints the dirty regions.

Query the tree with CSS selectors:

```python
self.query_one("#sidebar")              # first match, by id; raises NoMatches if absent
self.query_one("#lbl", Label)           # typed: returns Label, raises WrongType otherwise
self.query(".row")                       # DOMQuery of all matches (iterable)
self.query_one(Button)                   # by widget type
```

`query_one` raises `NoMatches` if nothing matches — that usually means you queried before
`on_mount` (the DOM wasn't built yet) or used the wrong selector.

## compose() and lifecycle

`compose()` is a generator that **runs once** to build a widget's children. Yield widgets, or
use a container as a context manager to nest:

```python
def compose(self) -> ComposeResult:
    yield Header()
    with Horizontal():
        yield Static("nav", id="sidebar")
        yield VerticalScroll(id="body")
    yield Footer()
```

Lifecycle hooks, in order:

- `on_mount` — the node and its children are mounted; **this is where you initialise state and
  touch widgets.** Do not query the DOM in `__init__` or `compose` — it isn't mounted.
- `on_ready` (App) — first paint done.
- `on_unmount` — node is being removed; workers on it are auto-cancelled.

Run the app with `App().run()` (blocking), `await App().run_async()` (inside an existing loop),
or `async with App().run_test() as pilot:` (tests). Mount widgets dynamically later with
`await self.mount(widget)` / `widget.remove()`.

## Messages and events

Input and widget notifications arrive as **messages** that **bubble** from the originating
widget up toward the `App`. Two ways to handle them:

```python
from textual import on

@on(Button.Pressed, "#save")        # decorator + optional CSS selector (preferred, since 0.23)
def _save(self) -> None: ...

def on_button_pressed(self, event: Button.Pressed) -> None:   # naming convention, no filter
    ...
```

Prefer `@on(...)` with a selector over a single `on_button_pressed` with a big `if event.button.id == …` chain. Control flow:

- `event.stop()` — stop bubbling (the parent won't see it).
- `event.prevent_default()` — skip the widget's built-in handling.

**Custom messages** are a nested `Message` subclass, posted with `post_message`:

```python
class FilePicker(Widget):
    class Picked(Message):
        def __init__(self, path: str) -> None:
            self.path = path
            super().__init__()
    def _choose(self, path: str) -> None:
        self.post_message(self.Picked(path))     # bubbles to whoever handles FilePicker.Picked
```

Handlers run on the message pump in order; keep them fast (offload work to `@work`).

## Actions and BINDINGS

`BINDINGS` maps keys to **actions** (`action_*` methods); the bound description shows in the
`Footer`.

```python
class App(App):
    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        Binding("q", "quit", "Quit", show=False),   # Binding(...) for extra options
    ]
    def action_save(self) -> None: ...
```

Actions can take parameters via the action string (`"set_theme('nord')"`) and can live on any
widget in the focus chain. `Binding` (from `textual.binding`) adds `show`, `priority`, `key_display`.

## Screens, modals, and results

Screens are full-window widgets you push/pop. A modal returns a value to its caller:

```python
from textual.screen import ModalScreen

class Confirm(ModalScreen[bool]):                # typed result
    def compose(self) -> ComposeResult:
        yield Button("Yes", id="yes")
        yield Button("No", id="no")
    @on(Button.Pressed, "#yes")
    def _yes(self) -> None: self.dismiss(True)   # return value to the caller
    @on(Button.Pressed, "#no")
    def _no(self) -> None: self.dismiss(False)

# caller — await the result (don't fire-and-forget):
@work
async def ask(self) -> None:
    if await self.push_screen_wait(Confirm()):
        ...
```

Use `push_screen_wait()` (in a worker) or `push_screen(screen, callback=...)`. Don't treat
`push_screen`/`dismiss` as synchronous — wait for the result.

## Reactivity internals

`reactive(default)` is a descriptor. On assignment Textual runs, in order:

1. `validate_<name>(value)` → return a coerced/clamped value (optional)
2. `compute_<name>()` → recompute derived reactives (optional)
3. `watch_<name>(old, new)` → react (optional)

then a **smart refresh** (repaint, or relayout if `layout=True`). Flags on `reactive(...)`:

| Flag | Effect |
| --- | --- |
| `init=True` (default) | run watchers once at mount |
| `always_update=True` | fire watchers even when the value is unchanged |
| `layout=True` | trigger a relayout, not just a repaint |
| `repaint=False` | no automatic repaint |
| `recompose=True` | re-run `compose()` on change (rebuild children) |
| `bindings=True` | refresh the footer/bindings |

`var(default)` is a reactive that never auto-refreshes (plain observable state). **Footgun:**
mutating a list/dict reactive in place does not fire watchers — reassign, call
`self.mutate_reactive(Cls.attr)`, or declare `always_update=True`. Setting a reactive in
`__init__` can fire a watcher against the unmounted DOM (`NoMatches`); use `self.set_reactive(Cls.attr, value)`
to set without triggering.

## Workers (concurrency)

Textual is single-threaded asyncio. **Never block the event loop.** Offload with `@work`:

```python
from textual import work

@work                                   # ASYNC worker: awaitable I/O (httpx, async SDKs)
async def fetch(self) -> None:
    data = await client.get(...)
    self.query_one(DataTable).add_rows(data)     # safe: async workers run on the loop

@work(thread=True)                      # THREAD worker: blocking/sync calls
def crunch(self) -> None:
    result = slow_blocking_call()
    self.call_from_thread(self.query_one(Label).update, result)   # UI only via call_from_thread
```

- A bare `@work` on a **sync** `def` raises `WorkerDeclarationError` — sync work needs `thread=True`.
- From a **thread** worker, never touch widgets directly; marshal with `self.call_from_thread(fn, *args)` or `post_message`.
- `@work(exclusive=True, group="g")` cancels any running worker in that group before starting — ideal for "cancel the previous request when a new one starts".
- Workers auto-cancel when their node is removed or the app exits. Handle errors via the worker's state or `exit_on_error`.
