---
name: dev:design
description: "Use when a requirements doc exists and the work involves UI, visual components, or front-end changes. Detects project design maturity and routes through the right design pipeline. Skip entirely for pure backend work."
---

# Phase 2: Design -- "长什么样"

## Overview

Phase 2 establishes the visual language and interaction patterns. It **detects** project design maturity (no system / has system / has mockups) and **routes** through the right pipeline stage. The anchor artifact is `DESIGN.md`.

Position in workflow: Phase 1 (discover) -> **Phase 2** -> Phase 3 (planning)

## When to Use

- Requirements doc exists and the work involves UI, visual components, or front-end changes

**Skip when:** Pure backend, API-only, infrastructure, or CLI work with no visual surface.

## Scene Detection

Check these signals in order:

**Signal 1: Does `DESIGN.md` exist at repo root?**
- No -> this project has no design system yet -> Route A: Full pipeline
- Yes -> check Signal 2

**Signal 2: Does `approved.json` exist for this feature?**
- Search `~/.gstack/projects/*/designs/` for sessions matching the current feature/branch
- No approved direction -> Route B: Visual exploration
- Yes, but plan lacks design decisions -> Route C: Plan-level review only
- Yes, and plan has design decisions -> SKIP Phase 2

**Signal 3: Is there an existing frontend codebase?**
- Scan for design signals: CSS variables, component libraries, Tailwind config, font imports
- 4+ signals -> `frontend-design` will auto-detect in Phase 4 (no action needed in Phase 2)
- 1-3 signals -> partial system, `design-shotgun` should constrain to existing patterns
- 0 signals -> greenfield, full creative freedom

## Routing

```
Requirements Doc (from Phase 1)
  |
  +-- No DESIGN.md ---------> Route A: design-consultation -> design-shotgun
  |   (no design system)       Create the system, then explore visuals
  |
  +-- Has DESIGN.md, -------> Route B: design-shotgun
  |   no approved.json         Explore visuals within existing system
  |   (system exists,
  |    no visual direction)
  |
  +-- Has DESIGN.md, -------> Route C: plan-design-review (deferred to Phase 3)
  |   has approved.json,       Plan exists but needs design dimension audit
  |   plan lacks design
  |
  +-- Has DESIGN.md, -------> SKIP Phase 2 -> /dev:plan
      has approved.json,
      plan has design decisions
```

## Workflow

1. **Detect scene** using the signals above. Announce:
   - "No design system found -- creating DESIGN.md first."
   - "Design system exists, exploring visual direction for this feature."
   - "Visual direction already approved -- deferring design review to planning phase."

2. **Execute the detected route**

   **Route A**: Run `/gstack-design-consultation` -> output `DESIGN.md` -> then `/gstack-design-shotgun`
   **Route B**: Run `/gstack-design-shotgun` with `DESIGN.md` as constraint
   **Route C**: Note for Phase 3 to run `/gstack-plan-design-review`

3. **REVIEW: Spec Review Loop** (auto-triggered by `design-consultation`)
   - Independent sub-agent adversarial review (5 dimensions: Completeness / Consistency / Clarity / Scope / Feasibility)
   - Score 1-10, fix-and-re-review up to 3 rounds
   - Unresolved issues written to "Reviewer Concerns" section

   **GATE: `DESIGN.md` reviewed + `approved.json` exists + user confirmed direction.**

4. **(Optional)** Run `/gstack-design-html` to generate high-fidelity prototype

5. **Next**: `/dev:plan` (Phase 3)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Phase 1 requirements doc, existing codebase |
| **Output** | `DESIGN.md` (persistent) + `approved.json` (per-feature) |
| **Next** | `/dev:plan` (Phase 3) |

## Key Artifact

`DESIGN.md` is the design anchor -- all downstream skills consume or enforce it:
- `design-shotgun` constrains variant generation
- `plan-design-review` calibrates ratings against it
- `design-html` extracts tokens from it
- `design-review` scores deviations as higher severity
- `frontend-design` detects and follows it automatically in `ce:work`
