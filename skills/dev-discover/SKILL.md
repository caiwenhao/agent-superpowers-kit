---
name: dev:discover
description: "Use when starting any new work: a feature idea, vague request, product question, or 'I want to build X'. Detects intent clarity and routes to the right discovery skill, always producing a requirements doc with R-IDs before planning begins."
---

# Phase 1: Discover -- "做什么"

## Overview

Phase 1 is the mandatory entry point for all new work. It **detects** user intent clarity, **routes** to the best discovery skill, and **converges** all paths onto `ce:brainstorm` as the single exit, producing a requirements document with traceable R-IDs (R1, R2, R3...).

Position in workflow: **Phase 1** -> Phase 2 (design) or Phase 3 (planning)

## When to Use

- Starting a new feature, improvement, or product idea
- User describes something to build but scope is unclear
- User wants to explore what is worth building

**Skip when:** An approved requirements doc (`docs/brainstorms/*-requirements.md`) already exists for this work item.

## Scene Detection

Analyze user input to classify intent. Check these signals in order:

**Signal 1: Is there an existing requirements doc?**
- Search `docs/brainstorms/` for `*-requirements.md` matching the topic (within 30 days)
- If found and approved -> SKIP Phase 1, go to `/dev:design` or `/dev:plan`
- If found but incomplete -> RESUME, run `/ce:brainstorm` on existing doc

**Signal 2: Does the user have a direction?**
- No direction detected (keywords: "ideas", "what should I", "improve", "suggest", "don't know what") -> Route A: Ideate first
- Has direction but uncertain about value (keywords: "worth building", "validate", "is this a good idea", "should I", "market") -> Route B: Validate first
- Has direction with clear scope -> Route C or D (see Signal 3)

**Signal 3: How specific is the request?**
- Multi-faceted / cross-cutting / 3+ independent concerns -> Route C: Standard/Deep brainstorm
- Single concern / clear boundary / small scope -> Route D: Lightweight brainstorm

## Routing

```
User Input
  |
  +-- [No direction] -------> Route A: /ce:ideate -> /ce:brainstorm
  |   "give me ideas"
  |   "what should I improve"
  |
  +-- [Has direction,  -----> Route B: /gstack-office-hours -> /ce:brainstorm
  |    uncertain value]
  |   "is this worth building"
  |   "validate my idea"
  |
  +-- [Has direction,  -----> Route C: /ce:brainstorm (Standard/Deep)
  |    multi-faceted]
  |   "add user auth with OAuth and RBAC"
  |
  +-- [Has direction,  -----> Route D: /ce:brainstorm (Lightweight)
      clear & small]
      "add a logout button"
```

All routes converge to `/ce:brainstorm` as the single exit.

## Workflow

1. **Detect scene** using the signals above. Announce the detected route:
   - "Input is exploratory with no clear direction -- starting with ideation."
   - "Input has a direction but needs validation -- running office hours."
   - "Input describes a multi-faceted feature -- starting standard brainstorm."
   - "Input is clear and bounded -- running lightweight brainstorm."

2. **Execute the detected route**

   **Route A**: Run `/ce:ideate` -> user selects direction -> feed into `/ce:brainstorm`
   **Route B**: Run `/gstack-office-hours` -> validated direction -> feed into `/ce:brainstorm`
   **Route C/D**: Run `/ce:brainstorm` directly (scope auto-assessed by ce:brainstorm itself)

3. **REVIEW: `document-review`** (auto-triggered by `ce:brainstorm` Phase 3.5)
   - Multi-persona review: coherence / feasibility / product-lens / design-lens / security-lens / scope-guardian
   - `auto` fixes applied, `present` findings surfaced to user

   **GATE: Requirements doc must exist, document-review complete, user approved.**

4. **Detect next phase** by scanning the approved requirements:
   - Requirements mention UI elements (views, pages, components, styles, layouts, visual) -> `/dev:design`
   - Pure backend / API / infrastructure / CLI -> `/dev:plan`

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | User's idea, question, or feature description |
| **Output** | `docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md` with R-IDs |
| **Next** | `/dev:design` (has UI) or `/dev:plan` (no UI) -- auto-detected |

## Iron Law

> No planning, no implementation, no architecture discussion until the requirements document exists and the user has approved it.
