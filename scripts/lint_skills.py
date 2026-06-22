#!/usr/bin/env python3
"""Validate every SKILL.md under skills/.

Baseline checks (tune to taste in this file):
  ERROR  missing frontmatter block
  ERROR  missing or empty `name`
  ERROR  missing or empty `description`
  ERROR  `name` is not a kebab-case slug (lowercase, hyphen-separated)
  ERROR  category or skill folder is not kebab-case (agentskills.io rejects underscores)
  WARN   `name` does not match the skill folder name (skipped for namespaced a:b)
  WARN   description longer than DESCRIPTION_MAX chars
  WARN   a relative file referenced in the body does not exist

Exit code: 1 if any ERROR, or any WARN when run with --strict. Otherwise 0.

Usage:
  python3 scripts/lint_skills.py
  python3 scripts/lint_skills.py --strict
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

from skilltools import parse_frontmatter, iter_skill_files

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

DESCRIPTION_MAX = 1024
# Kebab-case only: the agentskills.io slug regex rejects underscores, so the
# cabinet does too. NAME_RE allows one namespace segment (a:b); SLUG_RE is the
# plain form for directory names (category + skill folder), never namespaced.
NAME_RE = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*(?::[a-z0-9]+(?:-[a-z0-9]+)*)?$"
)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_RE = re.compile(
    r"(?:\]\(|`)((?:scripts|reference|references|assets|data)/[^)\s`]+)"
)
TRIGGER_RE = re.compile(
    r"\b(use\s+(this\s+|the\s+)?(skill\s+)?(when|for)|whenever|when\s+the\s+user|when\s+you\s+need|trigger)\b",
    re.IGNORECASE,
)


def lint_skill(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    text = path.read_text(encoding="utf-8")
    has_fm = text.lstrip().startswith("---")
    fm = parse_frontmatter(text)

    if not has_fm:
        errors.append("missing YAML frontmatter (--- block)")
    name = (fm.get("name") or "").strip()
    desc = (fm.get("description") or "").strip()
    if not name:
        errors.append("missing or empty `name`")
    if not desc:
        errors.append("missing or empty `description`")
    if name and not NAME_RE.match(name):
        errors.append(f"`name` is not a kebab-case slug (no underscores): {name!r}")
    folder = path.parent.name
    if not SLUG_RE.match(folder):
        errors.append(f"skill folder is not kebab-case (no underscores): {folder!r}")
    rel_parts = path.relative_to(SKILLS_DIR).parts
    if len(rel_parts) >= 3 and not SLUG_RE.match(rel_parts[0]):
        errors.append(f"category folder is not kebab-case (no underscores): {rel_parts[0]!r}")
    if name and ":" not in name and name != folder:
        warns.append(f"`name` ({name!r}) does not match folder ({folder!r})")
    if desc and len(desc) > DESCRIPTION_MAX:
        warns.append(f"description is {len(desc)} chars (> {DESCRIPTION_MAX})")
    if desc and not TRIGGER_RE.search(desc):
        warns.append("description may lack explicit trigger language (e.g. \"Use when ...\")")

    body = text.split("---", 2)[-1] if has_fm else text
    for m in REF_RE.finditer(body):
        ref = m.group(1)
        if not (path.parent / ref).exists():
            warns.append(f"referenced file not found: {ref}")
    return errors, warns


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    files = iter_skill_files(SKILLS_DIR)
    if not files:
        print("No skills found under skills/. Nothing to lint.")
        return 0

    total_err = 0
    total_warn = 0
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        errors, warns = lint_skill(path)
        total_err += len(errors)
        total_warn += len(warns)
        if not errors and not warns:
            print(f"[ok]   {rel}")
            continue
        tag = "[FAIL]" if errors else "[warn]"
        print(f"{tag} {rel}")
        for e in errors:
            print(f"         error: {e}")
        for w in warns:
            print(f"         warn:  {w}")

    print(
        f"\n{len(files)} skill(s) checked, "
        f"{total_err} error(s), {total_warn} warning(s)."
    )
    if total_err or (strict and total_warn):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
