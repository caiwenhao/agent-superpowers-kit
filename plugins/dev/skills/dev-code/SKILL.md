---
name: dev-code
description: Use when an approved plan exists or a very small bare prompt is ready for implementation in a Codex CLI session
---

# Phase 4: Code

Use `$dev-code` only when the task is ready for implementation.

## Decision Rules
- approved plan -> route to `ce:work`
- very small bare prompt -> allow inline execution
- bug work -> require `systematic-debugging` before fix
- implementation notes may trigger `test-driven-development`

## Execution Posture

- Default to `ce:work` when a plan is already approved. Let it own execution strategy rather than re-planning inside this phase.
- Inline execution is only for small, self-contained work that does not need a separate planning pass.
- If the task is a bug, regression, or failing behavior report, run `systematic-debugging` first and only then implement the fix.
- If the plan or implementation notes call for test-first work, or the change needs behavior lock-in before edits, use `test-driven-development`.

## Exit Criteria

- The requested implementation is complete.
- Local verification for touched code has been run.
- The work is ready to move to `$dev-verify`.
