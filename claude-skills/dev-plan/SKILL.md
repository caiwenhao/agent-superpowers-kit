---
name: dev-plan
description: "Use when a requirements doc exists and it is time to create an implementation plan. Detects scope to select review depth: autoplan for large features, plan-eng-review for ordinary work. Always uses ce:plan as the sole plan creator."
---

<SUPERVISE-CHECK>
执行前自检（Codex 环境必读，Claude Code 环境由 L1 hook 覆盖）：
1. 铁律 6（工作区）：运行 `git rev-parse --abbrev-ref HEAD`。若在 main/master 且不在 `.worktrees/` 子路径 → STOP，创建 worktree。
2. 铁律 7（提交触发）：本 phase 禁止 `git commit` / `git push` / `gh pr create`。提交仅在 `/dev:ship` 中由用户触发。
3. 铁律 4（证据先行）：声称"完成/通过"前必须有测试命令的实际输出作为证据。
</SUPERVISE-CHECK>

# Phase 3: Plan -- "怎么做"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、路由宣告均使用中文。
2. **工作区前置（强制）。** 在创建任何计划文档或代码之前，执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并调用 `compound-engineering:ce-worktree`（或 `superpowers:using-git-worktrees`）创建工作区后再继续。
3. **提交由用户触发。** 本阶段只写文件、运行只读命令，不执行 `git commit` / `git push` / 创建 PR。提交动作只在 `/dev:ship`（Phase 6）由用户显式触发。
4. **Review 多轮门禁。** `ce-doc-review` 和 `plan-eng-review` 均是进入 `/dev:code` 前的门禁：执行"审查->修复/用户裁决->再审查"，直到零未处理 P0/P1、达到 3 轮上限、或连续两轮发现相同问题后升级给用户裁决。不要把 standalone `document-review` 的单轮报告当作通过。

## Overview

Phase 3 transforms requirements into an executable plan. `ce:plan` is the sole creator (decisions, not code). The skill **detects** plan scope and **auto-selects** the right review depth. Plans produce Implementation Units, Requirements Trace, and Test Scenarios consumed by `ce:work` in Phase 4.

Position in workflow: Phase 2 (design) -> **Phase 3** -> Phase 4 (implementation)

## When to Use

- Requirements doc exists (`docs/brainstorms/*-requirements.md`)
- Work is non-trivial (more than a one-file fix)

**Skip when:** Plan already exists and has review-pass evidence for this work item (`ce-doc-review` passed and `plan-eng-review`/selected Layer 2 review cleared).

## Scene Detection

**Signal 1: Does a plan already exist?**
- Search `docs/plans/` for plans matching the topic (within 30 days)
- If found with `status: active` and review-pass evidence present -> SKIP, go to `/dev:code`
- If found with `status: active` but missing `ce-doc-review` pass or Layer 2 REVIEW REPORT -> resume at review step
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

1. **Detect scene** using Signal 1. Announce (中文):
   - "找到已有计划，从审查步骤恢复。"
   - "无已有计划 -- 从需求文档创建。"

2. **Run `/ce:plan`** with requirements doc path
   - Parallel research: repo-research, learnings, best-practices, framework-docs, **`/dev:wiki-search`**
   - **Wiki Query**: 调用 `/dev:wiki-search` 扫项目 `wiki/index.md` + 全局 `~/.claude/wiki/index.md`,获取既有模式、决策、相关知识,按 caller 推荐顺序读页面,注入 plan context。
   - Output: `docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`（frontmatter 必须含 `status: active`）
   - Scope auto-classified: Lightweight / Standard / Deep

3. **REVIEW GATE (Layer 1): `ce-doc-review` 多轮门禁** (内嵌在 `ce:plan` Phase 5)
   - 使用 Compound Engineering 的 `ce-doc-review` / `compound-engineering:ce-doc-review`；不要改用 standalone `document-review`，因为它缺少本阶段需要的 round primer、routing question 和 CE handoff 语义。
   - 多人格审查: coherence / feasibility / scope-guardian（由 `ce-doc-review` 按文档内容自动叠加其他 persona）。
   - `safe_auto` 修复自动应用，`gated_auto` / `manual` 发现交用户判断；Codex 没有阻塞提问工具时，用编号选项停下等待用户，不得静默选项。
   - **循环**: 审查 -> 修复/用户裁决 -> 再审查，直到零未处理 P0/P1，或达到 3 轮上限，或连续两轮发现相同 P0/P1。
   - 若达到上限或收敛仍有 P0/P1：STOP，报告阻塞；只有用户显式接受风险并把理由写入计划的 Deferred/Open Questions 或 Review Notes 后，才允许继续 Layer 2。

   **GATE: 计划文件存在且有 `ce-doc-review` 通过证据（零未处理 P0/P1 或用户记录化 override）。**

4. **Detect review depth** from plan's Implementation Unit count (Signal 3). Announce (中文):
   - "计划有 12 个单元 -- 运行完整 autoplan 审查流水线。"
   - "计划有 5 个单元含 UI -- 运行工程 + 设计审查。"
   - "计划有 2 个单元 -- 仅运行工程审查。"

5. **REVIEW (Layer 2): 多视角计划审查 多轮循环** (auto-selected)
   - Large: `/gstack-autoplan` (CEO -> Design -> Eng -> DX, serial)
   - Standard: `/gstack-plan-eng-review` (required gate) + `/gstack-plan-design-review` (if UI)
   - Small: `/gstack-plan-eng-review` only
   - Developer-facing: + `/gstack-plan-devex-review`
   - **循环**: 每个审查技能内部执行多轮修复，直到零未处理 P0/P1、达到上限、或连续两轮发现相同问题。
   - 若 gstack 技能在 Codex 环境不可用，STOP 并要求用户选择手动执行对应审查、使用可用 CE/superpowers fallback，或显式记录 override；不得直接进入 `/dev:code`。

   **GATE: GSTACK REVIEW REPORT 写入计划文件。`plan-eng-review` CLEARED（零未处理 P0/P1 或用户记录化 override）。**

6. **Next**: `/dev:code` (Phase 4)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Phase 1 requirements doc path, Phase 2 `DESIGN.md` (if exists) |
| **Output** | `docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`（frontmatter 包含 `status: active`）with R-Trace + Impl Units |
| **Next** | `/dev:code` (Phase 4) |

## Iron Law

> Plans resolve decisions, not code. The implementer starts confidently without the plan writing code for them.
