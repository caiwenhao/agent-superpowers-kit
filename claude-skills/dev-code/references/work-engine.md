# Work Engine — Execution Protocol

## Phase 0: Input Triage

1. Determine input type:
   - **Plan document** (file path to existing plan/spec) → skip to Phase 1.
   - **Bare prompt** (description of work) → scan work area, find affected files and their tests, note local patterns.

2. Assess complexity and route:

| Complexity | Signals | Action |
|---|---|---|
| **Trivial** | 1-2 files, no behavioral change | Implement directly — no task list, no execution loop. Apply Test Discovery if touching behavior-bearing code |
| **Small/Medium** | Clear scope, under ~10 files | Build task list from discovery → Phase 1 |
| **Large** | Cross-cutting, 10+ files, auth/payments/migrations | Inform user this benefits from brainstorm/plan. Honor their choice. If proceeding, build task list → Phase 1 |

## Phase 1: Task List Creation

1. Read plan completely. Extract from: Implementation Units, Work Breakdown, Requirements, Files, Test Scenarios, Verification.
2. Check each unit's `Execution note` (test-first, characterization-first).
3. Check `Deferred to Implementation` / `Implementation-Time Unknowns` — resolve during execution.
4. Check `Scope Boundaries` — explicit non-goals.
5. Create tasks via platform task tracker (`TaskCreate`/`TaskUpdate`/`TaskList` in Claude Code, `update_plan` in Codex).
6. **U-ID anchoring**: preserve unit U-IDs as task subject prefixes (e.g., "U3: Add parser coverage").
7. Carry `Execution note`, `Patterns to follow`, and `Verification` field into each task.
8. Include inter-task dependencies. Prioritize by execution order.

## Phase 1b: Execution Strategy Selection

| Strategy | When |
|---|---|
| **Inline** | 1-2 tasks, or tasks needing user interaction. Default for bare-prompt work |
| **Serial subagents** | 3+ tasks with dependencies. Each gets fresh context window focused on one unit |
| **Parallel subagents** | 3+ tasks passing Parallel Safety Check |

**Parallel Safety Check:**
1. Build file-to-unit mapping from every unit's `Files:` section.
2. Check intersection — any path in 2+ units = overlap.
3. Overlap found + no worktree isolation → downgrade to serial.
4. Overlap found + worktree isolation available → parallel safe (overlap surfaces as merge conflict).

**Subagent dispatch payload** (per unit):
- Full plan file path
- Unit's Goal, Files, Approach, Execution note, Patterns, Test scenarios, Verification
- Resolved deferred questions relevant to that unit
- Instruction to check test scenario completeness before writing tests

**After each serial subagent completes:**
1. Review diff — verify scope matches unit's `Files:` list.
2. Run relevant test suite.
3. If tests fail, fix before dispatching next unit.
4. Update task list.

**After parallel batch completes (worktree mode):**
1. Merge each branch in dependency order.
2. On conflict: `git merge --abort`, re-dispatch conflicting unit serially.
3. Run tests after each merge.
4. Clean up worktrees and branches.

## Phase 2: Task Execution Loop

```
while (tasks remain):
  - Mark task in-progress
  - If unit's work already present and matches plan intent → verify, mark complete, move on
  - Read referenced files; find similar patterns in codebase
  - Run Test Discovery (below)
  - Implement following existing conventions
  - Add/update/remove tests to match changes
  - Run System-Wide Test Check (below)
  - Run tests
  - Mark task completed
  - Evaluate incremental commit opportunity
```

**Execution note honor:**
- Test-first: write failing test before implementation. Do not write test + impl in same step.
- Characterization-first: capture existing behavior before changing it.
- No note: proceed pragmatically.

## Test Discovery Protocol

Before changing any file:
1. Search for test/spec files that import, reference, or share naming patterns with the implementation file.
2. Start with plan-specified test scenarios, then check for additional coverage.
3. New behavior → new tests. Changed behavior → updated tests. Deleted behavior → removed tests.

**Test Scenario Completeness** — supplement if plan's scenarios are vague or missing:

| Category | When applicable | Derivation |
|---|---|---|
| Happy path | Always for feature-bearing units | Unit's Goal and Approach |
| Edge cases | Meaningful boundaries exist | Boundary values, empty/nil, concurrency |
| Error/failure paths | Validation, external calls, permissions | Invalid inputs, auth denials, downstream failures |
| Integration | Crosses layers (callbacks, middleware) | Cross-layer chain exercised without mocks |

## System-Wide Test Check

Before marking a task done, answer:

1. **What fires when this runs?** Trace callbacks, middleware, observers, event handlers two levels out.
2. **Do tests exercise the real chain?** Write at least one integration test with real objects through full callback/middleware chain. No mocks for interacting layers.
3. **Can failure leave orphaned state?** If state persists before an external call, test that failure cleans up or retry is idempotent.
4. **What other interfaces expose this?** Grep for method/behavior in related classes. Add parity now.
5. **Do error strategies align across layers?** Verify rescue list matches what lower layer actually raises.

**Skip when:** leaf-node change with no callbacks, no state persistence, no parallel interfaces.

## Incremental Commits

| Commit when | Do not commit when |
|---|---|
| Logical unit complete | Small part of larger unit |
| Tests pass + meaningful progress | Tests failing |
| About to switch contexts | Purely scaffolding with no behavior |
| About to attempt risky changes | Would need "WIP" message |

Stage only files related to the logical unit. Use conventional commit messages derived from unit Goal.
