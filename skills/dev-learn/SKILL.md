---
name: dev:learn
description: "Use after solving a significant problem, shipping a feature, or completing a sprint. Detects the trigger type and routes to the right knowledge capture skill: ce:compound for problems, retro for sprints, writing-skills for reusable methods."
---

# Phase 7: Learn -- "学到什么"

## Overview

Phase 7 is the compound interest phase. It **detects** what just happened and **routes** to the right knowledge capture mechanism. Knowledge captured here is **automatically injected** into future Phase 3 planning and Phase 5 review via learnings-researcher.

Position in workflow: Phase 6 (ship) -> **Phase 7** -> Phase 1 (next work item, closes the loop)

## When to Use

- Just solved a hard bug or complex problem
- Shipped a feature and want to document decisions
- End of sprint / weekly review
- Discovered a reusable cross-project pattern

**Skip when:** Trivial change with nothing novel learned.

## Scene Detection

Analyze the conversation history and recent git activity to classify the trigger:

**Signal 1: Was a problem just solved?**
- Conversation contains debugging/investigation (keywords: "fixed", "root cause", "the issue was", "resolved", "that worked")
- Recent commits include `fix:` prefix
- -> Route A: Document the problem

**Signal 2: Was a feature just shipped?**
- Phase 6 just completed (PR merged, deploy verified)
- Recent commits include `feat:` prefix
- -> Route A (if non-trivial decisions were made) or skip (if straightforward)

**Signal 3: Is it end of sprint/week?**
- User explicitly mentions "retro", "weekly", "sprint review", "what did we do"
- -> Route B: Retrospective

**Signal 4: Was a reusable method discovered?**
- User mentions "this pattern works for any project", "we should always do this", "encode this as a skill"
- -> Route C: Write a skill

**Signal 5: Does the knowledge base feel stale?**
- User mentions "outdated", "stale", "contradicts", "wrong docs"
- `docs/solutions/` has files referencing deleted code paths
- -> Route D: Refresh

## Routing

```
Completed work
  |
  +-- [Problem solved] -----------> Route A: /ce:compound
  |   "fixed", "root cause",        -> docs/solutions/<category>/<slug>.md
  |   "the issue was"
  |
  +-- [Sprint/week end] ----------> Route B: /gstack-retro
  |   "retro", "weekly review"       -> Retro report + trend snapshot
  |
  +-- [Reusable method found] ----> Route C: writing-skills
  |   "always do this",              -> ~/.claude/skills/<name>/SKILL.md
  |   "encode as a skill"
  |
  +-- [Knowledge stale] ----------> Route D: /ce:compound-refresh
  |   "outdated", "contradicts"      -> Updated/merged/deleted docs
  |
  +-- [Nothing novel] ------------> SKIP Phase 7 -> /dev:discover (next item)
```

## Workflow

1. **Detect scene** and announce:
   - "Bug fix with root cause analysis -- documenting the solution."
   - "Sprint ended -- running retrospective with trend analysis."
   - "Reusable pattern detected -- creating a skill with TDD."

2. **Execute detected route**

   **Route A: `/ce:compound`** (problem documentation)
   - Parallel sub-agents: Context Analyzer + Solution Extractor + Related Docs Finder
   - Auto-detects track: Bug (Problem->Root Cause->Solution->Prevention) vs Knowledge (Context->Guidance->Why->Examples)
   - Auto-detects overlap with existing docs (5 dimensions, High/Moderate/Low)
   - REVIEW (Optional): domain-specific review auto-triggered by problem type:
     - `performance_issue` -> `performance-oracle`
     - `security_issue` -> `security-sentinel`
     - `database_issue` -> `data-integrity-guardian`
   - Selective refresh if new doc contradicts existing docs

   **Route B: `/gstack-retro`** (retrospective)
   - Analyzes: commit frequency, code LOC, test ratios, file hotspots, AI-assisted %
   - Compares vs last retro for trends
   - Per-contributor praise and growth areas

   **Route C: `writing-skills`** (skill creation)
   - RED: pressure scenario without skill, document failures
   - GREEN: write minimal skill that fixes those failures
   - REFACTOR: close loopholes, re-test

   **Route D: `/ce:compound-refresh`** (knowledge maintenance)
   - Classify each doc: Keep / Update / Consolidate / Replace / Delete
   - Evidence-based: check if referenced files still exist

3. **Verify knowledge is discoverable**
   - `docs/solutions/`: YAML frontmatter searchable? `AGENTS.md`/`CLAUDE.md` points to it?
   - `learnings.jsonl`: entry written by gstack/learn (automatic)?

4. **Next**: `/dev:discover` (Phase 1) -- closes the loop

## Knowledge Feedback Loop

```
Phase 4 (ce:work) -- solve problem --> Phase 7 (ce:compound) -- docs/solutions/
                                                                      |
Phase 3 (ce:plan) <-- learnings-researcher auto-searches -------------+
Phase 5 (ce:review) <-- learnings-researcher always-on ---------------+
All gstack skills <-- preamble auto-searches learnings.jsonl ---------+
```

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Completed work (shipped feature, resolved bug, finished sprint) |
| **Output** | `docs/solutions/*.md`, `learnings.jsonl`, optional `SKILL.md` |
| **Next** | `/dev:discover` (Phase 1) -- closes the loop |

## Dual-Layer Architecture

| Layer | Mechanism | Granularity | Trigger |
|---|---|---|---|
| `gstack/learn` | Automatic, passive | One-line insight | Every gstack skill completion |
| `ce:compound` | Manual, active | Full document | Explicit invocation after solving a problem |

Knowledge is not just recorded -- it is automatically injected into future planning and review. That is what makes it compound.
