---
name: dev-discover
description: Use when new work is still vague, value is uncertain, or a Codex CLI session needs a requirements artifact before planning
---

# dev-discover

## Decision Rules
- no approved requirements -> stay in discovery
- value unclear -> route to `office-hours`
- idea space unclear -> route to `ce:ideate`
- otherwise -> route to `ce:brainstorm`
- discovery lane uses `ce:brainstorm`; add `document-review` when the requirements artifact needs structured challenge before planning
- user-facing status and gate reporting stays in Chinese

## Exit / Handoff
| Condition | Outcome |
|---|---|
| approved requirements exist | discovery ends after handoff is explicit |
| approved requirements include UI or interaction work | hand off to `$dev-design` |
| approved requirements are non-UI | hand off to `$dev-plan` |
