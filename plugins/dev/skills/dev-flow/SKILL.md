---
name: dev-flow
description: "Use when starting any development task, or when unsure which dev: phase to begin with. Detects the current project state, identifies which phase the work is in, and orchestrates the full discover->design->plan->code->verify->ship->learn pipeline automatically. The single entry point for the entire AI Coding workflow."
---

# dev-flow -- 智能研发编排器

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、路由宣告、错误信息均使用中文。技能名称、文件路径、代码保持英文原样。
2. **工作区检查优先。** 在创建任何文档或代码之前，必须确认当前是否在 git worktree 中。如果不在，先创建工作区（调用 `compound-engineering:git-worktree` 或 `superpowers:using-git-worktrees`），再开始工作。
3. **Review 采取多轮循环。** 所有涉及 review 的环节（document-review、ce:review、plan-eng-review 等），执行"审查 -> 修复 -> 再审查"循环，直到：(a) 零 P0/P1 发现，或 (b) 达到最大轮次（默认 3 轮），或 (c) 连续两轮发现相同问题（收敛）。

## Overview

`$dev-flow` is the single entry point for the entire AI Coding workflow. It **detects** where the current work stands in the 7-phase pipeline, **enters** at the right phase, and **drives** through to completion -- or stops at a GATE for user approval before continuing.

```
$dev-flow
  |
  +-- Detect current state
  |
  +-- Enter at the right phase
  |
  +-- Drive: discover -> design -> plan -> code -> verify -> ship -> learn
  |                                                                   |
  +-- <------------------------------- next work item ----------------+
```

You do not need to call individual `dev:*` phase skills manually. `$dev-flow` detects and routes.

## Scene Detection: Where Are We?

On invocation, check these signals **in order** to determine which phase to enter:

### Signal 0: Are we in a worktree?

```bash
# Check if currently in a git worktree
git rev-parse --is-inside-work-tree 2>/dev/null && echo "GIT: yes" || echo "GIT: no"
git worktree list 2>/dev/null | head -5
```

| Finding | Action |
|---|---|
| Not in a git repo | STOP: "当前不在 git 仓库中，无法启动研发流程。" |
| In main/master branch, no worktree | 创建工作区: "当前在主分支，需要创建工作区以隔离开发。" -> 调用 `compound-engineering:git-worktree` |
| Already in a feature branch or worktree | 继续 Signal 1 |

### Signal 1: Is there unfinished work from a previous session?

```bash
# Check for in-progress plan
ls docs/plans/*-plan.md 2>/dev/null | head -5

# Check for uncommitted code changes
git status --short

# Check for open PR on current branch
gh pr view --json state,title 2>&1
```

| Finding | Enter At |
|---|---|
| Plan with `status: active`, unchecked Implementation Units | Phase 4 (code) -- resume execution |
| Uncommitted code changes + recent ce:review run | Phase 6 (ship) -- ready to deliver |
| Uncommitted code changes, no review evidence | Phase 5 (verify) -- needs review |
| Open PR with unresolved review threads | Phase 6 (ship) -- resolve feedback, then ship |
| Plan with `status: active`, all units checked, no code changes | Phase 5 (verify) -- confirm completion |
| Nothing in progress | Check Signal 2 |

### Signal 2: What did the user provide?

| User Input | Enter At |
|---|---|
| No input / empty | Phase 1 (discover) -- "我们做什么？" |
| Vague idea: "improve the search", "make it faster" | Phase 1 (discover) -- needs requirements |
| Bug report: "X is broken", "error when Y" | Phase 4 (code) -- via `ce:work` bare prompt with `investigate` |
| Clear feature with spec: "Add OAuth per this doc" | Phase 3 (plan) -- requirements exist informally |
| File path to requirements doc | Phase 2 or 3 -- check if UI involved |
| File path to plan doc | Phase 4 (code) -- plan exists, execute it |
| "ship it" / "deploy" / "create PR" | Phase 6 (ship) -- go straight to delivery |
| "what did we learn" / "retro" | Phase 7 (learn) -- knowledge capture |
| Dependency upgrade: "upgrade X", "update deps" | Phase 3 (plan) -- 需要计划升级步骤和回滚策略 |
| Docs-only: "update README", "fix docs" | Phase 4 (code) -- bare prompt inline, skip Phase 1-3 |
| Greenfield: "new project", "init", "bootstrap" | Phase 1 (discover) -- 从头开始，含项目脚手架 |

### Signal 3: What artifacts already exist?

```bash
# Requirements docs
ls docs/brainstorms/*-requirements.md 2>/dev/null

# Design system
ls DESIGN.md 2>/dev/null

# Plans
ls docs/plans/*-plan.md 2>/dev/null

# Recent ce:review runs
ls .context/compound-engineering/ce-review/ 2>/dev/null
```

| Artifacts Present | Enter At |
|---|---|
| No requirements doc | Phase 1 (discover) |
| Requirements doc exists, no DESIGN.md, work has UI | Phase 2 (design) |
| Requirements doc exists, no plan | Phase 3 (plan) |
| Requirements + plan exist, plan not started | Phase 4 (code) |
| Code changes + review done | Phase 6 (ship) |
| Everything shipped | Phase 7 (learn) |

## Orchestration Loop

Once the entry phase is determined, `$dev-flow` drives through the pipeline:

```
[Entry Point Detected]
      |
      v
  Phase 1: $dev-discover
      |  Scene Detection -> ideate / office-hours / brainstorm
      |  Output: requirements doc with R-IDs
      |  GATE: user approves requirements
      |
      |  Auto-detect: has UI? ----yes----> Phase 2
      |                  |
      |                  no
      |                  |
      v                  v
  Phase 2: $dev-design        |
      |  Scene Detection ->   |
      |  consultation /       |
      |  shotgun / skip       |
      |  Output: DESIGN.md    |
      |  GATE: design approved|
      |                       |
      v                       |
  Phase 3: $dev-plan  <-------+
      |  ce:plan -> auto-select review depth
      |  Output: plan doc with Impl Units
      |  GATE: plan-eng-review CLEARED
      |
      v
  Phase 4: $dev-code
      |  ce:work auto-selects strategy
      |  Built-in: ce:review mode:autofix
      |  GATE: all tasks done, tests pass
      |
      v
  Phase 5: $dev-verify
      |  ce:review full + auto-stack layers
      |  GATE: PASS verdict
      |
      v
  Phase 6: $dev-ship
      |  Auto-select Path A or B
      |  land-and-deploy with canary
      |  GATE: user confirms merge
      |
      v
  Phase 7: $dev-learn
      |  Auto-detect trigger type
      |  compound / retro / writing-skills
      |
      v
  [Loop back to Phase 1 for next work item]
```

## GATE Behavior

At each GATE, `$dev-flow` **stops and reports status** before continuing:

```
--- GATE: Phase 1 完成 ---
需求文档: docs/brainstorms/2026-04-04-user-auth-requirements.md
需求 ID: R1 (注册), R2 (登录), R3 (管理员禁用)
文档审查: 通过
UI 检测: 是 (R1, R2 中提到 views/components)

下一步: Phase 2 (设计) -- 继续? [继续 / 跳到 Phase 3 / 暂停]
```

User can:
- **继续** -- 进入下一阶段
- **跳过** -- 跳过当前阶段（如后端无需设计）
- **暂停** -- 暂停流程，稍后用 `$dev-flow` 恢复
- **回退** -- "回到 Phase 1 修改需求"

## Resume Intelligence

When `$dev-flow` is called again in a subsequent session:

1. Scan for artifacts (Signal 3) to detect where the previous session left off
2. Read the most recent plan's `status` field and checkbox progress
3. Check git branch state and PR status
4. Announce: "Resuming from Phase 4 -- plan has 3/5 units completed on branch `feat/user-auth`."
5. Continue from the detected phase

## Handling Branches and Parallel Work

```
$dev-flow (main line of work)
  |
  +-- User says "also fix this bug while we're at it"
  |   -> Assess: is this related to current work?
  |     yes -> add to current plan as a new Implementation Unit
  |     no  -> "This is separate work. Finish current flow first, or use
  |             $dev-flow in a new worktree for parallel development."
  |
  +-- User says "pause this, work on something else"
  |   -> 调用 `/gstack-checkpoint` 保存当前状态 (branch, progress, decisions)
  |   -> Start new $dev-flow for the new work item
  |   -> When done, `/gstack-checkpoint` resume 恢复暂停的流程
```

## Phase Skip Rules

Not every work item needs all 7 phases. `$dev-flow` auto-detects skippable phases:

| Condition | Skip |
|---|---|
| Pure backend, no UI in requirements | Phase 2 (design) |
| Trivial fix (1-2 files, clear scope) | Phase 1 (Lightweight brainstorm), Phase 2, Phase 3 |
| Emergency hotfix | Phase 1, 2, 3 -- go straight to Phase 4 with bare prompt |
| Requirements already exist and approved | Phase 1 |
| DESIGN.md exists and no new UI patterns needed | Phase 2 |
| Plan already exists and reviewed | Phase 3 |
| Nothing novel learned | Phase 7 |
| Docs-only change (README, CONTRIBUTING, etc.) | Phase 1, 2, 3 -- Phase 4 inline + Phase 5 (devex-review auto-stacked) |
| Dependency upgrade | Phase 2 -- 走 Phase 1(轻量需求)->3(升级计划)->4->5->6 |

When skipping, announce: "Skipping Phase 2 (design) -- pure backend work, no UI surface detected."

## Error Recovery

| Situation | Action |
|---|---|
| Phase fails (tests don't pass, review finds blockers) | Stay in current phase, fix issues, retry |
| User disagrees with routing | Accept redirect, re-enter at specified phase |
| Upstream artifact missing (no requirements, no plan) | Route back to the missing phase |
| 3 consecutive failures in same phase | Escalate: "Phase 4 has failed 3 times. Should we revisit the plan (Phase 3) or the requirements (Phase 1)?" |

## Full Example

```
用户: "我想在用户账号被禁用时发送邮件通知"

$dev-flow 检测:
  - Signal 0: 在 feat/notifications 分支，工作区就绪
  - Signal 1: 无进行中的工作
  - Signal 2: 明确的功能描述，中等范围
  - 进入 Phase 1

Phase 1 ($dev-discover):
  场景: 明确功能，中等范围 -> Route C (Standard brainstorm)
  -> ce:brainstorm 产出需求文档 R1-R4
  -> document-review: 通过（2 轮循环，第 1 轮修复 1 个一致性问题）
  -> 检测到 UI: 是（通知设置页面）
  GATE: "需求已就绪。检测到 UI。进入 Phase 2?"

Phase 2 ($dev-design):
  场景: DESIGN.md 存在，该功能无 approved.json -> Route B
  -> design-shotgun 生成 3 个变体
  -> 用户选择变体 B
  GATE: "设计方向已确认。进入 Phase 3?"

Phase 3 ($dev-plan):
  -> ce:plan 产出 4 个实施单元
  -> document-review: 通过
  -> 检测到 4 单元 -> plan-eng-review + plan-design-review
  -> plan-eng-review: CLEARED
  GATE: "计划已审查通过。进入 Phase 4?"

Phase 4 ($dev-code):
  -> ce:work 检测 4 单元，2 个独立 -> 并行+串行策略
  -> Unit 1-2 (并行): 邮件服务 + 通知模型
  -> Unit 3-4 (串行): 控制器 + 设置页面
  -> ce:review mode:autofix: 修复 2 个 safe_auto 问题
  GATE: "所有单元完成。测试通过。进入 Phase 5?"

Phase 5 ($dev-verify):
  -> ce:review interactive: 8 个 persona 激活（含邮件处理的 security）
  -> 第 1 轮: 发现 1 个 P1 (邮件注入风险) + 1 个 P2
  -> 修复 -> 第 2 轮: 零 P0/P1 -> 通过
  -> test-browser: 通知设置页面测试通过
  GATE: "验证通过。进入 Phase 6?"

Phase 6 ($dev-ship):
  场景: 无版本文件 + 上游 ce:review 已确认 -> Path A
  -> git-commit-push-pr: PR 已创建
  -> feature-video: 通知流程录屏
  -> land-and-deploy: 合并、部署、金丝雀健康
  GATE: "已发布并验证。进入 Phase 7?"

Phase 7 ($dev-learn):
  场景: 功能已发布，邮件服务模式是新的 -> Route A
  -> ce:compound 记录邮件通知模式
  -> "知识已沉淀。准备进入下一个工作项。"
```

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Anything: idea, bug report, file path, "ship it", or nothing |
| **Output** | Completed work item: requirements -> design -> plan -> code -> verified -> shipped -> documented |
| **Next** | Self (next work item) |

## Iron Laws (inherited from all phases)

1. **Design before implement** -- no code without approved requirements
2. **Test before code** -- no production code without failing test
3. **Root cause before fix** -- no fix without understanding why
4. **Evidence before assertion** -- no "it works" without proof
5. **Verify before adopt** -- no review feedback accepted without verification
