# Skill card review — image-to-ascii

Each HUMAN field below needs sign-off: put an x in its checkbox once you
have verified it. `skillcard review` / `make check` blocks until every box
is checked. Regenerating the card with changed content resets this checklist.

fingerprint: sha256:2e728a1a5cb8ad87412a0d480709b00197a7e12c08229a5e775c61751edabe95

- [x] `summary` — Convert an image file to ASCII art from the command line with shape-aware glyph matching (6D shape vectors, not a brightness ramp), output as .txt or a rendered .png/.svg, using a bundled monospace font for deterministic results.
- [x] `triggers` — 6 positive / 3 negative
- [x] `inputs` — ['An image file (PNG/JPG/etc.) plus options: --cols, --out/--format, --invert, --contrast.']
- [x] `output` — {'type': 'ASCII art', 'format': '.txt, .png, or .svg produced by scripts/image_to_ascii.py (a shell invocation)'}
- [x] `dependencies` — ['Pillow', 'python>=3.9']
- [x] `external_endpoints` — none
- [x] `permissions` — network=false shell=true file=true env=false mcp=false
- [x] `status` — beta
- [x] `scan.findings[LP3]` — accepted: "SkillSpector 'MCP Least Privilege' (LP3) on SKILL.md: flags file_read / file_write with no scanner-recognized permissions declaration. Accepted, not fixed — LP3 reads a `permissions` *list*, but the Claude Code skill loader honors `allowed-tools`, not a SkillSpector-style permissions list, so adding one would be loader-ignored scanner-bait. The file I/O is the converter's documented job (read an image, write the .txt/.png/.svg via scripts/image_to_ascii.py), confined to the workspace; external_endpoints is none and the skill makes no network calls."
- [x] `scan.findings[EA3]` — accepted: "SkillSpector 'Excessive Agency / Scope Creep' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font's license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it."
- [x] `scan.findings[EA3]` — accepted: "SkillSpector 'Excessive Agency / Scope Creep' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font's license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it."
- [x] `scan.findings[EA3]` — accepted: "SkillSpector 'Excessive Agency / Scope Creep' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font's license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it."
- [x] `scan.findings[EA3]` — accepted: "SkillSpector 'Excessive Agency / Scope Creep' (EA3, 4x) on assets/DejaVuSansMono-LICENSE.txt (lines 36/85/144/176): matches the legal phrase "INCLUDING BUT NOT LIMITED TO" in the bundled SIL Open Font License boilerplate. False positive — the match is in the font's license *data*, not skill instructions. The .ttf is shipped only for deterministic rendering and its license text must travel with it."
