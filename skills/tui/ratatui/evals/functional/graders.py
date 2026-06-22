"""Deterministic graders for the ratatui functional evals.

Stdlib-only (regex over the generated Rust source), so it runs under any
python3. Each grader takes the generated main.rs text plus a task config and
returns a list of assertion dicts shaped {text, passed, evidence} — the shape the
eval aggregator expects.

The assertions reward correct, current Ratatui 0.30 code: the right API for the
task, and the ABSENCE of the stale tui-rs / pre-0.26 patterns the skill exists to
refuse. They never require padding or a construct the skill should not emit, and
they accept valid variants (e.g. `.areas()` OR `.split()`) so a correct program
is not failed for choosing a legal alternative. Comments are stripped before the
stale scan, so a comment that names a forbidden API (e.g. "init handles raw mode,
no enable_raw_mode") is not miscounted as using it.
"""
from __future__ import annotations
import re

# Stale tui-rs / pre-0.26 tokens the skill must never emit (SKILL.md reject
# table). `Alignment` is deliberately absent — it is a kept 0.30 alias, so
# flagging it would penalize correct code (the rust-register grader lesson).
STALE = [
    (r"\benable_raw_mode\b", "enable_raw_mode (init/run handles it)"),
    (r"\bEnterAlternateScreen\b", "EnterAlternateScreen (init/run handles it)"),
    (r"Constraint::Proportional|\bProportional\s*\(", "Proportional (use Fill)"),
    (r"\bStretchLast\b|\bSegmentSize\b", "StretchLast/SegmentSize (removed)"),
    (r"\bcassowary\b", "cassowary (kasuari is the first-party solver)"),
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
    return _a("no stale tui-rs / pre-0.26 patterns", not hits,
              "clean" if not hits else f"found: {hits}")


def grade_constrained_layout(code, cfg):
    return [
        pos(code, "uses Layout::vertical / Layout::horizontal", r"Layout::(vertical|horizontal)"),
        pos(code, "destructures regions via .areas() or .split()", r"\.areas\b|\.split\s*\("),
        pos(code, "uses Constraint::Fill for the filling regions", r"Fill\s*\("),
        pos(code, "uses Constraint::Length for the fixed header/sidebar/status", r"Length\s*\("),
        pos(code, "renders inside terminal.draw / a Frame", r"\.draw\s*\(|frame\.|Frame"),
        _no_stale(code),
    ]


def grade_stateful_scrollable_list(code, cfg):
    return [
        pos(code, "owns a ListState", r"\bListState\b"),
        pos(code, "renders via render_stateful_widget", r"render_stateful_widget"),
        pos(code, "moves selection (select_next/select_previous/select)",
            r"select_next|select_previous|\.select\s*\("),
        pos(code, "drives a ScrollbarState", r"\bScrollbarState\b"),
        pos(code, "filters key repeats with KeyEventKind::Press", r"KeyEventKind::Press"),
        _no_stale(code),
    ]


def grade_scrollback_model(code, cfg):
    return [
        pos(code, "owns a VecDeque<Line> / Vec<Line> scrollback", r"VecDeque\s*<\s*Line|Vec\s*<\s*Line"),
        pos(code, "tracks a scroll offset", r"offset"),
        pos(code, "renders a windowed slice (skip/take/range over offset)",
            r"\.skip\s*\(|\.take\s*\(|\[\s*\w*offset"),
        pos(code, "drives a ScrollbarState from offset+len", r"\bScrollbarState\b"),
        neg(code, "stays synchronous (no async / await / tokio)", r"\basync\b|\.await\b|\btokio\b"),
        _no_stale(code),
    ]


def grade_streaming_viewport(code, cfg):
    return [
        pos(code, "uses a tokio mpsc channel", r"mpsc"),
        pos(code, "multiplexes with tokio::select!", r"select\s*!|tokio::select"),
        pos(code, "has a render tick (interval/tick), not redraw-per-delta", r"interval|tick"),
        pos(code, "redraws via terminal.draw", r"\.draw\s*\("),
        pos(code, "models events as an enum", r"enum\s+\w+"),
        _no_stale(code),
    ]


def grade_custom_stateful_widget(code, cfg):
    return [
        pos(code, "implements Widget for a reference (&T) or StatefulWidget",
            r"impl\s+(?:\w+::)*Widget\s+for\s+&|impl\s+(?:\w+::)*StatefulWidget\s+for"),
        pos(code, "correct render signature (Rect + Buffer)", r"fn\s+render\b[\s\S]{0,160}?Buffer"),
        pos(code, "writes cells via Line/Span/Buffer methods",
            r"Line::|Span::|\.set_string\s*\(|buf\.|Buffer"),
        neg(code, "no raw ANSI escape codes", r"\\x1b|\\u\{1b\}|\\033|\\e\["),
        _no_stale(code),
    ]


def grade_text_wrapping_unicode(code, cfg):
    return [
        pos(code, "measures display width via unicode-width (.width())",
            r"unicode_width|UnicodeWidth|\.width\s*\(\s*\)"),
        pos(code, "wraps with Paragraph + Wrap", r"Paragraph|Wrap\b"),
        neg(code, "does not size text by char count", r"\.chars\s*\(\s*\)\s*\.\s*count"),
        pos(code, "truncates on grapheme boundaries (unicode-segmentation)",
            r"unicode_segmentation|graphemes\s*\("),
        _no_stale(code),
    ]


def grade_lifecycle_hygiene(code, cfg):
    return [
        pos(code, "uses ratatui::init()/restore() or ratatui::run()",
            r"ratatui::init|ratatui::run|::init\s*\(\s*\)|::restore\s*\(\s*\)"),
        pos(code, "installs color_eyre", r"color_eyre"),
        pos(code, "restores the terminal on teardown", r"restore\s*\(\s*\)|ratatui::run"),
        _a("does not hand-roll raw mode / alternate screen",
           not re.search(r"enable_raw_mode|EnterAlternateScreen", _strip_comments(code)),
           "absent" if not re.search(r"enable_raw_mode|EnterAlternateScreen", _strip_comments(code)) else "hand-rolled setup found"),
        _no_stale(code),
    ]


GRADERS = {
    "constrained-layout": grade_constrained_layout,
    "stateful-scrollable-list": grade_stateful_scrollable_list,
    "scrollback-model": grade_scrollback_model,
    "streaming-viewport": grade_streaming_viewport,
    "custom-stateful-widget": grade_custom_stateful_widget,
    "text-wrapping-unicode": grade_text_wrapping_unicode,
    "lifecycle-hygiene": grade_lifecycle_hygiene,
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
