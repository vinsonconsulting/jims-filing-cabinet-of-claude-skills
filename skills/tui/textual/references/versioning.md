# Versioning & the deprecation map

Pinned versions, the Python floor, and the reject-list of stale patterns. Every entry below was
**executed** against the pinned versions, not taken from training data. Re-run `scripts/verify.py`
after upgrading Textual to catch new drift.

## Pins (resolved 2026-06-16)

| Package | Version | Notes |
| --- | --- | --- |
| **textual** | **8.2.7** | MIT, Production/Stable. `Requires-Python: >=3.9,<4.0` |
| **rich** | **15.0.0** | the rendering foundation |
| textual-dev | 1.8.0 | dev CLI (`textual run --dev`, `console`, `serve`) |
| pytest-textual-snapshot | 1.1.0 | `snap_compare` fixture |
| textual-serve | 1.1.3 | browser serving |

**Python floor: 3.9** (verified from `textual`'s metadata). The **1.0** (Dec 2024) and **2.0**
(Feb 2025) releases were the breaking boundaries — any 0.x API in training data is suspect.
Pin the major and let patches flow; Textual ships roughly weekly, so a newer patch than 8.2.7 is
likely by the time you read this. Pin what actually resolves and re-verify.

## Reject-list / deprecation map (the grep targets)

Verified against 8.2.7. Each "Reject" either errors, is renamed, or silently misbehaves.

| Reject (pre-1.0 / 0.x) | Use instead | Why |
| --- | --- | --- |
| `from textual.widgets import TextLog` | `RichLog` | `TextLog` removed → `ImportError` |
| bare `@work` on a **sync** `def` | `@work(thread=True)` | raises `WorkerDeclarationError` at decoration |
| `self.items.append(x)` expecting `watch_items` | reassign, or `self.mutate_reactive(Cls.items)` | in-place mutation does not notify |
| `Reactive(...)` to **declare** a reactive | `reactive(...)` / `var(...)` | `Reactive` is the base class — keep it only in type annotations like `Reactive[int]` |
| `self.view.dock(...)`, `edge=` | `dock:` in TCSS + `compose()` | `App.view` and pre-CSS docking are gone |
| `Static(renderable=...)`, `widget.renderable` | `Static(content=...)`, `widget.content` | renamed; instances expose `.content`, not `.renderable` |
| `Select.BLANK` as the empty value | `Select.NULL` | `BLANK` is now the bool `False`; the no-selection sentinel is `NULL` (`NoSelection`), so `is Select.BLANK` silently breaks |
| `Switch.action_toggle` as the toggle | `action_toggle_switch` | the binding action is `toggle_switch`; `action_toggle` is inherited and unrelated |
| remove + remount `Markdown` per token | `Markdown.get_stream(widget)` | classmethod; coalesces updates |
| `stream.stop()` / `stream.write(...)` unawaited | `await stream.stop()` / `await stream.write(...)` | both are coroutines |
| `md.get_stream()` (instance call) | `Markdown.get_stream(md)` | it's a **classmethod** taking the widget |
| `time.sleep` / blocking `requests` in a handler | `@work` async (or `@work(thread=True)`) | blocking the loop freezes the UI |
| fire-and-forget `push_screen` / `dismiss` | `push_screen_wait()` / `push_screen(cb=...)` | results are async |
| `tea`/Elm-style or immediate-mode redraw loops | retained DOM + `reactive` | wrong framework's mental model |

## Do NOT over-reject (these are current and correct)

- `events.Load` / `on_load` **still exist** — do not "modernise" them away.
- `Reactive[int]` as a **type annotation** is correct — only the `Reactive(...)` *constructor call* to declare state is stale.
- `Select.NULL`, `Static(content=...)`, `RichLog`, `@work(thread=True)`, `mutate_reactive`,
  `set_reactive`, `Markdown.get_stream`, `push_screen_wait`, `call_from_thread` are all current.
- `var(...)` (no-auto-refresh reactive) is current, not a typo for `reactive`.

## Migration heuristic

If a snippet looks like Textual 0.x — `TextLog`, manual `dock()`/`view`, `Select.BLANK`,
synchronous screen results, per-token Markdown remount, or blocking calls in handlers — it
predates 1.0/2.0. Rewrite to the right column above and confirm with `scripts/verify.py`.
