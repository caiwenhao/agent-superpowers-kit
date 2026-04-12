---
name: dev-learn
description: Use when meaningful work is complete and a Codex CLI session should capture reusable knowledge or refresh an existing pattern
---

# dev-learn

## Decision Rules
- solved problem -> `ce:compound`
- stale knowledge -> `ce:compound-refresh`
- reusable method -> `writing-skills`
- no durable learning -> skip and close the loop cleanly

## Exit / Handoff
| Condition | Outcome |
|---|---|
| reusable problem-solving knowledge exists | route to `ce:compound` |
| existing knowledge is stale or contradictory | route to `ce:compound-refresh` |
| the session produced a repeatable workflow or reusable agent behavior | route to `writing-skills` |
| nothing reusable was learned | skip Phase 7 |
