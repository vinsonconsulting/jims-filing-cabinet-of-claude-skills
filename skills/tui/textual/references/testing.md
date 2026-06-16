# Testing

Textual's testing story is a genuine superpower: drive a real app headlessly with **Pilot**,
assert on widget state, and snapshot-test the rendered SVG. Verified against **8.2.7**
(`pytest-textual-snapshot` **1.1.0**).

## Pilot + run_test

`App.run_test()` is an async context manager yielding a `Pilot`. It runs the app headless (no
real terminal) at a fixed size.

```python
import pytest
from myapp import CounterApp
from textual.widgets import Label

async def test_counter():
    app = CounterApp()
    async with app.run_test() as pilot:        # size defaults to (80, 24), headless=True
        await pilot.press("a", "a", "a")        # send keys
        await pilot.pause()                      # let messages drain BEFORE asserting
        assert "count: 3" in str(app.query_one("#lbl", Label).render())
```

`run_test(size=(120, 40))` sets the viewport. The Pilot surface:

| Call | Does |
| --- | --- |
| `await pilot.press("a", "ctrl+s", "enter")` | send key events in order |
| `await pilot.click("#save")` / `double_click` / `triple_click` | mouse on a selector/widget |
| `await pilot.hover("#row")` | hover |
| `await pilot.pause()` | **await until pending messages are processed** — call before asserting |
| `await pilot.resize_terminal(100, 30)` | simulate a resize |
| `await pilot.wait_for_animation()` | wait out animations |
| `await pilot.exit(result)` | stop the app with a result |

The single most common test bug is asserting before `await pilot.pause()` — the action you just
triggered hasn't been handled yet, so the DOM still shows the old value.

## asyncio mode

Tests are `async def`, so configure an async runner. With `pytest-asyncio`, set auto mode in
`pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

(`anyio` works too.) Without this, async tests are silently skipped or error on collection.

## Snapshot testing

`pytest-textual-snapshot` renders the app to an SVG and compares it against a stored baseline —
great for catching unintended layout/style regressions.

```python
def test_layout(snap_compare):
    assert snap_compare("path/to/app.py")                       # compare full app
    # assert snap_compare("app.py", press=["tab", "enter"])     # after interactions
    # assert snap_compare("app.py", terminal_size=(120, 40))
```

`snap_compare` is a pytest fixture (installed with the plugin). First run records the baseline;
update intentional changes with `pytest --snapshot-update`. Snapshots are SVG, so visual diffs
are reviewable. Don't snapshot graphics-protocol output (Sixel/Kitty) — it isn't captured.

## What to test where

- **Logic / state** — drive with Pilot and assert on `reactive` values and `query_one(...).render()`. Fast and precise.
- **Layout / styling** — snapshot tests; they catch CSS regressions a state assertion won't.
- **Messages** — assert side effects of posting (a handler ran, a reactive changed) rather than poking internals.
