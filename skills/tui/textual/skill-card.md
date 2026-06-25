---
name: textual
version: 0.1.0
summary: Build and debug Python TUIs with Textual 8.x — App/Screen/Widget, reactive attributes, TCSS layout, @work workers, Pilot tests, and textual serve.
owner: '@vinsonconsulting'
repo:
  tier: public
  url: https://github.com/vinsonconsulting/claude-skill-foundry
license: Apache-2.0
source_commit: 5e49df814225e1d33d63b52f49780175fd0a4ef2
content_hash: sha256:a884ccbefc0a99dce11184e9e145e251d004245a8db4d244687a1ed7dcdbffd0
description: 'Use this skill when building or debugging a Python terminal UI (TUI) with Textual (Textualize''s framework) — `App`/`Screen`/`Widget`, `compose()`, `reactive`/`watch_`, `@work` workers, Textual CSS / TCSS (`dock`, `grid`, `fr` units), widgets like `RichLog`, `Markdown`, `DataTable`, `Input`, `TextArea`, `Tree`, `ListView`; testing with `Pilot` / `pytest-textual-snapshot`; `textual serve` / Textual Web deploy; Rich renderables inside Textual; or streaming LLM/agent tokens into a terminal and agentic-CLI front-ends. Triggers: Textual, Textualize, TUI, terminal UI, `@work`, TCSS, `RichLog`, `query_one`, Pilot, `textual serve`. Writes current 8.x code, not stale pre-1.0 patterns. Not for: Rust TUIs (→ Ratatui sibling), Go TUIs (→ Bubble Tea sibling), plain non-interactive CLI output (Click/argparse/Typer) with no live UI, or agent-session orchestration / tmux multiplexing. Note: browser deploy via `textual serve` (the same Textual app served to a browser) IS in scope — a general React/HTML web-app request is not.'
triggers:
  positive:
  - build a Textual app with a DataTable and a Footer
  - my reactive attribute isn't updating the widget — fix the watch_ method
  - lay out two panels side by side with TCSS dock/grid
  - push a modal Screen and return a value when it dismisses
  - run a long task in a @work worker without blocking the Textual UI
  - stream agent tokens into a RichLog in my Textual app
  - write a Pilot test / pytest-textual-snapshot for my Textual app
  - deploy my Textual app to the browser with textual serve
  - why does textual run show a blank screen
  - style widgets with TCSS using fr units and dock
  - embed a Rich renderable inside a Textual widget
  - build a Tree or ListView navigation pane in Textual
  negative:
  - prompt: build a Rust terminal UI
    use_instead: ratatui
  - prompt: build a Go TUI with Bubble Tea
    use_instead: bubbletea
  - prompt: convert an image to ASCII art
    use_instead: image-to-ascii
  - prompt: render an image as terminal color blocks
    use_instead: textmode-js
  - prompt: make an ASCII-art React component
    use_instead: ascii-img-react
  - prompt: parse CLI flags with argparse/Click, no live UI
    use_instead: plain CLI output (no TUI skill)
  - prompt: print a one-shot colored table with Rich, no app loop
    use_instead: rich-only output (out of scope)
  - prompt: build a general React/HTML web app
    use_instead: web UI (out of scope)
  - prompt: draw directly with curses windows
    use_instead: curses (out of scope)
  - prompt: orchestrate tmux or agent sessions
    use_instead: session orchestration (out of scope)
output:
  type: Code
  format: Markdown with Python + TCSS code blocks
dependencies:
- textual>=8.2,<9
- rich>=15.0
- python>=3.9
external_endpoints: none
permissions:
  network: false
  shell: true
  file: true
  env: false
  mcp: false
metrics: null
scan:
  tool: skillspector@a5092dd9b9521ff57a9b53612bb129ce78019002
  score: 0
  severity: LOW
  date: '2026-06-20'
  findings: []
  sarif: ./report.sarif
status: beta
card_version: '1.0'
updated: '2026-06-20'
---

# textual <small>v0.1.0</small>

Build and debug Python TUIs with Textual 8.x — App/Screen/Widget, reactive attributes, TCSS layout, @work workers, Pilot tests, and textual serve.

**Status:** beta | **License:** Apache-2.0 | **Scan:** LOW (0/100)

## When to use it

Use this skill when building or debugging a Python terminal UI (TUI) with Textual (Textualize's framework) — `App`/`Screen`/`Widget`, `compose()`, `reactive`/`watch_`, `@work` workers, Textual CSS / TCSS (`dock`, `grid`, `fr` units), widgets like `RichLog`, `Markdown`, `DataTable`, `Input`, `TextArea`, `Tree`, `ListView`; testing with `Pilot` / `pytest-textual-snapshot`; `textual serve` / Textual Web deploy; Rich renderables inside Textual; or streaming LLM/agent tokens into a terminal and agentic-CLI front-ends. Triggers: Textual, Textualize, TUI, terminal UI, `@work`, TCSS, `RichLog`, `query_one`, Pilot, `textual serve`. Writes current 8.x code, not stale pre-1.0 patterns. Not for: Rust TUIs (→ Ratatui sibling), Go TUIs (→ Bubble Tea sibling), plain non-interactive CLI output (Click/argparse/Typer) with no live UI, or agent-session orchestration / tmux multiplexing. Note: browser deploy via `textual serve` (the same Textual app served to a browser) IS in scope — a general React/HTML web-app request is not.


## Security

SkillSpector scan `skillspector@a5092dd9b9521ff57a9b53612bb129ce78019002` scored 0/100 (LOW band).

No findings.

The SARIF report lives at `./report.sarif`.
