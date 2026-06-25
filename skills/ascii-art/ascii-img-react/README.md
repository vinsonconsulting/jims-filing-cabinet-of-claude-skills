# ascii-img-react

<!-- card:begin summary -->

_Skill card pending. This skill ships a `SKILL.md` but has no published `card.json` yet, so the summary block fills in once it is carded._

<!-- card:end summary -->

<!-- card:begin badges -->

_Skill card pending. This skill ships a `SKILL.md` but has no published `card.json` yet, so the badges block fills in once it is carded._

<!-- card:end badges -->

## What it does

This skill renders an image as ASCII art in React through an `<AsciiImage>`
component. It matches each grid cell to the character whose shape fits best (6D
shape vectors with a nearest-neighbour lookup), so diagonals and curves read as
`/`, `\`, and `_` rather than a blocky brightness ramp. It also covers CSS-variable
theming, the CORS requirement for the source image, and Astro or Next integration.

## When it triggers

<!-- card:begin triggers -->

_Skill card pending. This skill ships a `SKILL.md` but has no published `card.json` yet, so the triggers block fills in once it is carded._

<!-- card:end triggers -->

## Install

Copy the skill folder into a place Claude reads skills.

```bash
git clone https://github.com/vinsonconsulting/claude-skill-foundry
cp -r claude-skill-foundry/skills/ascii-art/ascii-img-react ~/.claude/skills/
```

Use `.claude/skills/` inside a project to scope it to one repo instead of your user.

## Example

Ask for an ASCII image and the skill wires up the component.

> Add an ASCII portrait to my hero section, green on black, no ripple.

The skill installs `ascii-img-react`, then renders
`<AsciiImage src="/portrait.jpg" width={100} color="#39ff14" backgroundColor="#000" enableRipple={false} />`,
where `width` is measured in characters. It flags that the source image must be
same-origin or CORS-enabled, since the component samples it on a hidden canvas.

## Quality

<!-- card:begin metrics -->

_Skill card pending. This skill ships a `SKILL.md` but has no published `card.json` yet, so the metrics block fills in once it is carded._

<!-- card:end metrics -->

## Links

- [`SKILL.md`](SKILL.md): the instructions Claude follows.

The card files (`card.json`, `skill-card.md`, `report.sarif`) appear once this
skill is carded.
