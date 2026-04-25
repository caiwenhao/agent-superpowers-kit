---
name: dev-design
description: "Use when a requirements doc exists and the work involves UI, visual components, or front-end changes. Detects project design maturity and routes through the right design pipeline. Skip entirely for pure backend work."
---

<SUPERVISE-CHECK>
执行前自检（Codex 环境必读，Claude Code 环境由 L1 hook 覆盖）：
1. 铁律 6（工作区）：运行 `git rev-parse --abbrev-ref HEAD`。若在 main/master 且不在 `.worktrees/` 子路径 → STOP，创建 worktree。
2. 铁律 7（提交触发）：本 phase 禁止 `git commit` / `git push` / `gh pr create`。提交仅在 `/dev:ship` 中由用户触发。
3. 铁律 4（证据先行）：声称"完成/通过"前必须有测试命令的实际输出作为证据。
</SUPERVISE-CHECK>

# Phase 2: Design -- "长什么样"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、路由宣告均使用中文。
2. **工作区前置（强制）。** 在创建任何设计文档或代码之前，执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并调用 `compound-engineering:git-worktree`（或 `superpowers:using-git-worktrees`）创建工作区后再继续。
3. **提交由用户触发。** 本阶段只写文件、运行只读命令，不执行 `git commit` / `git push` / 创建 PR。提交动作只在 `/dev:ship`（Phase 6）由用户显式触发。
4. **Review 多轮循环。** Spec Review Loop 执行"审查->修复->再审查"循环，最多 3 轮。

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

1. **Detect scene** using the signals above. Announce (中文):
   - "未找到设计体系 -- 先创建 DESIGN.md。"
   - "设计体系已存在，为该功能探索视觉方向。"
   - "视觉方向已确认 -- 将设计审查推迟到规划阶段。"

2. **Execute the detected route**

   **Route A**: Run `/gstack-design-consultation` -> output `DESIGN.md` -> then `/gstack-design-shotgun`
   **Route B**: Run `/gstack-design-shotgun` with `DESIGN.md` as constraint
   **Route C**: Note for Phase 3 to run `/gstack-plan-design-review`

3. **REVIEW: Spec Review Loop 多轮循环** (内嵌在 `design-consultation`)
   - 独立子 Agent 对抗审查 (5 维度: Completeness / Consistency / Clarity / Scope / Feasibility)
   - 评分 1-10，有问题则修复后重新审查
   - **循环**: 审查 -> 修复 -> 再审查，最多 3 轮或连续两轮发现相同则收敛
   - 未解决的问题写入 "Reviewer Concerns" 部分

   **GATE: `DESIGN.md` 通过审查（零 P0/P1）+ `approved.json` 存在 + 用户确认方向。**

4. **(Optional)** Run `/gstack-design-html` to generate high-fidelity prototype

5. **Next**: `/dev:plan` (Phase 3)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Phase 1 requirements doc, existing codebase |
| **Output** | `DESIGN.md` (persistent) + `approved.json` (per-feature) |
| **Next** | `/dev:plan` (Phase 3) |

## Iron Law

> No implementation begins until the visual direction is approved. `DESIGN.md` is the design source of truth -- deviations are defects.

`DESIGN.md` is the design anchor -- all downstream skills consume or enforce it:
- `/gstack-design-shotgun` constrains variant generation
- `/gstack-plan-design-review` calibrates ratings against it
- `/gstack-design-html` extracts tokens from it
- `/gstack-design-review` scores deviations as higher severity
- `frontend-design` detects and follows it automatically in `/ce:work`
