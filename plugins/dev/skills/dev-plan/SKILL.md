---
name: dev-plan
description: Use when approved requirements exist and a Codex CLI session needs a reviewed implementation plan before code changes begin
---

# dev-plan

## Decision Rules
- `ce:plan` is the only plan creator
- choose review depth from implementation-unit count
- route UI-sensitive plans through `plan-design-review`
- do not include implementation code in the plan skill body

## Review Depth / Handoff
| Plan Shape | Required Review | Next |
|---|---|---|
| small: 1-2 implementation units | `plan-eng-review` is mandatory | `$dev-code` after reviewed plan |
| standard: 3-9 implementation units | `plan-eng-review` is mandatory | `$dev-code` after reviewed plan |
| large: 10+ implementation units | `plan-eng-review` is mandatory | `$dev-code` after reviewed plan |
| any UI-sensitive plan | add `plan-design-review` alongside engineering review | `$dev-code` after reviewed plan |
