# image-to-ascii

<!-- card:begin summary -->

Convert an image file to ASCII art from the command line with shape-aware glyph matching (6D shape vectors, not a brightness ramp), output as .txt or a rendered .png/.svg, using a bundled monospace font for deterministic results.

<!-- card:end summary -->

<!-- card:begin badges -->

[![scan: MEDIUM (39/100)](https://img.shields.io/static/v1?label=scan&message=MEDIUM%20%2839/100%29&color=yellow)](skill-card.md)
![status: beta](https://img.shields.io/static/v1?label=status&message=beta&color=blue)
![card: v1.0](https://img.shields.io/static/v1?label=card&message=v1.0&color=555)
![signing: hash](https://img.shields.io/static/v1?label=signing&message=hash&color=555)

<!-- card:end badges -->

## What it does

This skill converts an image file to ASCII art from the command line. It matches
each cell to the glyph whose shape fits best (6D shape vectors with a
nearest-neighbour lookup) instead of using a brightness ramp, so edges stay sharp.
It ships a monospace font so a given image renders the same way every run, and it
writes `.txt`, `.png`, or `.svg` through `scripts/image_to_ascii.py`.

## When it triggers

<!-- card:begin triggers -->

**Use it when**

- make ASCII art of this photo
- convert this logo PNG to an ASCII text file for my README
- turn this screenshot into ASCII art saved as a .txt
- batch-convert a folder of images to ASCII art
- render this image as an ASCII .png, white text on black
- sharpen the edges on my logo's image-to-ASCII conversion

**Reach for a sibling instead when**

- render an image as ASCII art in a React component or on a web page → use [`ascii-img-react`](../ascii-img-react/README.md)
- build a real-time generative textmode sketch (webcam, animation, WebGL) → use [`textmode-js`](../textmode-js/README.md)
- make a figlet-style ASCII banner from a word → figlet/toilet text-banner tools (this converts images, not words)

<!-- card:end triggers -->

## Install

Copy the skill folder into a place Claude reads skills.

```bash
git clone https://github.com/vinsonconsulting/jims-filing-cabinet-of-claude-skills
cp -r jims-filing-cabinet-of-claude-skills/skills/ascii-art/image-to-ascii ~/.claude/skills/
```

Use `.claude/skills/` inside a project to scope it to one repo instead of your user.

## Example

Point it at an image and it runs the converter.

> Convert this logo PNG to an ASCII text file for my README, 120 columns wide.

The skill runs `python3 scripts/image_to_ascii.py logo.png --cols 120 --out logo.txt`,
sampling each cell to its best-fitting glyph. Add `--out logo.png` for a rendered
image, or `--invert` for white characters on black.

## Quality

<!-- card:begin metrics -->

Quality metrics are not published yet (status: beta). The security scan is MEDIUM (39/100).

<!-- card:end metrics -->

The scan findings are reviewed and accepted; see [`skill-card.md`](skill-card.md)
and [`scan.json`](scan.json) for the notes on each one.

## Links

- [`SKILL.md`](SKILL.md): the instructions Claude follows.
- [`skill-card.md`](skill-card.md): the card in human-readable form.
- [`card.json`](card.json): the card in machine form.
- [`scan.json`](scan.json): the SkillSpector scan and findings.
