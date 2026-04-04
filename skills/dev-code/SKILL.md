---
name: dev:code
description: "Use when a reviewed plan exists and it is time to write code. Routes through ce:work, which detects plan complexity and auto-selects execution strategy (inline, serial agents, parallel agents, or swarm)."
---

# Phase 4: Code -- "写代码"

## Overview

Phase 4 executes the plan. The single entry point is `ce:work`, which **detects** plan complexity and **auto-selects** the best execution strategy. Auxiliary skills are **auto-triggered** by context signals -- not by the user.

Position in workflow: Phase 3 (planning) -> **Phase 4** -> Phase 5 (verification)

## When to Use

- A reviewed plan exists (`docs/plans/*.md`)
- Or: a bare prompt describes small, clear work

**Never skip Phase 4.**

## Scene Detection (performed by `ce:work` internally)

**Signal 1: Is there a plan file?**
- No plan file, no bare prompt -> STOP, return to `/dev:plan`
- No plan file, has bare prompt -> `ce:work` assesses complexity:
  - Trivial (1-2 files) -> proceed inline
  - Large (10+ files, cross-cutting) -> recommend `/dev:discover` + `/dev:plan` first

**Signal 2: Plan complexity (auto-detected from Implementation Units)**

| Detected Signal | Auto-selected Strategy |
|---|---|
| 1-2 files, no behavioral change | Direct inline |
| < 10 files, clear scope | Serial task list |
| 3+ units with sequential dependencies | Serial sub-agents |
| 3+ units with independent units (no shared files) | Parallel sub-agents |
| 10+ units needing inter-agent coordination | Swarm (Agent Teams) |

**Signal 3: Execution posture (auto-detected from plan content)**

| Detected Signal | Auto-triggered Skill |
|---|---|
| Implementation Unit has `Execution note: test-first` | `test-driven-development` (RED-GREEN-REFACTOR) |
| Implementation Unit has `Execution note: characterization-first` | Characterization tests before changes |
| Implementation Unit has `Execution note: external-delegate` | Codex delegation mode |
| Bug encountered during implementation | `systematic-debugging` / `investigate` |
| Multiple independent test failures | `dispatching-parallel-agents` |
| Files in `views/`, `components/`, `*.tsx`, `*.css` touched | `frontend-design` (auto-detects DESIGN.md) |
| Plan references a GitHub Issue | `reproduce-bug` |

## Workflow

1. **`ce:work` detects scene** and announces:
   - "Plan has 5 units with 2 independent -- using parallel sub-agents for units 1-2, then serial for 3-5."
   - "Bare prompt, 2 files affected -- proceeding inline."
   - "Plan unit 3 is tagged test-first -- will use TDD for that unit."

2. **`ce:work` executes** with auto-selected strategy
   - Per task: Implement -> Test Discovery -> System-Wide Test Check -> Incremental commit
   - Every 2-3 units: Simplify pass (cross-unit dedup)

3. **REVIEW: `ce:review mode:autofix`** (auto-triggered by `ce:work` Phase 3)
   - Tier 2 (default): 20+ persona parallel review, safe_auto fixes, R-ID trace
   - Tier 1 (only when ALL four: purely additive + single concern + pattern-following + plan-faithful)
   - Passes `plan:<path>` for requirements verification

   **GATE: All tasks complete. Tests pass. Review applied. Residual todos recorded.**

4. **Next**: `/dev:verify` (Phase 5)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Plan file path from Phase 3 (or bare prompt for small work) |
| **Output** | Committed code, passing tests, ce:review autofix applied |
| **Next** | `/dev:verify` (Phase 5) |

## Iron Laws

- **No failing test, no production code**
- **No root cause, no fix**
- **3 fix failures: stop and question the architecture**
