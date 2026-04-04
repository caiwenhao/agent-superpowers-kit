---
name: dev:plan
description: "Use when a requirements doc exists and it is time to create an implementation plan. Detects scope to select review depth: autoplan for large features, plan-eng-review for ordinary work. Always uses ce:plan as the sole plan creator."
---

# Phase 3: Plan -- "怎么做"

## Overview

Phase 3 transforms requirements into an executable plan. `ce:plan` is the sole creator (decisions, not code). The skill **detects** plan scope and **auto-selects** the right review depth. Plans produce Implementation Units, Requirements Trace, and Test Scenarios consumed by `ce:work` in Phase 4.

Position in workflow: Phase 2 (design) -> **Phase 3** -> Phase 4 (implementation)

## When to Use

- Requirements doc exists (`docs/brainstorms/*-requirements.md`)
- Work is non-trivial (more than a one-file fix)

**Skip when:** Plan already exists and has been reviewed for this work item.

## Scene Detection

**Signal 1: Does a plan already exist?**
- Search `docs/plans/` for plans matching the topic (within 30 days)
- If found with `status: active` and REVIEW REPORT present -> SKIP, go to `/dev:code`
- If found with `status: active` but no REVIEW REPORT -> resume at review step
- If found with `status: completed` -> SKIP or create new plan (ask user)

**Signal 2: Does `DESIGN.md` exist? (from Phase 2)**
- Yes -> `ce:plan` will reference design tokens; `plan-design-review` should run
- No -> skip design review dimension

**Signal 3: Plan scope (auto-detected by `ce:plan` after creating the plan)**
- Count Implementation Units produced:
  - 1-2 units -> Small scope
  - 3-9 units -> Standard scope
  - 10+ units -> Large scope
- Check if units touch developer-facing surfaces (API, CLI, SDK, docs):
  - Yes -> add DX review

## Routing

### Plan Creation (always the same)

`/ce:plan` -- parallel research sub-agents, R-ID trace, Implementation Units, Test Scenarios.

### Review Depth (auto-selected after plan creation)

```
Plan created by ce:plan
  |
  +-- 10+ Implementation Units ---------> autoplan (CEO + Design + Eng + DX)
  |   (large/cross-cutting)
  |
  +-- 3-9 Units ------------------------> plan-eng-review (required)
  |   (standard)                           + plan-design-review (if DESIGN.md exists)
  |
  +-- 1-2 Units ------------------------> plan-eng-review only
  |   (small)
  |
  +-- Units touch API/CLI/SDK/docs -----> + plan-devex-review (additive)
      (developer-facing)
```

## Workflow

1. **Detect scene** using Signal 1. Announce:
   - "Found existing plan, resuming at review step."
   - "No existing plan -- creating from requirements doc."

2. **Run `/ce:plan`** with requirements doc path
   - Parallel research: repo-research, learnings, best-practices, framework-docs
   - Output: `docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`
   - Scope auto-classified: Lightweight / Standard / Deep

3. **REVIEW (Layer 1): `document-review`** (auto-triggered by `ce:plan` Phase 5)
   - Multi-persona plan document review: coherence / feasibility / scope-guardian

   **GATE: Plan file exists and passes document-review.**

4. **Detect review depth** from plan's Implementation Unit count (Signal 3). Announce:
   - "Plan has 12 units -- running full autoplan review pipeline."
   - "Plan has 5 units with UI -- running eng + design review."
   - "Plan has 2 units -- running eng review only."

5. **REVIEW (Layer 2): Multi-perspective plan review** (auto-selected)
   - Large: `/gstack-autoplan` (CEO -> Design -> Eng -> DX, serial)
   - Standard: `/gstack-plan-eng-review` (required gate) + `/gstack-plan-design-review` (if UI)
   - Small: `/gstack-plan-eng-review` only
   - Developer-facing: + `/gstack-plan-devex-review`

   **GATE: GSTACK REVIEW REPORT in plan file. `plan-eng-review` CLEARED.**

6. **Next**: `/dev:code` (Phase 4)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Phase 1 requirements doc path, Phase 2 `DESIGN.md` (if exists) |
| **Output** | `docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md` with R-Trace + Impl Units |
| **Next** | `/dev:code` (Phase 4) |

## Iron Law

> Plans resolve decisions, not code. The implementer starts confidently without the plan writing code for them.
