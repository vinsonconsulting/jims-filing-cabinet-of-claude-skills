#!/usr/bin/env python3
"""Run a functional grader against a generated artifact.

Usage:
  python run_grader.py --task <task-id> --readme <path-to-artifact> [--out grading.json]
  python run_grader.py --list

Loads tasks.json (sibling file), dispatches to graders.py, and writes a grading.json
shaped {expectations:[{text,passed,evidence}], summary:{passed,total,pass_rate}} — the
shape the eval viewer and aggregator expect.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import graders  # noqa: E402


def load_tasks() -> dict:
    data = json.loads((HERE / "tasks.json").read_text(encoding="utf-8"))
    return {t["id"]: t for t in data["tasks"]}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task")
    ap.add_argument("--readme")
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    tasks = load_tasks()
    if args.list:
        for tid, t in tasks.items():
            print(f"{tid}: {t['name']}")
        return 0

    if not args.task or not args.readme:
        ap.error("--task and --readme are required (or use --list)")
    if args.task not in tasks:
        ap.error(f"unknown task {args.task!r}; choose from {list(tasks)}")

    readme = Path(args.readme).read_text(encoding="utf-8")
    result = graders.grade(args.task, readme, tasks[args.task].get("grader_config", {}))
    out = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(out + "\n", encoding="utf-8")
    print(out)
    s = result["summary"]
    # Exit non-zero if any assertion failed, so this is usable as a CI gate.
    return 0 if s["passed"] == s["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
