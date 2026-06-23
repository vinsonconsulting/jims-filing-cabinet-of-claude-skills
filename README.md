<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img alt="Jim's Filing Cabinet of Claude Skills" src="assets/hero-light.svg" width="760">
  </picture>
</p>

<h1 align="center">Jim's Filing Cabinet of Claude Skills</h1>

<p align="center">A library of self-contained Claude skills you copy into your setup, each one security-scanned and measured before it ships.</p>

<!-- build / CI -->
[![validate](https://github.com/vinsonconsulting/jims-filing-cabinet-of-claude-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/vinsonconsulting/jims-filing-cabinet-of-claude-skills/actions/workflows/validate.yml)

<!-- catalog (counts read from the skill cards by `make index`) -->
[<!-- SKILLS-COUNT:START -->
![6 skills](https://img.shields.io/badge/skills-6-2b7489)
<!-- SKILLS-COUNT:END -->](#catalog)
[<!-- SCANS:START -->
![scans: 4/6 carded · worst MEDIUM](https://img.shields.io/static/v1?label=scans&message=4/6%20carded%20%C2%B7%20worst%20MEDIUM&color=yellow)
<!-- SCANS:END -->](#catalog)

<!-- meta -->
[![license: MIT](https://img.shields.io/badge/license-MIT-2b7489)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-2b7489)](CONTRIBUTING.md)
[![last commit](https://img.shields.io/github/last-commit/vinsonconsulting/jims-filing-cabinet-of-claude-skills)](https://github.com/vinsonconsulting/jims-filing-cabinet-of-claude-skills/commits/main)
[![repo size](https://img.shields.io/github/repo-size/vinsonconsulting/jims-filing-cabinet-of-claude-skills)](https://github.com/vinsonconsulting/jims-filing-cabinet-of-claude-skills)

## What this is

A skill is a folder. It holds a `SKILL.md` and whatever scripts, references, or
assets that skill needs. Claude reads the description to decide when the skill
applies, then follows the instructions inside. The folders carry no global state
and no install step, so you copy one into your own setup and it works.

This repo is a shelf of those folders. What makes it different is what rides along
with each one: a Skill Card. Every skill ships a recorded SkillSpector security
scan plus measured trigger metrics, and the catalog further down reads straight
from those cards. The numbers in the table are not hand-typed marketing. They are
generated, so the catalog cannot quietly drift away from the truth.

The build pipeline that produces a skill, and the cards that record how it scored,
sit lower down under [How these are built](#how-these-are-built). Start with the
[Catalog](#catalog) if you just want to grab something.

## What you get

- **Portable folders.** Copy one into a skills directory and go. No package
  manager, no global config, nothing to undo later.
- **A security scan on every skill, gated in CI.** SkillSpector runs against each
  skill's text surface on every push. A HIGH or CRITICAL score fails the build.
- **Measured triggering, not vibes.** Whether a skill actually fires on the
  prompts it should is something you can measure, so it gets measured.
- **An honest catalog.** The `Scan` and `Trigger` columns are wired to the cards.
  Nothing is carded yet shows a `—` rather than a made-up number.

## Quickstart

Install a skill by copying its folder into a place Claude reads skills. The unit
you copy is the skill folder itself (`bubbletea`), not the category folder above
it (`tui`).

```bash
git clone https://github.com/vinsonconsulting/jims-filing-cabinet-of-claude-skills
cp -r jims-filing-cabinet-of-claude-skills/skills/tui/bubbletea ~/.claude/skills/
```

That installs `bubbletea` for your user. There are three places it can live:

- **User scope:** `~/.claude/skills/` makes the skill available in every project.
- **Project scope:** `.claude/skills/` inside a repo scopes it to that repo, which
  is the right call for a skill only one project needs.
- **Claude's web and desktop apps:** add the `SKILL.md` and the files it points to
  as Project knowledge, or paste a `SKILL.md` straight into a conversation.

## Catalog

Each category links to its own index; each skill links to its page. `Scan` is the
SkillSpector severity and score, and `Trigger (P/R)` is the measured precision and
recall once a skill has published metrics. Both columns read from each skill's
`card.json`, so a skill cannot claim a score it did not earn, and the table cannot
go stale while the cards say otherwise.

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

Every skill runs the same gauntlet before it lands. A research dossier collects
the current, version-correct facts. Those become the `SKILL.md` body and its
trigger description. An eval set checks that the skill fires on the prompts it
should and finishes the task once it does. A description optimizer tightens the
trigger wording against held-out cases. SkillSpector scans the text surface for
security findings. The result is a Skill Card.

The triggering step is the one people skip, and it is the one that matters most.
Under-triggering is the dominant failure mode for skills: a skill that never fires
is just markdown and hope. So triggering is measured against held-out prompts
rather than eyeballed, and the result is a column in the catalog instead of a
footnote. A skill that scores well on security but never activates is not a good
skill. It is a quiet one.

## Skill Cards

A Skill Card is the per-skill record of what was measured and when. It comes in
two forms: a `card.json` (the machine form the tooling reads) and a human-readable
`skill-card.md`. The card records the SkillSpector scan result and the trigger
metrics, keyed to a content hash of the skill's source, so a card always describes
the exact bytes it was built from. Change the source and the hash no longer
matches, which is the point: `make check` rebuilds each card from its committed
inputs and fails if the result drifts from what is checked in.

See a live example in the [`textual` skill card](skills/tui/textual/skill-card.md).

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

Names are kebab-case and the folder name matches the skill's `name`. Folders under
`skills/` that start with `_` (like `_TEMPLATE`) are ignored by the tooling.
`make check` runs lint, the card gate, and the README freshness checks; CI
(`.github/workflows/validate.yml`) runs the same, so a stale catalog or a lint
failure fails the build just as it would on your machine.

## FAQ

**Are these official Anthropic skills?**

No. This is a personal library, MIT licensed, with no affiliation to Anthropic.
The skills target Claude because that is what I use, but the format is just folders
of Markdown and scripts.

**What is a Skill Card?**

The per-skill record of what was measured: a `card.json` plus a human-readable
`skill-card.md`, holding the security scan result and any trigger metrics, keyed to
a content hash of the source. It is how a skill in this repo shows its work instead
of asking you to trust it.

**Why does the catalog show trigger precision and recall?**

Because a skill that never fires does nothing, and under-triggering is the most
common way skills fail in practice. Measuring whether a skill activates on the
right prompts (and stays quiet on the wrong ones) keeps the library honest about
which skills actually earn their place.

**Why scan a folder of Markdown?**

Because a skill is not passive text. It is a set of instructions a model follows,
and some skills tell Claude to run shell commands, reach the network, or read and
write files in your workspace. The study behind
[SkillSpector](https://github.com/NVIDIA/SkillSpector), the scanner this library
uses, looked at 42,447 real-world skills and found 26.1% carried at least one
vulnerability and 5.2% showed likely malicious intent. A static scan is cheap
insurance against installing one of those without noticing.

**Can I use these outside Claude Code?**

Yes. Copy a folder into the API or Claude's apps as Project knowledge, or paste a
`SKILL.md` straight into a conversation. Nothing here is specific to the CLI.

**Some skills show `—` for scan or trigger. Why?**

They are not carded yet. The badge and the catalog say so on purpose. A blank is
more honest than a placeholder number, and it makes the carding backlog visible
rather than hiding it.

**How do I add one?**

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: `make check` has to
pass and the skill needs a card.

## Security

These are static skills, but a skill is instructions a model follows, and some of
them run shell, touch the network, or write files. Treat an installed skill like
code you are about to run. Every skill is scanned with SkillSpector in `make check`
and in CI, and a HIGH or CRITICAL result fails the build. The full trust model,
the scoring bands, and how to report a vulnerable or malicious skill are in
[SECURITY.md](SECURITY.md).

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md) to add or change a skill. Released under the
MIT license; see [LICENSE](LICENSE).
