---
name: dev-discover
description: "Use when starting any new work: a feature idea, vague request, product question, or 'I want to build X'. Detects intent clarity and routes to the right discovery skill, always producing a requirements doc with R-IDs before planning begins."
---

# Phase 1: Discover -- "做什么"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、路由宣告均使用中文。
2. **工作区检查优先。** 创建文档前确认在 worktree/feature branch 中，否则先创建工作区。
3. **Review 多轮循环。** `document-review` 执行"审查->修复->再审查"循环，直到零 P0/P1 或达到 3 轮上限。

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

1. **Detect scene** using the signals above. Announce the detected route (中文):
   - "输入是探索性的，没有明确方向 -- 先进行创意发散。"
   - "输入有方向但需要验证价值 -- 运行 Office Hours。"
   - "输入描述了一个多面向的功能 -- 启动标准头脑风暴。"
   - "输入清晰且范围小 -- 运行轻量头脑风暴。"

2. **Execute the detected route**

   **Route A**: Run `/ce:ideate` -> user selects direction -> feed into `/ce:brainstorm`
   **Route B**: Run `/gstack-office-hours` -> validated direction -> feed into `/ce:brainstorm`
   **Route C/D**: Run `/ce:brainstorm` directly (scope auto-assessed by ce:brainstorm itself)

3. **REVIEW: `document-review` 多轮循环** (内嵌在 `ce:brainstorm` Phase 3.5)
   - 多人格并行审查: coherence / feasibility / product-lens / design-lens / security-lens / scope-guardian
   - `auto` 修复自动应用，`present` 发现交用户判断
   - **循环**: 审查 -> 修复 -> 再审查，直到零 P0/P1 或 3 轮上限或连续两轮发现相同

   **GATE: 需求文档必须存在，document-review 通过（零 P0/P1），用户批准。**

4. **Detect next phase** by scanning the approved requirements (中文宣告):
   - 需求涉及 UI (views, pages, components, styles, layouts, visual) -> `/dev:design`
   - 纯后端 / API / 基础设施 / CLI -> `/dev:plan`

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | User's idea, question, or feature description |
| **Output** | `docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md` with R-IDs |
| **Next** | `/dev:design` (has UI) or `/dev:plan` (no UI) -- auto-detected |

## Iron Law

> No planning, no implementation, no architecture discussion until the requirements document exists and the user has approved it.
