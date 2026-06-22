<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img alt="Jim's Filing Cabinet of Claude Skills" src="assets/hero-light.svg" width="760">
  </picture>
</p>

<h1 align="center">Jim's Filing Cabinet of Claude Skills</h1>

<p align="center">Small, self-contained skills a model loads on demand. Clone, copy a folder, done.</p>

[![validate](https://github.com/vinsonconsulting/jims-filing-cabinet-of-claude-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/vinsonconsulting/jims-filing-cabinet-of-claude-skills/actions/workflows/validate.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-2b7489)](LICENSE)
<!-- SKILLS-COUNT:START -->
![6 skills](https://img.shields.io/badge/skills-6-2b7489)
<!-- SKILLS-COUNT:END -->
<!-- SCANS:START -->
![scans: 4/6 carded · worst MEDIUM](https://img.shields.io/static/v1?label=scans&message=4/6%20carded%20%C2%B7%20worst%20MEDIUM&color=yellow)
<!-- SCANS:END -->
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-2b7489)](CONTRIBUTING.md)

## What this is

A library of Claude skills. Each one is a folder with a `SKILL.md` and whatever
scripts, references, or assets it needs. Claude reads the description to decide
when a skill applies, then follows the instructions inside. The folders are
portable, so you copy one into your own setup and it works.

The catalog below is the index. The build pipeline that produces each skill, and
the per-skill cards that record how it scored, sit further down under
[How these are built](#how-these-are-built).

## Quickstart

Install one skill by copying its folder into a place Claude reads skills. Take the
skill folder, not the category above it.

```bash
git clone https://github.com/vinsonconsulting/jims-filing-cabinet-of-claude-skills
cp -r jims-filing-cabinet-of-claude-skills/skills/tui/bubbletea ~/.claude/skills/
```

That installs `bubbletea` for your user. Use `.claude/skills/` inside a project
instead to scope it to one repo. In Claude's browser apps, add the `SKILL.md` and
any files it points to as Project knowledge, or paste it into a conversation.

## Catalog

Each category links to its own index; each skill links to its page. `Scan` is the
SkillSpector severity and score; `Trigger (P/R)` is the measured precision and
recall, shown once a skill has published metrics. Both columns read from each
skill's `card.json`, so they cannot go stale silently.

<!-- SKILLS-INDEX:START -->

### [ascii-art](skills/ascii-art/README.md)

| Skill | What it does | Scan | Trigger (P/R) |
| --- | --- | --- | --- |
| [`ascii-img-react`](skills/ascii-art/ascii-img-react/README.md) | Use when rendering images as ASCII art in the browser or a React app with the ascii-img-react library | — | — |
| [`image-to-ascii`](skills/ascii-art/image-to-ascii/README.md) | Convert an image file to ASCII art from the command line with shape-aware glyph matching (6D shape vectors, not a brightness ramp), output as .txt or a rendered .png/.svg, using a bundled monospace font for deterministic results. | MEDIUM (39/100) | — |
| [`textmode-js`](skills/ascii-art/textmode-js/README.md) | Use when building real-time ASCII or textmode graphics in the browser with the textmode.js library | — | — |

### [tui](skills/tui/README.md)

| Skill | What it does | Scan | Trigger (P/R) |
| --- | --- | --- | --- |
| [`bubbletea`](skills/tui/bubbletea/README.md) | Build current Bubble Tea v2 terminal UIs in Go on the charm.land import paths — the Elm/MVU pattern, Lip Gloss, Bubbles, Glamour, streaming, and teatest. | LOW (13/100) | — |
| [`ratatui`](skills/tui/ratatui/README.md) | Write current, compiling Ratatui 0.30+ terminal UIs in Rust — render loop and teardown, Layout/Constraint, widgets, styling, Unicode width, streaming, and headless render tests. | LOW (13/100) | — |
| [`textual`](skills/tui/textual/README.md) | Build and debug Python TUIs with Textual 8.x — App/Screen/Widget, reactive attributes, TCSS layout, @work workers, Pilot tests, and textual serve. | LOW (0/100) | — |

<!-- SKILLS-INDEX:END -->

The table above is generated from the skill cards by `make index`. Do not edit
between the markers by hand.

## How these are built

Every skill goes through the same pipeline before it ships. A research dossier
collects the current, version-correct facts. Those become the `SKILL.md` body and
its trigger description. An eval set checks that the skill fires on the right
prompts and finishes the task. A description optimizer tightens the trigger
wording against held-out cases. SkillSpector scans the skill's text surface for
security findings. The result is a Skill Card.

A Skill Card is the per-skill record of what was measured and when: a `card.json`
(the machine form) plus a human-readable `skill-card.md`. It records the scan
result and the trigger metrics, keyed to a content hash of the source. See a
live example in the [`textual` skill card](skills/tui/textual/skill-card.md).
The catalog above reads its `Scan` and `Trigger` columns straight from each card,
and `make check` fails if a README drifts from the cards.

## Repo layout

```
skills/<category>/<skill-name>/
  SKILL.md            # required: frontmatter (name + description) + instructions
  README.md           # this skill's page (card blocks rendered from card.json)
  card.json           # the Skill Card: scan, triggers, metrics, provenance
  skill-card.md       # human-readable view of the card
  report.sarif        # SkillSpector findings
  evals/              # trigger + functional eval cases
  reference/          # optional: docs the skill points to
  scripts/            # optional: helper scripts the skill runs
  assets/             # optional: templates, fonts, samples
```

Names are kebab-case and the folder name matches the skill `name`. Folders under
`skills/` that start with `_` (like `_TEMPLATE`) are ignored by the tooling.
`make check` runs lint, the card gate, and the README freshness checks; CI
(`.github/workflows/validate.yml`) runs the same, so a stale catalog or a lint
failure fails the build.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md) to add or change a skill. Released under the
MIT license; see [LICENSE](LICENSE).
