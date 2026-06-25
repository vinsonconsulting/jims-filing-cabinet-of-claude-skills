---
name: image-to-ascii
version: 0.1.0
summary: Convert an image file to ASCII art from the command line with shape-aware glyph matching (6D shape vectors, not a brightness ramp), output as .txt or a rendered .png/.svg, using a bundled monospace font for deterministic results.
owner: '@vinsonconsulting'
repo:
  tier: public
  url: https://github.com/vinsonconsulting/claude-skill-foundry
license: Apache-2.0
source_commit: 5e49df814225e1d33d63b52f49780175fd0a4ef2
content_hash: sha256:5c6b1646a7e845169642c667509afb4d7078b0a40170656e08ed28e161a322c1
description: Use when converting an image file to ASCII art outside the browser — a command-line or script run that turns a photo, logo, screenshot, or render into text, saved as .txt or rendered to .png/.svg. Trigger on "make ASCII art of this image/photo/cat", "convert this picture/logo to ASCII", "turn this PNG into an ASCII text file for my README", batch-converting a folder of images to ASCII, or any Python/Pillow image-to-ASCII task. Produces sharp, shape-aware output by matching each cell to the glyph whose shape fits best (6D shape vectors + nearest-neighbour, optional contrast enhancement) rather than a naive brightness ramp, and bundles a monospace font for deterministic results. Runs scripts/image_to_ascii.py. Not for ASCII graphics on a web page or in React (use ascii-img-react), not the real-time textmode.js library (use textmode-js), and not figlet-style text banners (this converts images, not words).
triggers:
  positive:
  - make ASCII art of this photo
  - convert this logo PNG to an ASCII text file for my README
  - turn this screenshot into ASCII art saved as a .txt
  - batch-convert a folder of images to ASCII art
  - render this image as an ASCII .png, white text on black
  - sharpen the edges on my logo's image-to-ASCII conversion
  negative:
  - prompt: render an image as ASCII art in a React component or on a web page
    use_instead: ascii-img-react
  - prompt: build a real-time generative textmode sketch (webcam, animation, WebGL)
    use_instead: textmode-js
  - prompt: make a figlet-style ASCII banner from a word
    use_instead: figlet/toilet text-banner tools (this converts images, not words)
inputs:
- 'An image file (PNG/JPG/etc.) plus options: --cols, --out/--format, --invert, --contrast.'
output:
  type: ASCII art
  format: .txt, .png, or .svg produced by scripts/image_to_ascii.py (a shell invocation)
dependencies:
- Pillow
- python>=3.9
external_endpoints: none
permissions:
  network: false
  shell: true
  file: true
  env: false
  mcp: false
metrics: null
scan:
  tool: skillspector@a5092dd9b9521ff57a9b53612bb129ce78019002
  score: 39
  severity: MEDIUM
  date: '2026-06-20'
  findings:
  - rule_id: LP3
    severity: MEDIUM
    status: accepted
    owasp: null
    atlas: null
    note: 'SkillSpector ''MCP Least Privilege'' (LP3) on SKILL.md: flags file_read / file_write with no scanner-recognized permissions declaration. Accepted, not fixed — LP3 reads a `permissions` *list*, but the Claude Code skill loader honors `allowed-tools`, not a SkillSpector-style permissions list, so adding one would be loader-ignored scanner-bait. The file I/O is the converter''s documented job (read an image, write the .txt/.png/.svg via scripts/image_to_ascii.py), confined to the workspace; external_endpoints is none and the skill makes no network calls.'
  - rule_id: EA3
    severity: LOW
    status: accepted
    owasp: null
    atlas: null
    note: 'SkillSpector ''Excessive Agency / Scope Creep'' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font''s license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it.'
  - rule_id: EA3
    severity: LOW
    status: accepted
    owasp: null
    atlas: null
    note: 'SkillSpector ''Excessive Agency / Scope Creep'' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font''s license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it.'
  - rule_id: EA3
    severity: LOW
    status: accepted
    owasp: null
    atlas: null
    note: 'SkillSpector ''Excessive Agency / Scope Creep'' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font''s license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it.'
  - rule_id: EA3
    severity: LOW
    status: accepted
    owasp: null
    atlas: null
    note: 'SkillSpector ''Excessive Agency / Scope Creep'' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font''s license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it.'
  sarif: ./report.sarif
status: beta
card_version: '1.0'
updated: '2026-06-20'
---

# image-to-ascii <small>v0.1.0</small>

Convert an image file to ASCII art from the command line with shape-aware glyph matching (6D shape vectors, not a brightness ramp), output as .txt or a rendered .png/.svg, using a bundled monospace font for deterministic results.

**Status:** beta | **License:** Apache-2.0 | **Scan:** MEDIUM (39/100)

## When to use it

Use when converting an image file to ASCII art outside the browser — a command-line or script run that turns a photo, logo, screenshot, or render into text, saved as .txt or rendered to .png/.svg. Trigger on "make ASCII art of this image/photo/cat", "convert this picture/logo to ASCII", "turn this PNG into an ASCII text file for my README", batch-converting a folder of images to ASCII, or any Python/Pillow image-to-ASCII task. Produces sharp, shape-aware output by matching each cell to the glyph whose shape fits best (6D shape vectors + nearest-neighbour, optional contrast enhancement) rather than a naive brightness ramp, and bundles a monospace font for deterministic results. Runs scripts/image_to_ascii.py. Not for ASCII graphics on a web page or in React (use ascii-img-react), not the real-time textmode.js library (use textmode-js), and not figlet-style text banners (this converts images, not words).


## Security

SkillSpector scan `skillspector@a5092dd9b9521ff57a9b53612bb129ce78019002` scored 39/100 (MEDIUM band).

Findings:

- `LP3` (MEDIUM, accepted) — SkillSpector 'MCP Least Privilege' (LP3) on SKILL.md: flags file_read / file_write with no scanner-recognized permissions declaration. Accepted, not fixed — LP3 reads a `permissions` *list*, but the Claude Code skill loader honors `allowed-tools`, not a SkillSpector-style permissions list, so adding one would be loader-ignored scanner-bait. The file I/O is the converter's documented job (read an image, write the .txt/.png/.svg via scripts/image_to_ascii.py), confined to the workspace; external_endpoints is none and the skill makes no network calls.
- `EA3` (LOW, accepted) — SkillSpector 'Excessive Agency / Scope Creep' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font's license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it.
- `EA3` (LOW, accepted) — SkillSpector 'Excessive Agency / Scope Creep' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font's license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it.
- `EA3` (LOW, accepted) — SkillSpector 'Excessive Agency / Scope Creep' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font's license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it.
- `EA3` (LOW, accepted) — SkillSpector 'Excessive Agency / Scope Creep' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font's license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it.

The SARIF report lives at `./report.sarif`.
