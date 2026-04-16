---
name: dev-plan
description: 用于已存在批准后的需求，且在 Codex CLI 会话中开始改代码前需要先得到经过审查的实施计划时
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
