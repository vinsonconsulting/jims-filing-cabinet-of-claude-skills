"""Deterministic graders for the bubbletea functional evals.

Stdlib-only (regex over the generated Go source), so it runs under any python3.
Each grader takes the generated main.go text plus a task config and returns a list
of assertion dicts shaped {text, passed, evidence} — the shape the eval aggregator
expects.

The assertions reward correct, current Bubble Tea v2 code (the charm.land/*/v2
stack and the v2 signatures) and the ABSENCE of the v1 / github.com-beta patterns
the skill exists to refuse. They accept valid variants so a correct program is not
failed for a legal choice, and they never require padding. Comments are stripped
before the stale scan, so a comment that names a forbidden API is not miscounted as
using it.
"""
from __future__ import annotations
import re

# v1 / github.com-beta tokens the skill must never emit (SKILL.md reject table).
# The x/* helpers (github.com/charmbracelet/x/ansi) are KEPT in v2, so the path
# patterns below match only bubbletea/lipgloss/bubbles, never .../x/.
STALE = [
    (r"github\.com/charmbracelet/bubbletea", "v1/beta bubbletea path (use charm.land/bubbletea/v2)"),
    (r"github\.com/charmbracelet/lipgloss", "v1 lipgloss path (use charm.land/lipgloss/v2)"),
    (r"github\.com/charmbracelet/bubbles\b", "v1 bubbles path (use charm.land/bubbles/v2)"),
    (r"tea\.WithAltScreen|WithMouseCellMotion", "v1 NewProgram option (set AltScreen/MouseMode on tea.View)"),
    (r"func\s*\([^)]*\)\s*View\s*\(\s*\)\s*string", "View() string (v2 returns tea.View)"),
    (r"msg\.Runes\b|msg\.Type\b", "v1 KeyMsg .Type/.Runes (use KeyPressMsg + msg.String())"),
]


def _a(text, passed, evidence):
    return {"text": text, "passed": bool(passed), "evidence": evidence}


def _strip_comments(code):
    """Drop // line and /* */ block comments so the stale scan sees code only."""
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//[^\n]*", "", code)
    return code


def pos(code, text, pattern, flags=0):
    """A positive assertion: the pattern SHOULD be present."""
    m = re.search(pattern, code, flags)
    return _a(text, bool(m), m.group(0)[:60] if m else "not found")


def neg(code, text, pattern, flags=0):
    """A negative assertion: the pattern should be ABSENT."""
    m = re.search(pattern, code, flags)
    return _a(text, not m, ("found: " + m.group(0)[:60]) if m else "absent")


def _no_stale(code):
    stripped = _strip_comments(code)
    hits = [label for pat, label in STALE if re.search(pat, stripped)]
    return _a("no v1 / github.com-beta patterns", not hits,
              "clean" if not hits else f"found: {hits}")


def _v2_imports(code):
    return pos(code, "imports the charm.land/*/v2 stack", r"charm\.land/(bubbletea|lipgloss|bubbles|glamour)/v2")


def grade_constrained_layout(code, cfg):
    return [
        pos(code, "imports Lip Gloss v2", r"charm\.land/lipgloss/v2"),
        pos(code, "composes blocks with JoinHorizontal/JoinVertical/Place",
            r"JoinHorizontal|JoinVertical|lipgloss\.Place"),
        pos(code, "sizes from tea.WindowSizeMsg", r"WindowSizeMsg"),
        pos(code, "measures width with lipgloss.Width / lipgloss.Size", r"lipgloss\.(Width|Size)\b"),
        pos(code, "View returns a tea.View", r"tea\.NewView|\)\s*tea\.View\b"),
        _no_stale(code),
    ]


def grade_stateful_list(code, cfg):
    return [
        pos(code, "uses the Bubbles list component", r"charm\.land/bubbles/v2/list|list\.Model"),
        pos(code, "routes into the child and reassigns the returned model",
            r"=\s*[\w.]+\.Update\s*\("),
        pos(code, "keeps the v2 Update signature", r"Update\s*\([^)]*tea\.Msg\s*\)\s*\(\s*tea\.Model\s*,\s*tea\.Cmd\s*\)"),
        pos(code, "forwards WindowSizeMsg sizing to the child", r"WindowSizeMsg"),
        pos(code, "View returns a tea.View", r"tea\.NewView|\)\s*tea\.View\b"),
        _no_stale(code),
    ]


def grade_scrollback_viewport(code, cfg):
    return [
        pos(code, "uses the viewport Bubble", r"charm\.land/bubbles/v2/viewport|viewport\.Model"),
        pos(code, "builds the viewport with functional options",
            r"viewport\.New\s*\(\s*viewport\.With"),
        pos(code, "sets content via SetContent", r"SetContent\s*\("),
        pos(code, "auto-follows via AtBottom/GotoBottom", r"AtBottom\s*\(\s*\)"),
        neg(code, "no positional viewport.New(w, h) (v1)", r"viewport\.New\s*\(\s*[A-Za-z0-9_]+\s*,"),
        _no_stale(code),
    ]


def grade_streaming_llm(code, cfg):
    return [
        pos(code, "pushes deltas with p.Send", r"\.Send\s*\("),
        pos(code, "runs a producer goroutine", r"go\s+func"),
        pos(code, "feeds a custom Msg back into Update", r"case\s+\w+\s*:|case\s+\w+Msg\b|\btea\.Msg\b"),
        pos(code, "appends into a viewport with follow", r"SetContent\s*\(|AtBottom\s*\(\s*\)"),
        neg(code, "goroutine does not call Update directly", r"go\s+func[\s\S]{0,240}?\.Update\s*\("),
        _no_stale(code),
    ]


def grade_mvu_event_flow(code, cfg):
    return [
        pos(code, "Init returns tea.Cmd", r"Init\s*\(\s*\)\s*tea\.Cmd"),
        pos(code, "v2 Update signature returns (tea.Model, tea.Cmd)",
            r"Update\s*\([^)]*tea\.Msg\s*\)\s*\(\s*tea\.Model\s*,\s*tea\.Cmd\s*\)"),
        pos(code, "handles tea.KeyPressMsg and matches msg.String()",
            r"KeyPressMsg[\s\S]{0,200}?\.String\s*\(\s*\)|\.String\s*\(\s*\)[\s\S]{0,200}?KeyPressMsg"),
        pos(code, "returns tea.Quit as a Cmd", r"tea\.Quit\b"),
        pos(code, "drives a periodic tick with tea.Tick/tea.Every", r"tea\.(Tick|Every)\b"),
        _no_stale(code),
    ]


def grade_text_width_unicode(code, cfg):
    return [
        pos(code, "measures display width via lipgloss.Width / ansi.StringWidth",
            r"lipgloss\.Width\b|ansi\.StringWidth\b"),
        pos(code, "truncates/wraps with x/ansi", r"ansi\.(Truncate|Wrap|Cut)\b"),
        pos(code, "imports the kept x/ansi helper", r"github\.com/charmbracelet/x/ansi"),
        neg(code, "does not compute width from len(...)", r"Width\s*\(\s*len\s*\(|len\s*\([^)]*\)\s*[<>]=?\s*\w*[Ww]idth"),
        _no_stale(code),
    ]


def grade_lifecycle(code, cfg):
    stripped = _strip_comments(code)
    handrolled = re.search(r"MakeRaw|enableRawMode|term\.SetRaw", stripped)
    return [
        pos(code, "builds the program with tea.NewProgram", r"tea\.NewProgram\s*\("),
        pos(code, "runs it and checks the error from p.Run()", r"\.Run\s*\(\s*\)"),
        pos(code, "enables alt-screen on the tea.View (not a NewProgram option)",
            r"\.AltScreen\s*=\s*true"),
        pos(code, "View returns a tea.View", r"tea\.NewView|\)\s*tea\.View\b"),
        _a("does not hand-roll raw mode / teardown", not handrolled,
           "absent" if not handrolled else f"found: {handrolled.group(0)}"),
        _no_stale(code),
    ]


GRADERS = {
    "constrained-layout": grade_constrained_layout,
    "stateful-list": grade_stateful_list,
    "scrollback-viewport": grade_scrollback_viewport,
    "streaming-llm": grade_streaming_llm,
    "mvu-event-flow": grade_mvu_event_flow,
    "text-width-unicode": grade_text_width_unicode,
    "lifecycle": grade_lifecycle,
}


def grade(task_id: str, code_text: str, cfg: dict | None = None) -> dict:
    cfg = cfg or {}
    expectations = GRADERS[task_id](code_text, cfg)
    passed = sum(1 for e in expectations if e["passed"])
    total = len(expectations)
    return {
        "expectations": expectations,
        "summary": {"passed": passed, "total": total,
                    "pass_rate": round(passed / total, 4) if total else 0.0},
    }
