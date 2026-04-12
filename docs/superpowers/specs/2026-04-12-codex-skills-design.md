# Codex-Native `dev:*` Skills Design

## Overview

This document defines a Codex CLI-native skill system that keeps `dev:*` as the public workflow surface while making the underlying skill implementation fully comply with the `superpowers` meta-skill rules, especially `writing-skills`.

Core decision: `dev:*` remains the user-facing phase vocabulary, but the actual skill names and directories use hyphenated `agentskills.io`-compatible names such as `dev-flow` and `dev-plan`.

## Goals

- Preserve the 7-phase AI coding workflow as the main user mental model.
- Make the skill set native to Codex CLI, not a Claude compatibility shim.
- Keep `dev:*` as a thin orchestration layer over existing `superpowers`, `compound-engineering`, and `gstack` skills.
- Enforce `writing-skills` constraints on naming, descriptions, scope, and testing.
- Default user-visible workflow reporting to Chinese while keeping code, paths, commands, and skill IDs in English.

## Non-Goals

- Rewriting existing lower-level skills such as `ce:work` or `ce:review`.
- Creating a cross-agent abstraction layer for Claude, Codex, and other runtimes.
- Writing the first batch of skill bodies in this document.
- Treating `dev:*` as a heavy workflow monolith that duplicates downstream instructions.

## Design Principles

1. Public invocation and internal skill identity are separate contracts.
2. Each phase skill owns routing, gates, skip logic, and handoff boundaries, not full downstream implementation detail.
3. Artifact- and state-based routing beats intent guessing.
4. Description fields describe only when to load a skill, never the workflow inside the skill.
5. Shared rules should live once at the highest stable layer instead of being copied into every phase skill.
6. Every skill design must be testable with RED baseline scenarios before the skill is written.

## Baseline Failures Observed

The current reference material reveals several violations against `writing-skills`:

| Failure | Why it matters |
|---|---|
| Frontmatter names like `dev:flow` | `writing-skills` requires letters, numbers, and hyphens only |
| Descriptions summarize workflow internals | Models may stop at the description and skip the body |
| Phase skills repeat large workflow details | Creates drift and makes maintenance expensive |
| Claude-oriented and Codex-oriented variants both exist | Duplicate maintenance surface invites divergence |
| No explicit alias contract between `dev:*` and skill names | Invocation and discovery behavior remain ambiguous |

These failures define the minimum scope of the redesign.

## Naming And Alias Contract

### Rule

- User-facing invocation stays `dev:*`.
- Skill directory names and frontmatter `name` fields use hyphenated names.

### Examples

| Public surface | Skill directory | Frontmatter name |
|---|---|---|
| `dev:flow` | `dev-flow/` | `dev-flow` |
| `dev:discover` | `dev-discover/` | `dev-discover` |
| `dev:plan` | `dev-plan/` | `dev-plan` |

### Rationale

This preserves the phase vocabulary users already understand while complying with skill naming rules and keeping discovery predictable.

## Target Layout

```text
.agents/skills/
  dev-flow/
    SKILL.md
  dev-discover/
    SKILL.md
  dev-design/
    SKILL.md
  dev-plan/
    SKILL.md
  dev-code/
    SKILL.md
  dev-verify/
    SKILL.md
  dev-ship/
    SKILL.md
  dev-learn/
    SKILL.md

docs/codex-skills/
  architecture.md
  testing-matrix.md
  alias-contract.md
```

`docs/codex-skills/` is optional supporting documentation. It is not a substitute for concise `SKILL.md` files.

## Thin Orchestration Model

Each `dev-*` skill should do four things:

1. Detect whether the phase applies.
2. Decide whether to enter, skip, resume, or hand back.
3. Invoke the next required lower-level skill(s).
4. Report status and gate transitions in Chinese.

Each `dev-*` skill should not:

- Re-document the full downstream skill body.
- Embed large command manuals.
- Duplicate testing or review doctrine already owned by `superpowers`.
- Introduce parallel abstractions that bypass established lower-level skills.

## First Batch

The first release should contain exactly these eight public phase skills.

### `dev-flow`

- Role: top-level phase router.
- Owns: entry detection, resume logic, skip logic, artifact inspection, phase handoff, GATE behavior.
- Delegates to: the other seven `dev-*` skills.
- Should not: contain detailed downstream instructions for discovery, planning, coding, review, or shipping.

### `dev-discover`

- Role: route ambiguous or fresh work into requirements creation.
- Owns: discovery scene detection and routing to the correct requirements workflow.
- Delegates to: `ce:ideate`, `office-hours`, `ce:brainstorm`, `document-review`.
- Output: approved requirements artifact with stable identifiers.

### `dev-design`

- Role: decide whether UI or design work is required and which design lane to use.
- Owns: design maturity detection and design-phase skip logic.
- Delegates to: `design-consultation`, `design-shotgun`, `plan-design-review`.
- Should not: run for pure backend work.

### `dev-plan`

- Role: produce execution-ready plans from approved requirements.
- Owns: planning entry criteria, review depth selection, and plan handoff gate.
- Delegates to: `ce:plan`, `plan-eng-review`, `plan-design-review`, `autoplan`.
- Output: reviewed plan with implementation units and test scenarios.

### `dev-code`

- Role: execute approved plans or a narrowly scoped bare prompt.
- Owns: execution posture selection and code-phase gate conditions.
- Delegates to: `ce:work`, `test-driven-development`, `systematic-debugging`, `frontend-design`.
- Should not: claim complete quality verification.

### `dev-verify`

- Role: run the full quality gate after implementation.
- Owns: additive verification-layer selection based on diff and risk.
- Delegates to: `ce:review`, `test-browser`, `qa`, `design-review`, `cso`, `benchmark`.
- Output: evidence-based PASS or NEEDS_WORK result.

### `dev-ship`

- Role: move verified work into PR, merge, deploy, and post-deploy verification.
- Owns: delivery-path selection and deployment handoff gate.
- Delegates to: `git-commit-push-pr`, `ship`, `land-and-deploy`, `document-release`.
- Should not: compensate for missing planning or missing verification.

### `dev-learn`

- Role: capture reusable knowledge after meaningful work completes.
- Owns: learning trigger detection and routing to the right knowledge capture lane.
- Delegates to: `ce:compound`, `ce:compound-refresh`, `retro`, `writing-skills`.
- Output: reusable knowledge artifact or explicit skip.

## First-Batch Priority Order

Recommended implementation order:

1. `dev-flow`
2. `dev-discover`
3. `dev-plan`
4. `dev-code`
5. `dev-verify`
6. `dev-ship`
7. `dev-learn`
8. `dev-design`

Rationale:

- `dev-flow` defines the system contract.
- `discover`, `plan`, `code`, `verify`, and `ship` cover the most common CLI development paths.
- `design` is important but more conditional and can follow once the core phase spine is stable.

## Frontmatter Rules

Each skill must follow these rules:

| Field | Rule |
|---|---|
| `name` | Hyphenated only, no colons |
| `description` | Starts with `Use when...` |
| `description` | Describes triggering conditions only |
| `description` | Must not summarize workflow internals |
| `description` | Prefer under 500 characters |

Example:

```yaml
---
name: dev-flow
description: Use when starting a development task, resuming interrupted work, or when the correct workflow phase is unclear in a Codex CLI session
---
```

## Shared Content Rules

To keep the phase skills maintainable:

- Put cross-phase doctrine in one shared place where possible.
- Repeat only the rules that are genuinely phase-specific.
- Reference lower-level skills by skill name, not file path.
- Use `REQUIRED BACKGROUND` and `REQUIRED SUB-SKILL` markers when a downstream skill is mandatory.
- Keep examples minimal and phase-specific.

## RED Test Matrix

Per `writing-skills`, every skill must have a failing baseline before it is written or edited.

### System-Level Baseline Tests

| Skill | RED scenario | Expected failure without good skill |
|---|---|---|
| `dev-flow` | Repo has active plan and dirty branch | Agent restarts from discovery instead of resuming |
| `dev-discover` | User gives vague feature request | Agent jumps to planning or coding too early |
| `dev-design` | Task is pure backend | Agent enters design unnecessarily |
| `dev-design` | Task contains UI changes | Agent skips design entirely |
| `dev-plan` | Requirements doc exists | Agent writes pseudo-code instead of decision-level plan |
| `dev-code` | Plan is approved | Agent writes production code without a failing test or without root-cause analysis for bugs |
| `dev-verify` | Diff touches risky areas | Agent declares success without running evidence-producing checks |
| `dev-ship` | PR has unresolved feedback | Agent tries to deliver anyway |
| `dev-learn` | Significant problem was solved | Agent ends session without capturing reusable knowledge |

### Pressure Types

Each RED scenario should combine at least three pressures where relevant:

- time pressure
- sunk-cost pressure
- authority pressure
- ambiguity pressure
- fatigue pressure
- “just this once” rationalization pressure

## Minimal Skill Template

Every first-batch skill should use a concise template:

1. Overview
2. When to Use
3. Entry Signals
4. Decision Rules
5. Required Sub-Skills
6. Gate / Stop Conditions
7. Common Mistakes

Only add a flowchart if the decision boundary is non-obvious.

## Migration Strategy

### Phase 1

- Freeze the public `dev:*` vocabulary.
- Stop treating colon-based frontmatter names as valid.
- Define alias behavior explicitly.

### Phase 2

- Create `dev-flow` and the first batch of hyphenated skills.
- Move repeated cross-phase doctrine upward or remove it.
- Rewrite descriptions so they describe trigger conditions only.

### Phase 3

- Run RED/GREEN/REFACTOR tests for each skill.
- Remove or archive duplicate Claude-oriented phase copies once Codex-native skills pass.

## Open Decisions Deferred

These are intentionally deferred until the skill-writing phase:

- The exact alias implementation mechanism for `dev:*` invocation.
- Whether shared doctrine belongs in a directory-local `AGENTS.md` or a supporting reference file.
- Whether `dev-design` should ship in the first wave or immediately after.
- Whether supporting documentation under `docs/codex-skills/` should be generated or handwritten.

## Acceptance Criteria

This design is complete when:

- The system has a single public phase vocabulary: `dev:*`.
- All actual skill names are `writing-skills` compliant.
- The first batch is limited to eight thin orchestration skills.
- Each skill has a defined downstream dependency set.
- Each skill has defined RED baseline scenarios before writing.
- No phase skill description summarizes its own internal workflow.

