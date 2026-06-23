<!--
Thanks for the PR. Keep it focused: one skill or one concern per PR.
See CONTRIBUTING.md for the ground rules.
-->

## Summary

<!-- One or two sentences. What changes, and why. -->

## Type of change

- [ ] New skill
- [ ] Fix to an existing skill (stale advice, triggering, broken script)
- [ ] Docs only
- [ ] Tooling / CI

## Checklist

- [ ] `make check` passes (lint, the card gate, and the catalog freshness check)
- [ ] If a skill's source changed, its card was rebuilt (`make scan SKILL=…` then
      rebuild + tick `card-review.md`) so `card.json` and `skill-card.md` match
- [ ] `name` matches the folder, and both are kebab-case
- [ ] No secrets committed (references where they live instead)
- [ ] I did NOT hand-edit anything between the catalog's `SKILLS-INDEX` markers

## Notes for the reviewer

<!-- Optional. Anything that helps: a triggering edge case, an accepted MEDIUM
     finding and why you accepted it, a version the skill is now pinned to. -->
