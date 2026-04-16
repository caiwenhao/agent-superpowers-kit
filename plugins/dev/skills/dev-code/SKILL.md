---
name: dev-code
description: 用于已有批准计划，或在 Codex CLI 会话中一个范围很小的裸提示已经可以直接进入实现时
---

# Phase 4: Code

Use `$dev-code` only when the task is ready for implementation.

## Decision Rules
- approved plan -> route to `ce:work`
- very small bare prompt -> allow inline execution
- bug work -> require `systematic-debugging` before fix
- test-first or behavior lock-in work -> add `test-driven-development`
- UI implementation or visual change -> add `frontend-design`
- user-facing status and gate reporting stays in Chinese

## Conditional Delegates
- `ce:work` is the default implementation lane when a reviewed plan exists.
- `systematic-debugging` comes first for bugs, regressions, or failing behavior.
- `test-driven-development` is additive when the change needs failing-test lock-in before edits.
- `frontend-design` is additive for UI implementation or meaningful visual work.

## Exit Criteria

- The requested implementation is complete.
- Local verification for touched code has been run.
- The work is ready to move to `$dev-verify`.
