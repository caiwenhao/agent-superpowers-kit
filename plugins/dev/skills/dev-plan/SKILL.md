---
name: dev-plan
description: Use when approved requirements exist and a Codex CLI session needs a reviewed implementation plan before code changes begin
---

# dev-plan

## Decision Rules
- `ce:plan` is the only plan creator
- `plan-eng-review` is mandatory before handoff
- large plans add `autoplan`
- UI-sensitive plans add `plan-design-review`
- do not include implementation code in the plan skill body
- user-facing status and gate reporting stays in Chinese

## Review Depth / Handoff
| Plan Shape | Required Review | Next |
|---|---|---|
| small: 1-2 implementation units | `plan-eng-review` is mandatory | `$dev-code` after reviewed plan |
| standard: 3-9 implementation units | `plan-eng-review` is mandatory | `$dev-code` after reviewed plan |
| large: 10+ implementation units | `autoplan` plus mandatory `plan-eng-review` | `$dev-code` after reviewed plan |
| any UI-sensitive plan | add `plan-design-review` alongside engineering review | `$dev-code` after reviewed plan |
