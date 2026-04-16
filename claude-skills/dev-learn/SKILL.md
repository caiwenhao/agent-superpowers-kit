---
name: dev-learn
description: "Use after solving a significant problem, shipping a feature, or completing a sprint. Detects the trigger type and routes to the right knowledge capture skill: ce:compound for problems, retro for sprints, writing-skills for reusable methods."
---

# Phase 7: Learn -- "学到什么"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、路由宣告均使用中文。
2. **工作区检查。** 知识文档写入 `docs/solutions/` 前确认在正确分支上。
3. **Review 多轮循环。** `ce:compound` Phase 3 的可选领域审查执行修复循环。

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

**Signal 6: Can an existing skill be improved?**
- Same review finding (same category) appeared 3+ times in `learnings.jsonl`
- Same friction point appears in consecutive retro reports
- Upstream submodule (compound-engineering / superpowers / gstack) has new capabilities
- A skill references a tool/skill name that no longer exists
- -> Route E: Skill improvement

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
  +-- [Reusable method found] ----> Route C: superpowers:writing-skills
  |   "always do this",              -> ~/.claude/skills/<name>/SKILL.md
  |   "encode as a skill"
  |
  +-- [Knowledge stale] ----------> Route D: /ce:compound-refresh
  |   "outdated", "contradicts"      -> Updated/merged/deleted docs
  |
  +-- [Skill improvable] ---------> Route E: superpowers:writing-skills (REFACTOR)
  |   repeated findings,             -> Updated SKILL.md + workflow doc
  |   upstream new capabilities,
  |   process friction
  |
  +-- [Nothing novel] ------------> SKIP Phase 7 -> /dev:discover (next item)
```

## Workflow

1. **Detect scene** and announce (中文):
   - "Bug 修复伴随根因分析 -- 记录解决方案。"
   - "迭代结束 -- 运行回顾分析趋势。"
   - "发现可复用模式 -- 用 TDD 创建 skill。"

2. **Execute detected route**

   **Route A: `/ce:compound`** (problem documentation)
   - Parallel sub-agents: Context Analyzer + Solution Extractor + Related Docs Finder
   - Auto-detects track: Bug (Problem->Root Cause->Solution->Prevention) vs Knowledge (Context->Guidance->Why->Examples)
   - Auto-detects overlap with existing docs (5 dimensions, High/Moderate/Low)
   - REVIEW (Optional): domain-specific review auto-triggered by problem type (最多 3 轮):
     - `performance_issue` -> `performance-oracle`
     - `security_issue` -> `security-sentinel`
     - `database_issue` -> `data-integrity-guardian`
   - Selective refresh if new doc contradicts existing docs

   **Route B: `/gstack-retro`** (retrospective)
   - Analyzes: commit frequency, code LOC, test ratios, file hotspots, AI-assisted %
   - Compares vs last retro for trends
   - Per-contributor praise and growth areas

   **Route C: `superpowers:writing-skills`** (skill creation)
   - RED: pressure scenario without skill, document failures
   - GREEN: write minimal skill that fixes those failures
   - REFACTOR: close loopholes, re-test

   **Route D: `/ce:compound-refresh`** (knowledge maintenance)
   - Classify each doc: Keep / Update / Consolidate / Replace / Delete
   - Evidence-based: check if referenced files still exist

   **Route E: `superpowers:writing-skills`** (skill improvement, REFACTOR mode)
   - Analyze gap: which route/rule/signal is missing or outdated
   - For upstream updates: read new SKILL.md/changelog, judge impact on dev:* routing
   - For repeated findings: aggregate from `learnings.jsonl`, locate missing detection signal
   - For friction: trace retro friction points to specific Phase's Scene Detection
   - Update SKILL.md + `docs/ai-coding-workflow.md` in sync
   - Verify: improved skill routes correctly on historical cases from retro

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

## Iron Law

> Knowledge captured now compounds into every future planning and review cycle. Skipping documentation is borrowing from your future self.
