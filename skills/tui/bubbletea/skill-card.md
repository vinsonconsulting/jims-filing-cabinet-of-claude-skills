---
name: bubbletea
version: 0.1.0
summary: Build current Bubble Tea v2 terminal UIs in Go on the charm.land import paths — the Elm/MVU pattern, Lip Gloss, Bubbles, Glamour, streaming, and teatest.
owner: '@vinsonconsulting'
repo:
  tier: public
  url: https://github.com/vinsonconsulting/jims-filing-cabinet-of-claude-skills
license: MIT
source_commit: 5136c9459165e3e4e62f0daad31045ba86bfd0dc
content_hash: sha256:40a8ee72bb795a02d97a49e4ca3d6dd7d585b83c1d873a3718d69a7e88efeb24
description: 'Use this skill when building a terminal UI (TUI) in Go with Bubble Tea and the Charm stack — the Elm Architecture / MVU pattern (`tea.Model` with `Init`/`Update`/`View`), `Cmd`/`Msg` event flow, Lip Gloss styling and layout, Bubbles components (`viewport`, `list`, `table`, `textinput`, `textarea`, `spinner`, `progress`), Glamour markdown rendering, and teatest for testing. Especially apt for streaming tokens from an LLM/agent into a terminal (goroutine → `p.Send` → `Update` → `viewport`), an agentic CLI, or any interactive full-screen or inline terminal app in Go. Targets v2 on the `charm.land/*/v2` import paths (Go 1.25+); writes current-version-correct code and avoids v1/beta patterns. Not for: Rust TUIs (→ Ratatui sibling), Python TUIs (→ Textual sibling), plain non-interactive CLI output (use `fmt`/`cobra`/standalone `lipgloss`), web/GUI UIs, or agent session orchestration / tmux / process multiplexing.'
triggers:
  positive:
  - build a Bubble Tea TUI in Go with a viewport and a list
  - wire up the Elm Architecture Init/Update/View for my Bubble Tea model
  - stream LLM tokens from a goroutine into a Bubble Tea viewport
  - style a layout with Lip Gloss v2 and compose blocks side by side
  - my Bubble Tea Cmd/Msg isn't updating the model — debug the event flow
  - add a spinner and a progress bar from Bubbles to my Go TUI
  - render markdown in the terminal with Glamour inside Bubble Tea
  - write a teatest test for my Bubble Tea program
  - migrate my Bubble Tea v1 code to the charm.land v2 import paths
  - build an interactive full-screen Go CLI with a text input and a table
  - handle WindowSizeMsg resize and recompute my Lip Gloss layout
  - measure display width correctly for CJK/emoji in my Bubble Tea view
  negative:
  - prompt: build a Rust terminal UI
    use_instead: ratatui
  - prompt: build a Python TUI with Textual
    use_instead: textual
  - prompt: convert an image to ASCII art
    use_instead: image-to-ascii
  - prompt: render an image as terminal color blocks
    use_instead: textmode-js
  - prompt: make an ASCII-art React component
    use_instead: ascii-img-react
  - prompt: colorize a one-shot CLI message with fmt/cobra, no live UI
    use_instead: plain CLI output (no TUI skill)
  - prompt: standalone lipgloss styling with no program loop
    use_instead: plain CLI output (no TUI skill)
  - prompt: build a browser or GUI app
    use_instead: web/GUI UI (out of scope)
  - prompt: multiplex processes or orchestrate tmux
    use_instead: session orchestration (out of scope)
  - prompt: write release notes for my Go library
    use_instead: changelog (out of scope)
output:
  type: Code
  format: Markdown with Go code blocks
dependencies:
- charm.land/bubbletea/v2>=2.0,<3
- charm.land/lipgloss/v2
- charm.land/bubbles/v2
- go>=1.25
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
  score: 13
  severity: LOW
  date: '2026-06-22'
  findings:
  - rule_id: LP3
    severity: MEDIUM
    status: resolved
    owasp: null
    atlas: null
    note: null
  sarif: ./report.sarif
status: beta
card_version: '1.0'
updated: '2026-06-22'
---

# bubbletea <small>v0.1.0</small>

Build current Bubble Tea v2 terminal UIs in Go on the charm.land import paths — the Elm/MVU pattern, Lip Gloss, Bubbles, Glamour, streaming, and teatest.

**Status:** beta | **License:** MIT | **Scan:** LOW (13/100)

## When to use it

Use this skill when building a terminal UI (TUI) in Go with Bubble Tea and the Charm stack — the Elm Architecture / MVU pattern (`tea.Model` with `Init`/`Update`/`View`), `Cmd`/`Msg` event flow, Lip Gloss styling and layout, Bubbles components (`viewport`, `list`, `table`, `textinput`, `textarea`, `spinner`, `progress`), Glamour markdown rendering, and teatest for testing. Especially apt for streaming tokens from an LLM/agent into a terminal (goroutine → `p.Send` → `Update` → `viewport`), an agentic CLI, or any interactive full-screen or inline terminal app in Go. Targets v2 on the `charm.land/*/v2` import paths (Go 1.25+); writes current-version-correct code and avoids v1/beta patterns. Not for: Rust TUIs (→ Ratatui sibling), Python TUIs (→ Textual sibling), plain non-interactive CLI output (use `fmt`/`cobra`/standalone `lipgloss`), web/GUI UIs, or agent session orchestration / tmux / process multiplexing.


## Security

SkillSpector scan `skillspector@a5092dd9b9521ff57a9b53612bb129ce78019002` scored 13/100 (LOW band).

Findings:

- `LP3` (MEDIUM, resolved)

The SARIF report lives at `./report.sarif`.
