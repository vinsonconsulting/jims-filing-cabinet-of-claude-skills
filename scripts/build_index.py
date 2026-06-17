#!/usr/bin/env python3
"""Generate the skills index and inject it into README.md.

Walks skills/ for SKILL.md files, reads `name` and `description` from the
frontmatter, and writes a Markdown table grouped by top-level category between
the SKILLS-INDEX markers in README.md. If the README also carries SKILLS-COUNT
markers, the skills-count badge between them is kept in sync too, so the count
can't go stale silently: `--check` (and therefore CI) fails when it drifts.

Usage:
  python3 scripts/build_index.py            # write the index into README.md
  python3 scripts/build_index.py --check    # exit 1 if README.md is out of date
"""
from __future__ import annotations
import sys
from pathlib import Path

from skilltools import parse_frontmatter, iter_skill_files

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
README = ROOT / "README.md"
START = "<!-- SKILLS-INDEX:START -->"
END = "<!-- SKILLS-INDEX:END -->"
COUNT_START = "<!-- SKILLS-COUNT:START -->"
COUNT_END = "<!-- SKILLS-COUNT:END -->"
# Badge color (shields.io). Keep in step with the README badge row.
COUNT_COLOR = "2b7489"


def discover() -> list[tuple[str, str, str, str]]:
    records = []
    for p in iter_skill_files(SKILLS_DIR):
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        name = (fm.get("name") or p.parent.name).strip()
        desc = (fm.get("description") or "").strip()
        rel = p.relative_to(SKILLS_DIR).parts
        category = rel[0] if len(rel) >= 3 else "uncategorized"
        path_display = p.parent.relative_to(ROOT).as_posix()
        records.append((category, name, desc, path_display))
    return records


def render_index(rows: list[tuple[str, str, str, str]]) -> str:
    if not rows:
        return "_No skills yet. Add one under `skills/<category>/<name>/SKILL.md`._"
    by_cat: dict[str, list[tuple[str, str, str]]] = {}
    for category, name, desc, path in rows:
        by_cat.setdefault(category, []).append((name, desc, path))
    out: list[str] = []
    for category in sorted(by_cat):
        out.append(f"### {category}\n")
        out.append("| Skill | Description | Path |")
        out.append("| --- | --- | --- |")
        for name, desc, path in sorted(by_cat[category]):
            d = desc.replace("|", "\\|").replace("\n", " ")
            out.append(f"| `{name}` | {d} | `{path}/` |")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_count_badge(n: int) -> str:
    """A static shields.io badge for the live skill count."""
    label = "skill" if n == 1 else "skills"
    return f"![{n} {label}](https://img.shields.io/badge/skills-{n}-{COUNT_COLOR})"


def replace_between(text: str, start: str, end: str, payload: str, *, required: bool) -> str:
    """Swap the content between `start` and `end` markers for `payload`.

    Markers are kept on their own lines with the payload between them. When the
    markers are absent, raise (if required) or return the text unchanged.
    """
    if start not in text or end not in text:
        if required:
            raise SystemExit(
                "README.md is missing the index markers. Add these two lines "
                f"where the index should go:\n  {start}\n  {end}"
            )
        return text
    pre = text.split(start)[0]
    post = text.split(end, 1)[1]
    return f"{pre}{start}\n{payload}\n{end}{post}"


def main(argv: list[str]) -> int:
    check = "--check" in argv
    rows = discover()
    index_md = render_index(rows)
    badge_md = render_count_badge(len(rows))
    current = README.read_text(encoding="utf-8") if README.exists() else ""
    # The index keeps a blank line around it (table reads better); the badge sits
    # inline in the badge row, so no surrounding blank lines for that one.
    updated = replace_between(current, START, END, f"\n{index_md}", required=True)
    updated = replace_between(updated, COUNT_START, COUNT_END, badge_md, required=False)
    if check:
        if updated != current:
            print("README.md skills index or count badge is out of date. Run: make index")
            return 1
        print("Skills index and count badge are up to date.")
        return 0
    README.write_text(updated, encoding="utf-8")
    print(f"Updated README.md skills index ({len(rows)} skills).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
