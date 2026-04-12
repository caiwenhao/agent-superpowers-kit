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

## Exit / Handoff
| Condition | Outcome |
|---|---|
| approved requirements exist | discovery ends |
| approved requirements include UI or interaction work | hand off to `$dev-design` |
| approved requirements are non-UI | hand off to `$dev-plan` |
