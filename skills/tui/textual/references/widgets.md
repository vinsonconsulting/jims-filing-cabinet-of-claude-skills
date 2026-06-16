# Widgets

The built-in catalog, when to reach for each, the messages they post, and how to author your
own. All import from `textual.widgets`. Verified against **8.2.7**.

## Choosing a widget

| Need | Widget | Key message |
| --- | --- | --- |
| Static text / Rich renderable | `Static`, `Label`, `Digits`, `Pretty` | — |
| Scrolling colored log | `RichLog` (markup/highlight) or `Log` (fast plain text) | — |
| Streaming/render Markdown | `Markdown`, `MarkdownViewer` | `Markdown.LinkClicked` |
| A button | `Button` | `Button.Pressed` |
| One-line text entry | `Input` | `Input.Submitted`, `Input.Changed` |
| Multi-line / code editor | `TextArea` | `TextArea.Changed`, `TextArea.SelectionChanged` |
| Pick from a vertical list | `ListView` (+ `ListItem`) | `ListView.Selected`, `.Highlighted` |
| Pick from many options | `OptionList` | `OptionList.OptionSelected` |
| Multi-select checklist | `SelectionList` | `SelectionList.SelectedChanged` |
| Dropdown | `Select` | `Select.Changed` |
| Tabular data, selectable rows | `DataTable` | `DataTable.RowSelected`, `.CellSelected` |
| Tree / file hierarchy | `Tree`, `DirectoryTree` | `Tree.NodeSelected`, `.NodeExpanded` |
| Toggles | `Switch`, `Checkbox`, `RadioButton`/`RadioSet` | `Switch.Changed`, … |
| Progress / activity | `ProgressBar`, `LoadingIndicator` | — |
| Tabs | `TabbedContent` (+ `TabPane`), `Tabs` | `TabbedContent.TabActivated` |
| Collapsible section | `Collapsible` | `Collapsible.Toggled` |
| Chrome | `Header`, `Footer` (auto-dock), `Rule` | — |
| Sparkline / plot | `Sparkline` (+ `textual-plotext`) | — |

Prefer a built-in over hand-rolling: `ListView`/`OptionList`/`DataTable` already handle
scrolling, selection, and keyboard nav. Forward `on_mount` sizing to them; don't reimplement scrollback.

## The selection-message pattern

Selectable widgets post a message; handle it with `@on` and read the payload — never poll:

```python
from textual import on
from textual.widgets import DataTable, ListView, OptionList

@on(DataTable.RowSelected)
def _row(self, event: DataTable.RowSelected) -> None:
    self.show_detail(event.row_key)

@on(ListView.Selected)
def _item(self, event: ListView.Selected) -> None:
    self.open(event.item)

@on(OptionList.OptionSelected)
def _opt(self, event: OptionList.OptionSelected) -> None:
    self.choose(event.option.prompt)
```

`DataTable` posts `RowSelected`/`CellSelected`/`RowHighlighted`/`CellHighlighted`/`ColumnSelected`;
populate it with `add_columns(...)` then `add_row(...)`/`add_rows(...)`, and set `cursor_type`
(`"row"`, `"cell"`, `"column"`). Update a list by changing its data and refreshing, or with a
`recompose=True` reactive — don't tear down and rebuild the whole widget per change.

## RichLog vs Log vs Static

- **`RichLog`** — appendable, scrolling log of Rich renderables. `RichLog(highlight=True, markup=True, auto_scroll=True, wrap=True)`, then `.write(renderable)`. `auto_scroll` sticks to the bottom. Use for colored output, tracebacks, REPL-style logs.
- **`Log`** — same idea, plain text, much faster; use for high-volume plain lines.
- **`Static`/`Label`** — a single renderable you `.update(...)`. **Not** a log — don't concatenate a growing string into a `Static` to fake scrollback.

## Custom widgets: `render()` vs `compose()`

A **leaf** widget draws itself with `render()`; a **compound** widget yields children with
`compose()`. Implement exactly one.

```python
from textual.widget import Widget
from textual.reactive import reactive

class Spark(Widget):                      # LEAF
    DEFAULT_CSS = "Spark { height: 1; }"
    value = reactive(0.0)
    def render(self):
        filled = int(self.value * 10)
        return "▇" * filled + "·" * (10 - filled)

class StatCard(Widget):                   # COMPOUND
    def compose(self):
        yield Label("CPU")
        yield Spark()
```

- Drive visible state with `reactive(...)` + a `watch_`/`render()` — no manual `*State` object.
- Post a nested `Message` for events the parent should handle (see `architecture.md`).
- `render()` may return a `str`, a Rich renderable, or a Textual `Content` (see `text-and-unicode.md`).
- For a custom widget that needs focus/keys, set `can_focus = True` and add `BINDINGS`.
