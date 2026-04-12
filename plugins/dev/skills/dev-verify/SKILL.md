---
name: dev-verify
description: Use when implementation is complete and a Codex CLI session needs evidence-based quality verification before delivery
---

# Phase 5: Verify

Use `$dev-verify` as the delivery gate after implementation is done.

## Decision Rules
- `ce:review` is always the core gate
- additive lanes are risk-based: `test-browser`, `qa`, `design-review`, `cso`, `benchmark`
- no pass claim without executed evidence
- user-facing status and gate reporting stays in Chinese

## Verification Additions
- `ce:review` is always first.
- Add `test-browser` or `qa` for browser-facing flows.
- Add `design-review` for visual-risk changes.
- Add `cso` for security-sensitive work.
- Add `benchmark` for performance-risk changes.

## Exit Criteria

- Review findings are resolved or explicitly surfaced.
- Verification evidence has been executed and read.
- The change is ready to move to `$dev-ship`.
