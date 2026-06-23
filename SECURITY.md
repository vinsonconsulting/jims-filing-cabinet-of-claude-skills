# Security Policy

## What is in this repo

Static skills. Each one is a folder: a `SKILL.md` plus optional scripts,
references, and assets. There is no server, no database, and nothing running here.

That does not make a skill inert. A skill is a set of instructions a model
follows, and some of the skills in this library instruct Claude to run shell
commands, make network calls, or read and write files in your workspace. The
risk is not the Markdown sitting on disk. It is what a capable model will do when
it reads that Markdown and acts on it. Treat a skill you install like code you are
about to run, because functionally that is what it is.

## How skills are scanned

Every skill is scanned with [SkillSpector](https://github.com/NVIDIA/SkillSpector)
on a static pass (`--no-llm`, SARIF plus JSON output) by `make check` and by CI on
every push. The
scan runs against the skill's text surface only. Bundled binary assets like fonts
and images are data, not instructions, so they are excluded rather than fed to the
scanner as noise.

SkillSpector scores a skill from 0 to 100. The gate maps that score to a band:

| Score | Band | Meaning |
| --- | --- | --- |
| 0 to 20 | LOW | Passes. |
| 21 to 50 | MEDIUM | Passes only if every finding is recorded on the skill's card with `status: accepted` and a non-empty note. No blank overrides. |
| 51 to 80 | HIGH | Hard fail. |
| 81 to 100 | CRITICAL | Hard fail. |

Two rules sit on top of the bands:

- Any single finding with CRITICAL severity fails the build, whatever the total
  score is.
- While the library is still carding its older skills, a MEDIUM-band skill that
  has no card yet warns instead of failing. HIGH, CRITICAL, and any
  CRITICAL-severity finding are never relaxed.

The scan result lands in each carded skill's `card.json` and shows in the
[README catalog](README.md#catalog) under the `Scan` column. CI fails the build on
HIGH or CRITICAL, so a skill that scores in those bands does not merge.

## Before you install a skill

- Read its `SKILL.md`. You are about to let a model act on it.
- Check the card's declared permissions and external endpoints (the `card.json`
  records whether the skill expects shell, network, or file access).
- Prefer skills with a LOW scan. For a MEDIUM, read the accepted findings and the
  notes explaining why they were accepted.
- The catalog's `Scan` column exists so you do not have to guess. A `—` means the
  skill is not carded yet, so judge it the way you would any unscanned code.

## Reporting a vulnerable or malicious skill

<!-- TODO(jim): set the reporting contact before announcing this policy. Pick one:
     a private email, or enable GitHub Private Vulnerability Reporting
     (Settings → Code security and analysis → Private vulnerability reporting)
     and link the advisory form here. -->

TODO(jim): reporting contact goes here (a private email, or GitHub Private
Vulnerability Reporting).

Please do not open a public issue for an active exploit. If a skill in this
library tells a model to do something harmful, or a script does something its card
does not declare, report it privately so it can be pulled before it spreads.
