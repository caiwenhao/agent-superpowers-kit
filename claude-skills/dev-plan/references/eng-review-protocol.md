# Engineering Review Protocol

Condensed from gstack plan-eng-review. Use as the review engine inside dev-plan.

## Execution Steps

1. **Scope challenge** — Before reviewing, answer: What existing code solves this? What is the minimum change? If plan touches 8+ files or 2+ new classes, STOP and challenge complexity.
2. **Architecture review** — System design, coupling, data flow, scaling, security, failure scenarios. One issue per question. STOP after each.
3. **Code quality review** — DRY violations, error handling gaps, over/under-engineering, stale diagrams. One issue per question. STOP after each.
4. **Test review** — Trace every codepath, diagram branches, map coverage gaps, add missing tests to plan. Produce ASCII coverage diagram.
5. **Performance review** — N+1 queries, memory, caching, slow paths. One issue per question. STOP after each.
6. **Outputs** — Produce NOT-in-scope list, what-already-exists list, failure modes, completion summary.

## Review Dimensions

| Dimension | What to evaluate |
|-----------|-----------------|
| Architecture | Component boundaries, dependency graph, data flow, scaling, SPOFs, security |
| Data flow | Input sources, transforms, outputs, what fails at each step |
| Edge cases | Null/empty/invalid inputs, concurrency, timeouts, stale data, boundary values |
| Test coverage | Every branch tested? Unit vs E2E decision? Regression rule enforced? |
| Performance | N+1 queries, memory allocation, caching opportunities, algorithmic complexity |
| Code quality | DRY, error handling, explicit over clever, right-sized abstractions |

## Scoring Rubric (Test Quality)

- 3 stars: Tests behavior with edge cases AND error paths
- 2 stars: Tests correct behavior, happy path only
- 1 star: Smoke test / existence check / trivial assertion

## Issue Classification

| Priority | Meaning | Action |
|----------|---------|--------|
| P0 | Security hole, data loss, silent corruption | Block. Fix before proceeding. |
| P1 | Bug that users will hit on common paths | Fix in this PR. |
| P2 | Edge case bug or degraded experience | Fix in this PR if cheap, else TODO. |
| P3 | Code smell, minor DX issue, future risk | TODO with context. Defer. |

## Fix-or-Defer Decision Framework

Fix now: P0/P1, or fix < 30 min CC time and contained to PR scope, or deferring creates regression.

Defer (TODO with full context): P2/P3 expanding scope, touches unrelated modules, or needs unmade design decisions.

Never defer without context. A TODO must include: what, why, pros, cons, dependencies.

## Interactive Walkthrough Structure

For each issue found:
1. State the problem with file/line reference and confidence (1-10)
2. Explain concrete impact (what breaks, who sees it, what is lost)
3. Present 2-3 options with effort estimate (human time / CC time)
4. Give opinionated recommendation tied to engineering preference
5. STOP. Wait for user decision before proceeding.

One issue per question. Never batch. Never auto-decide.

## Opinionated Recommendations Pattern

Every recommendation must:
- Name the preferred option explicitly
- State WHY in one sentence tied to a principle (DRY, explicit > clever, minimal diff, test coverage)
- Include effort on both scales: human team time vs CC time
- Flag when the "complete" option costs only marginally more with CC (recommend complete)
- Acknowledge when options differ in kind vs coverage (no fake completeness scores)

## Confidence Calibration

| Score | Meaning |
|-------|---------|
| 9-10 | Verified by reading specific code. Concrete bug demonstrated. |
| 7-8 | High confidence pattern match. Very likely correct. |
| 5-6 | Moderate. Could be false positive. Show with caveat. |
| 3-4 | Low confidence. Suppress from main report. |
| 1-2 | Speculation. Only report if P0 severity. |

Format: `[P{n}] (confidence: N/10) file:line — description`
