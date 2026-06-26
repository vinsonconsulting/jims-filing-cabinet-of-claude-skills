#!/usr/bin/env python3
"""Render a per-skill SVG skill card for every skill + a root rollup, into READMEs.

For each skill this renders a deterministic dark "skill card" SVG via
`herocard.render` (identity, when-to-use, output, dependencies, quality, security)
and fills the per-skill README's `scorecard` markers with an `<img>` to it. A
carded skill (`card.json`) renders its real values; an un-carded skill (SKILL.md
only) renders its name + when-to-use with the data sections marked "not yet
carded", so all skills get a card with no invented data. It also renders an
aggregate rollup from the carded cards and fills the root README's `SCORECARD`
markers (via `skillcard.scorecard.render_rollup`).

The SVGs live under `assets/scorecards/` (NOT beside the card): a card SVG is not
in Califa's `content_hash` exclusion list, so writing it into the skill dir would
move the skill's hash and break `make cards`. README files ARE hash-excluded, so
embedding the `<img>` is safe.

This is an asset step, not a correctness gate (`make check` does not run it).
`--check` exits 1 on any drift (an SVG or a README block), so CI can
regenerate-and-diff — which also re-proves determinism, since a stale card would
re-render to different bytes.

Usage:
  python3 scripts/build_scorecards.py            # write SVGs + fill the markers
  python3 scripts/build_scorecards.py --check    # exit 1 if anything is stale
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import cardkit
import herocard
from skilltools import iter_skill_files, parse_frontmatter

from schema.schema import SkillCard
from skillcard import scorecard

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
ASSETS_DIR = ROOT / "assets" / "scorecards"
ROLLUP_SVG = ROOT / "assets" / "scorecard-rollup.svg"
README = ROOT / "README.md"
README_NAME = "README.md"

# The rollup card's title; this catalog is the public foundry corpus.
ROLLUP_TITLE = "claude-skill-foundry"

CARD_SCORECARD = ("<!-- card:begin scorecard -->", "<!-- card:end scorecard -->")
ROOT_SCORECARD = ("<!-- SCORECARD:START -->", "<!-- SCORECARD:END -->")

SEVERITY_ORDER = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def replace_between(text: str, start: str, end: str, payload: str) -> str:
    """Swap content between markers; leave text unchanged if either is absent."""
    if start not in text or end not in text:
        return text
    pre = text.split(start)[0]
    post = text.split(end, 1)[1]
    return f"{pre}{start}\n{payload}\n{end}{post}"


def _rel(target: Path, from_dir: Path) -> str:
    return os.path.relpath(target, from_dir).replace(os.sep, "/")


def _category_of(skill_dir: Path) -> str:
    rel = skill_dir.relative_to(SKILLS_DIR).parts
    return rel[0] if len(rel) >= 2 else "uncategorized"


def _svg_path(skill_dir: Path) -> Path:
    return ASSETS_DIR / _category_of(skill_dir) / f"{skill_dir.name}.svg"


def _footer(card: dict) -> str:
    """The card footer: the metrics harness if measured, else the scan provenance."""
    metrics = card.get("metrics") or {}
    if metrics.get("harness"):
        return f"harness  {metrics['harness']}"
    scan = card.get("scan")
    if scan:
        return f"scan  {scan.get('tool', '?')} · {scan.get('date', '')}"
    return ""


def all_skills() -> list[tuple[str, Path, dict, dict | None]]:
    """(name, skill_dir, render_card, raw_card_or_None) for every skill.

    ``render_card`` is the dict passed to herocard: the validated card.json for a
    carded skill (plus a footer), or a sparse ``{name, status, description}`` built
    from the SKILL.md frontmatter for an un-carded one. ``raw_card_or_None`` is the
    card.json (for the rollup aggregate) or None.
    """
    out: list[tuple[str, Path, dict, dict | None]] = []
    for p in iter_skill_files(SKILLS_DIR):
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        name = (fm.get("name") or p.parent.name).strip()
        card = cardkit.load_card(p.parent)
        if card is not None:
            SkillCard.model_validate(card)
            render = dict(card)
            render["footer"] = _footer(card)
            out.append((name, p.parent, render, card))
        else:
            render = {
                "name": name,
                "status": "draft",
                "description": (fm.get("description") or "").strip(),
                "footer": "SKILL.md only · card pending",
            }
            out.append((name, p.parent, render, None))
    return out


def build_summary(cards: list[dict], total: int) -> dict:
    """Aggregate the corpus posture for the rollup (worst-severity wins)."""
    counts = {band: 0 for band in SEVERITY_ORDER}
    worst: str | None = None
    with_metrics = 0
    for card in cards:
        sev = (card.get("scan") or {}).get("severity")
        if sev in counts:
            counts[sev] += 1
            if worst is None or SEVERITY_ORDER.index(sev) > SEVERITY_ORDER.index(worst):
                worst = sev
        if card.get("metrics"):
            with_metrics += 1
    return {
        "title": ROLLUP_TITLE,
        "total": total,
        "carded": len(cards),
        "with_metrics": with_metrics,
        "severity_counts": counts,
        "worst": worst,
    }


def _embed(src_rel: str, alt: str) -> str:
    return f'<img src="{src_rel}" alt="{alt}" width="640">'


def run(check: bool) -> int:
    skills = all_skills()
    total = len(skills)
    changes: list[str] = []

    def apply(path: Path, new_text: str) -> None:
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        if new_text == old:
            return
        changes.append(str(path.relative_to(ROOT)))
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new_text, encoding="utf-8")

    # Per-skill: render the fuller card, embed it.
    for name, skill_dir, render_card, _raw in skills:
        svg_path = _svg_path(skill_dir)
        apply(svg_path, herocard.render(render_card))
        readme = skill_dir / README_NAME
        if readme.exists():
            embed = _embed(_rel(svg_path, skill_dir), f"{name} skill card")
            text = readme.read_text(encoding="utf-8")
            text = replace_between(text, *CARD_SCORECARD, f"\n{embed}\n")
            apply(readme, text)

    # Root rollup, aggregated over the carded skills only.
    carded = [raw for *_x, raw in skills if raw is not None]
    summary = build_summary(carded, total)
    apply(ROLLUP_SVG, scorecard.render_rollup(summary))
    if README.exists():
        embed = _embed(_rel(ROLLUP_SVG, ROOT), "skill cards rollup")
        text = README.read_text(encoding="utf-8")
        text = replace_between(text, *ROOT_SCORECARD, f"\n{embed}\n")
        apply(README, text)

    if check:
        if changes:
            print("Skill cards are out of date:")
            for c in changes:
                print(f"  - {c}")
            print("Run: make scorecards")
            return 1
        print("Skill cards are up to date.")
        return 0
    print(f"Generated skill cards ({len(changes)} file(s) updated).")
    return 0


def main(argv: list[str]) -> int:
    return run("--check" in argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
