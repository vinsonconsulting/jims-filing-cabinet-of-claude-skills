# Agent / LLM streaming UI (in-process)

How to stream model output into a Textual app. **Scope: the in-process UI only** — feeding
tokens from an async client into widgets without blocking the loop. Spawning/multiplexing
agent *sessions* (tmux, subprocess fan-out, transcript routing) is a different concern and
belongs in the orchestration skill, not here. Verified against **8.2.7**.

## The hero pattern: streaming Markdown

Run the stream in a `@work` async worker. Use `Markdown.get_stream()` — it coalesces bursts of
appends (it can't repaint faster than ~20/s) into single updates and re-renders only the last
block, which is far cheaper and flicker-free compared to remove-and-remount-per-token. Pin to
the bottom with `container.anchor()`.

```python
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Markdown
from textual.containers import VerticalScroll

class Chat(App):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Markdown()

    def on_mount(self) -> None:
        self.stream_reply()

    @work                                              # async worker; the loop stays responsive
    async def stream_reply(self) -> None:
        markdown_widget = self.query_one(Markdown)
        self.query_one(VerticalScroll).anchor()        # stick to bottom as content grows
        stream = Markdown.get_stream(markdown_widget)  # CLASSMETHOD — pass the widget instance
        try:
            async for chunk in llm_client.stream(prompt):
                await stream.write(chunk)              # await: write() is async
        finally:
            await stream.stop()                        # await: stop() is async; always run it
```

Critical, run-verified details (the dossier had these wrong):

- `Markdown.get_stream(widget)` is a **classmethod**; `widget.get_stream()` does **not** work.
- `stream.write(chunk)` and `stream.stop()` are **both awaitable**. A bare `stream.stop()`
  leaks a pending task and warns. Wrap the loop in `try/finally` so `stop()` always runs.
- `get_stream()` auto-starts the updater (no `start()` call needed).
- `container.anchor()` on the scrolling parent keeps the view pinned to the bottom.

## Cancel the previous turn

When the user sends a new message mid-stream, cancel the in-flight worker. Use an exclusive
group so a new run supersedes the old one automatically:

```python
@work(exclusive=True, group="llm")     # starting a new one cancels the running one
async def stream_reply(self) -> None:
    ...
```

`exclusive=True` cancels any running worker in the same `group` before this one starts.
Workers also auto-cancel when their widget is removed or the app exits, so teardown is clean.

## RichLog alternative (colored log lines, not Markdown)

For token/event logs rather than rendered Markdown, a `RichLog` is simpler:

```python
log = RichLog(highlight=True, markup=True, auto_scroll=True, wrap=True)
# in the worker:
log.write(f"[dim]{token}[/]")          # auto_scroll keeps the newest line visible
```

`auto_scroll=True` follows the bottom. If you want "stick to bottom **unless** the user has
scrolled up", put the content in a `VerticalScroll` and call `.anchor()` — Textual releases the
anchor when the user scrolls away and re-pins at the bottom.

## Thread-worker variant (blocking SDKs)

If the client is synchronous/blocking, use a thread worker and marshal every UI update:

```python
@work(thread=True)
def stream_reply(self) -> None:
    log = self.query_one(RichLog)
    for chunk in blocking_client.stream(prompt):
        self.call_from_thread(log.write, chunk)    # RichLog.write is sync; never touch widgets from the thread directly
```

## Reference apps (read, don't vendor)

- **Toad** (`batrachianai/toad`, McGugan) — the streaming-Markdown + anchor-to-bottom
  architecture this pattern mirrors. **AGPL — cite it, don't copy code in.** (PyPI `batrachian-toad`.)
- **Elia** (`darrenburns/elia`) — an LLM chat TUI; useful for *structure*, but it pins an older
  Textual (pre-2.0), so don't copy its API calls.
- **Posting** (`darrenburns/posting`) — a large app that tracks current Textual; good for
  large-app structure and worker usage.
