

<h1 align="center">claude-skill-foundry</h1>

<p align="center">A scoring harness for Claude Skills. Each carded skill ships a Skill Card: a SkillSpector security scan and trigger evals, generated and gated in CI so the catalog can't drift from what was measured.</p>

<!-- build / CI -->
[![validate](https://github.com/vinsonconsulting/claude-skill-foundry/actions/workflows/validate.yml/badge.svg)](https://github.com/vinsonconsulting/claude-skill-foundry/actions/workflows/validate.yml)

<!-- catalog (counts read from the skill cards by `make index`) -->
<!-- SKILLS-COUNT:START -->
[![6 skills](https://img.shields.io/badge/skills-6-2b7489)](#catalog)
<!-- SKILLS-COUNT:END -->
<!-- SCANS:START -->
[![scans: 4/6 carded · worst MEDIUM](https://img.shields.io/static/v1?label=scans&message=4/6%20carded%20%C2%B7%20worst%20MEDIUM&color=yellow)](#catalog)
<!-- SCANS:END -->

<!-- meta -->
[![license: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-2b7489)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-2b7489)](CONTRIBUTING.md)
[![last commit](https://img.shields.io/github/last-commit/vinsonconsulting/claude-skill-foundry)](https://github.com/vinsonconsulting/claude-skill-foundry/commits/main)
[![repo size](https://img.shields.io/github/repo-size/vinsonconsulting/claude-skill-foundry)](https://github.com/vinsonconsulting/claude-skill-foundry)

## What this is

This repo scores Claude Skills. Each carded skill ships a Skill Card that records
how it scored: a SkillSpector security scan and a trigger eval, keyed to a content
hash of the source. The catalog further down reads straight from those cards, so
the numbers are generated rather than hand-typed, and the table cannot quietly
drift away from the truth.

New to skills? A skill is a folder. It holds a `SKILL.md` and whatever scripts,
references, or assets that skill needs. Claude reads the description to decide when
the skill applies, then follows the instructions inside. The folders carry no
global state and no install step, so you copy one into your own setup and it works.

The six skills here are the corpus the scoring runs against. Start with the
[Catalog](#catalog) to grab one, or read [How these are built](#how-these-are-built)
for the pipeline that produces a card.

## Reading the scores

Every carded skill carries a SkillSpector security scan: a static pass over the
skill's text surface, run with no model calls, scored from 0 to 100 where a higher
number means more risk. The gate maps that score to a band.

| Band | Score | Gate |
| --- | --- | --- |
| LOW | 0 to 20 | Passes. |
| MEDIUM | 21 to 50 | Passes only if every finding is recorded on the card as `accepted` with a written note. |
| HIGH | 51 to 80 | Hard fail. Does not merge. |
| CRITICAL | 81 to 100 | Hard fail. Does not merge. |

Lower is safer, and LOW is the cleanest result. Any single finding with CRITICAL
severity fails the build on its own, whatever the total score.

**Carded** means the skill ships a committed Skill Card: a `card.json` for the
tooling and a human-readable `skill-card.md`, both keyed to a content hash of the
source so the card always describes the exact bytes it was built from. The card
format follows the [califa-cards](https://github.com/vinsonconsulting/califa-cards)
SPEC. A skill with no card yet shows `—` in the catalog instead of a number.

**Trigger (P/R)** is the measured precision and recall of a skill's triggering.
The eval cases live in each card today; the published precision and recall numbers
do not yet, so the column reads `—` for now.

So the summary badge **`4/6 carded · worst MEDIUM`** reads like this: four of the
six skills are carded, and the riskiest of those four sits at MEDIUM with its
findings accepted and justified on the card. The other three are LOW. Two skills
are not carded yet.

## A worked card

Here is what a scored skill looks like. `textual` builds and debugs Python TUIs
with Textual 8.x.

| Field | Value |
| --- | --- |
| Scan | LOW (0/100), no findings |
| Permissions | shell, file (no network, env, or MCP) |
| Dependencies | `textual>=8.2,<9`, `rich>=15.0`, `python>=3.9` |
| Source | pinned to a `content_hash` of the skill folder |
| Status | beta |

The full card is at
[`skills/tui/textual/skill-card.md`](skills/tui/textual/skill-card.md).

A clean scan is the easy case. When the scanner does find something, the card has
to account for it. `image-to-ascii` scores MEDIUM (39/100) on five findings, and
every one is recorded as `accepted` with a written reason: one for the file read
and write that are the converter's documented job, and four that match a legal
phrase inside a bundled font license rather than any skill instruction. The MEDIUM
band passes only because each finding is justified on the card, not waved through.
See [`skills/ascii-art/image-to-ascii/skill-card.md`](skills/ascii-art/image-to-ascii/skill-card.md).

## What you get

- **Portable folders.** Copy one into a skills directory and go. No package
  manager, no global config, nothing to undo later.
- **A security scan on every skill, gated in CI.** SkillSpector runs against each
  skill's text surface on every push, and the gate fails the build on a HIGH or
  CRITICAL result. See [Reading the scores](#reading-the-scores) for the bands.
- **Measured triggering, not vibes.** Whether a skill fires on the prompts it
  should is something you can measure, so it gets measured.
- **An honest catalog.** The `Scan` and `Trigger` columns are wired to the cards.
  A skill that is not carded yet shows a `—` rather than a made-up number.

## Quickstart

Install a skill by copying its folder into a place Claude reads skills. The unit
you copy is the skill folder itself (`bubbletea`), not the category folder above
it (`tui`).

```bash
git clone https://github.com/vinsonconsulting/claude-skill-foundry
cp -r claude-skill-foundry/skills/tui/bubbletea ~/.claude/skills/
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
go stale while the cards say otherwise. See [Reading the scores](#reading-the-scores)
to decode the bands and the `—` placeholders.

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

## Built on

- **Skill Card format and tooling.** The cards here conform to the
  [califa-cards](https://github.com/vinsonconsulting/califa-cards) SPEC, an
  Apache-2.0 standard for recording what a skill is and how it scored. The
  `skillcard` CLI that builds, gates, and validates each card is vendored under
  `tooling/califa/`.
- **Security scanner.** [SkillSpector](https://github.com/NVIDIA/SkillSpector)
  from NVIDIA, run static (`--no-llm`) on every push.

califa-cards is the standard; this repo is one corpus that exercises it.

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

No. This is a personal library, Apache-2.0 licensed, with no affiliation to Anthropic.
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
Apache-2.0 license; see [LICENSE](LICENSE).
