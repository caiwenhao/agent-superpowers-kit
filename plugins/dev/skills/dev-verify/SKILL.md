---
name: dev-verify
description: Use when implementation is complete and a Codex CLI session needs evidence-based quality verification before delivery
---

# Phase 5: Verify

Use `$dev-verify` as the delivery gate after implementation is done.

## Decision Rules
- `ce:review` is always the core gate
- additive review layers depend on diff scope and risk
- no pass claim without executed evidence

## Verification Posture

- Start with `ce:review` for every completed implementation. This phase is not optional.
- Add review layers only when the diff warrants them, such as security, API, performance, migration, UI, or browser-focused checks.
- Run the concrete commands that prove the change is ready: diagnostics, tests, typecheck, build, or other directly relevant verification.
- If any review or verification step fails, return to implementation, fix the issue, and rerun the gate.

## Exit Criteria

- Review findings are resolved or explicitly surfaced.
- Verification evidence has been executed and read.
- The change is ready to move to `$dev-ship`.
