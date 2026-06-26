.PHONY: lint index readmes scorecards check tools cards scan

# Every real skill: a SKILL.md, minus the template and any vendored mirror.
SKILL_DIRS := $(shell find skills -name SKILL.md -not -path '*/_TEMPLATE/*' -not -path '*/vendor/*' -exec dirname {} \;)
# Scratch dir (gitignored): the fresh gate-input scan and the drift-check build
# dirs live here, OUTSIDE the skill dirs. The committed scan.json is a FROZEN
# build input that lives in each skill dir; scan_skill.py excludes it from the
# scan surface, so SkillSpector never re-scans its own output.
SCAN_DIR := .skillcheck

lint:
	python3 scripts/lint_skills.py

index:
	python3 scripts/build_index.py

# Regenerate every README's card-derived region: the root catalog + badges, the
# per-category tables, and the per-skill badge/triggers/metrics blocks. All of it
# reads card.json, so it is safe to re-run; `make check` verifies it is current.
readmes:
	python3 scripts/build_index.py
	python3 scripts/render_skill_readmes.py

# Render every carded skill's SVG scorecard + the root rollup, and embed them in
# the READMEs. Textual renders headless to a deterministic SVG, so committed
# scorecards do not churn. The SVGs land in assets/ (NOT beside the card, which
# would move its content_hash). This is an asset step, kept OUT of `make check`'s
# correctness gate; CI regenerates and diffs as a drift guard. Needs the
# scorecard extra (`make tools` installs it).
scorecards:
	python3 scripts/build_scorecards.py

# Install the vendored Califa tooling (skillcard) + SkillSpector + the scorecard
# renderer into the active environment. Run once before `make check`; CI runs it
# as its own step.
tools:
	python3 -m pip install -e "tooling/califa[scan,scorecard]"

# For every skill: scan its text surface and gate the report. For carded skills,
# also (a) schema/hash-validate the committed card, (b) rebuild the card from its
# committed inputs into a scratch dir and prove it still matches what is checked
# in — no silent drift — and (c) confirm the human review sign-off. The rebuild
# reads the FROZEN committed scan.json (via --report), so it is byte-identical;
# the fresh scan only feeds the gate and the SARIF. Policy (Califa SPEC.md §E):
# HIGH/CRITICAL (or any CRITICAL-severity finding) always fails; a carded skill
# must accept+note every MEDIUM finding; an un-carded MEDIUM warns while the
# library is carded up.
cards:
	@set -e; mkdir -p $(SCAN_DIR); for d in $(SKILL_DIRS); do \
		echo ">> $$d"; \
		key=$$(echo "$$d" | tr '/' '_'); \
		rm -f "$$d/report.sarif"; \
		if [ -f "$$d/card.json" ]; then \
			python3 scripts/scan_skill.py "$$d" --json "$(SCAN_DIR)/$$key.json" --sarif "$$d/report.sarif"; \
			python3 -m skillcard.cli gate "$(SCAN_DIR)/$$key.json" --card "$$d/card.json"; \
			python3 -m skillcard.cli validate "$$d"; \
			rm -rf "$(SCAN_DIR)/build_$$key"; \
			python3 -m skillcard.cli build "$$d" --report "$$d/scan.json" -o "$(SCAN_DIR)/build_$$key" >/dev/null || true; \
			diff "$(SCAN_DIR)/build_$$key/card.json" "$$d/card.json" || { echo "DRIFT: $$d/card.json differs from a fresh build"; exit 1; }; \
			diff "$(SCAN_DIR)/build_$$key/skill-card.md" "$$d/skill-card.md" || { echo "DRIFT: $$d/skill-card.md differs from a fresh build"; exit 1; }; \
			python3 -m skillcard.cli review "$$d"; \
		else \
			python3 scripts/scan_skill.py "$$d" --json "$(SCAN_DIR)/$$key.json"; \
			python3 -m skillcard.cli gate "$(SCAN_DIR)/$$key.json" --warn-medium-without-card; \
		fi; \
	done

# Refresh the FROZEN committed scan.json for ONE skill after its source surface
# changes, then rebuild + re-tick card-review.md + commit. `make check` never
# regenerates scan.json (its scanned_at date lands in the card), which is what
# keeps rebuilds byte-identical. Usage: make scan SKILL=skills/tui/ratatui
scan:
	@test -n "$(SKILL)" || { echo "usage: make scan SKILL=<skill_dir>"; exit 2; }
	python3 scripts/scan_skill.py "$(SKILL)" --json "$(SKILL)/scan.json" --sarif "$(SKILL)/report.sarif"
	@echo ">> wrote $(SKILL)/scan.json — now: python3 -m skillcard.cli build $(SKILL); tick card-review.md; commit"

check: lint cards
	python3 scripts/build_index.py --check
	python3 scripts/render_skill_readmes.py --check
