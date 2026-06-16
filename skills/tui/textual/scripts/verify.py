#!/usr/bin/env python3
"""Re-verify the Textual skill against your *installed* Textual.

This skill is pinned to a specific Textual version and its examples are run-verified.
Textual ships ~weekly, so after upgrading, run this to confirm the skill's load-bearing
APIs and reject-list still hold. It executes the same snippets the SKILL.md teaches —
imports plus real apps driven through Pilot — and asserts the deprecation map.

    python3 -m venv .venv && .venv/bin/pip install textual rich
    .venv/bin/python skills/tui/textual/scripts/verify.py

Exit code 0 = all good. Non-zero = a check drifted; read the FAIL lines, then update
SKILL.md / references/versioning.md accordingly. No secrets, no network, standalone.
"""
from __future__ import annotations
import asyncio
import inspect
import sys
import warnings
from importlib.metadata import version

RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))


# ---------------------------------------------------------------------------
# Introspection: the reject-list / deprecation map
# ---------------------------------------------------------------------------
def introspect() -> None:
    print(f"textual {version('textual')} | rich {version('rich')} | python {sys.version.split()[0]}")
    print("-" * 70)

    # TextLog removed -> RichLog
    try:
        from textual.widgets import TextLog  # noqa: F401
        record("TextLog removed (expect ImportError)", False, "TextLog still imports!")
    except ImportError:
        record("TextLog removed (-> RichLog)", True)

    from textual.widgets import RichLog, Static, Label, Select, Switch, Markdown  # noqa: F401

    # Static/.content (not .renderable)
    s = Static("x")
    record("Static exposes .content not .renderable",
           hasattr(s, "content") and not hasattr(s, "renderable"))

    # Select.NULL is the sentinel; BLANK is the bool False
    record("Select.NULL is the no-selection sentinel; BLANK is not",
           hasattr(Select, "NULL") and Select.BLANK is False,
           f"BLANK={Select.BLANK!r}")

    # Switch binding action
    record("Switch.action_toggle_switch exists (the bound action)",
           hasattr(Switch, "action_toggle_switch"))

    # reactive helpers
    from textual.widget import Widget
    record("Widget.mutate_reactive + set_reactive exist",
           hasattr(Widget, "mutate_reactive") and hasattr(Widget, "set_reactive"))
    from textual.reactive import reactive, var, Reactive  # noqa: F401
    record("reactive/var subclass Reactive", issubclass(reactive, Reactive) and issubclass(var, Reactive))

    # Markdown.get_stream is a classmethod
    gs = inspect.getattr_static(Markdown, "get_stream")
    record("Markdown.get_stream is a classmethod", isinstance(gs, classmethod))

    # events.Load still exists (do NOT assert removed)
    try:
        from textual.events import Load  # noqa: F401
        record("events.Load still exists (do not over-reject)", True)
    except ImportError:
        record("events.Load still exists (do not over-reject)", False, "Load is gone — update docs")

    # bare @work on a sync fn raises
    from textual import work
    try:
        work(lambda self: 1)
        record("bare @work on sync fn raises WorkerDeclarationError", False, "no error raised")
    except Exception as e:
        record("bare @work on sync fn raises WorkerDeclarationError",
               type(e).__name__ == "WorkerDeclarationError", type(e).__name__)

    # Python floor
    try:
        from importlib.metadata import metadata
        rp = metadata("textual").get("Requires-Python", "")
        record("Python floor advertised", ">=3.9" in rp, rp)
    except Exception as e:  # pragma: no cover
        record("Python floor advertised", False, str(e))


# ---------------------------------------------------------------------------
# Pilot: the runtime patterns the skill teaches
# ---------------------------------------------------------------------------
async def pilot_checks() -> None:
    from textual import on, work
    from textual.app import App, ComposeResult
    from textual.widget import Widget
    from textual.reactive import reactive
    from textual.message import Message
    from textual.containers import Horizontal, VerticalScroll
    from textual.widgets import Button, Label, Static, Markdown, RichLog

    # --- skeleton + reactive footgun ---
    events: list = []

    class Demo(App):
        BINDINGS = [("a", "add", "Add")]
        items = reactive(list)
        n = reactive(0)

        def compose(self) -> ComposeResult:
            yield Label("count: 0", id="lbl")

        def on_mount(self) -> None:
            self.count = 0

        def action_add(self) -> None:
            self.count += 1
            self.query_one("#lbl", Label).update(f"count: {self.count}")

        def validate_n(self, value: int) -> int:
            return max(0, value)

        def watch_items(self, old, new) -> None:
            events.append(list(new))

    app = Demo()
    async with app.run_test() as pilot:
        await pilot.press("a", "a", "a")
        await pilot.pause()
        record("skeleton: compose+BINDINGS+action+query_one",
               "count: 3" in str(app.query_one("#lbl", Label).render()))
        events.clear()                       # discard the init=True mount firing
        app.items = ["a"]; await pilot.pause()
        reassign = events == [["a"]]
        events.clear(); app.items.append("b"); await pilot.pause()
        silent = events == []
        app.mutate_reactive(Demo.items); await pilot.pause()
        fired = events != []
        record("reactive: reassign fires, in-place is silent, mutate_reactive fires",
               reassign and silent and fired)
        app.n = -5; await pilot.pause()
        record("reactive: validate_ clamps", app.n == 0)

    # --- @on + custom Message bubbling ---
    got = {}

    class Child(Widget):
        class Fired(Message):
            def __init__(self, v: int) -> None:
                self.v = v; super().__init__()
        def compose(self) -> ComposeResult:
            yield Button("go", id="go")
        @on(Button.Pressed, "#go")
        def _go(self) -> None:
            self.post_message(self.Fired(42))

    class Parent(App):
        def compose(self) -> ComposeResult:
            yield Child()
        @on(Child.Fired)
        def _caught(self, m: Child.Fired) -> None:
            got["v"] = m.v

    app = Parent()
    async with app.run_test() as pilot:
        await pilot.click("#go"); await pilot.pause()
        record("messages: @on + custom Message bubbles to parent", got.get("v") == 42)

    # --- TCSS dock + fr ---
    class Lay(App):
        CSS = "#top{dock:top;height:1;} #side{width:20;} #main{width:1fr;}"
        def compose(self) -> ComposeResult:
            yield Static("t", id="top")
            with Horizontal():
                yield Static("s", id="side")
                yield Static("m", id="main")

    app = Lay()
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        side = app.query_one("#side").region.width
        main = app.query_one("#main").region.width
        record("layout: dock top + 20-cell sidebar + 1fr main",
               side == 20 and main == 60, f"side={side} main={main}")

    # --- custom widget render()/compose() ---
    class Pct(Widget):
        pct = reactive(0)
        def render(self) -> str:
            return f"{self.pct}%"

    class Card(Widget):
        def compose(self) -> ComposeResult:
            yield Label("title"); yield Pct()

    class CW(App):
        def compose(self) -> ComposeResult:
            yield Card()

    app = CW()
    async with app.run_test() as pilot:
        await pilot.pause()
        p = app.query_one(Pct); p.pct = 55; await pilot.pause()
        record("custom widget: render() leaf + compose() compound", str(p.render()) == "55%")

    # --- HERO streaming, warning-free ---
    CHUNKS = ["# Title\n\n", "streaming ", "tokens."]
    state = {}

    class Chat(App):
        def compose(self) -> ComposeResult:
            with VerticalScroll():
                yield Markdown()
        def on_mount(self) -> None:
            self._i = 0; self.go()
        async def _chunk(self):
            if self._i < len(CHUNKS):
                c = CHUNKS[self._i]; self._i += 1
                await asyncio.sleep(0.001); return c
            return None
        @work
        async def go(self) -> None:
            md = self.query_one(Markdown)
            self.query_one(VerticalScroll).anchor()
            stream = Markdown.get_stream(md)
            try:
                while (c := await self._chunk()) is not None:
                    await stream.write(c)
            finally:
                await stream.stop()
            state["src"] = md.source

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        app = Chat()
        async with app.run_test(size=(40, 10)) as pilot:
            for _ in range(20):
                await asyncio.sleep(0.01); await pilot.pause()
                if "src" in state:
                    break
        leak = [w for w in caught if "never awaited" in str(w.message)]
        record("HERO streaming: get_stream + await write/stop + anchor (warning-free)",
               "Title" in state.get("src", "") and "tokens" in state.get("src", "") and not leak,
               f"warns={[str(w.message) for w in leak]}")

    # --- RichLog + thread worker + exclusive ---
    class R(App):
        def compose(self) -> ComposeResult:
            yield RichLog(highlight=True, markup=True, auto_scroll=True, id="log")
    app = R()
    async with app.run_test(size=(40, 6)) as pilot:
        await pilot.pause()
        log = app.query_one("#log", RichLog)
        for i in range(20):
            log.write(f"[bold]line {i}[/]")
        await pilot.pause()
        record("RichLog: write() + markup + auto_scroll", len(log.lines) >= 1)

    import time
    done = {}

    class T(App):
        def compose(self) -> ComposeResult:
            yield Label("idle", id="s")
        def on_mount(self) -> None:
            self.job()
        @work(thread=True)
        def job(self) -> None:
            time.sleep(0.02)
            self.call_from_thread(self.query_one("#s", Label).update, "done")
            done["ok"] = True
    app = T()
    async with app.run_test() as pilot:
        await asyncio.sleep(0.1); await pilot.pause()
        record("thread worker: @work(thread=True) + call_from_thread", done.get("ok") is True)


async def main() -> int:
    introspect()
    print("-" * 70)
    await pilot_checks()
    print("=" * 70)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print(f"{passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
