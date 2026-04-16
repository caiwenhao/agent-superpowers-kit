---
name: dev-code
description: "Use when a reviewed plan exists and it is time to write code. Routes through ce:work, which detects plan complexity and auto-selects execution strategy (inline, serial agents, parallel agents, or swarm)."
---

# Phase 4: Code -- "写代码"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示均使用中文。
2. **工作区检查优先。** 开始写代码前确认在 worktree/feature branch 中，否则先创建工作区。
3. **Review 多轮循环。** 内嵌的 `ce:review mode:autofix` 执行多轮循环（最多 2 轮 bounded re-review）。

## Overview

Phase 4 executes the plan. The single entry point is `ce:work`, which **detects** plan complexity and **auto-selects** the best execution strategy. Auxiliary skills are **auto-triggered** by context signals -- not by the user.

Position in workflow: Phase 3 (planning) -> **Phase 4** -> Phase 5 (verification)

## When to Use

- A reviewed plan exists (`docs/plans/*.md`)
- Or: a bare prompt describes small, clear work

**Never skip Phase 4.**

## Scene Detection (performed by `ce:work` internally)

**Signal 1: Is there a plan file?**
- No plan file, no bare prompt -> STOP, return to `/dev:plan`
- No plan file, has bare prompt -> `ce:work` assesses complexity:
  - Trivial (1-2 files) -> proceed inline
  - Large (10+ files, cross-cutting) -> recommend `/dev:discover` + `/dev:plan` first

**Signal 2: Plan complexity (auto-detected from Implementation Units)**

| Detected Signal | Auto-selected Strategy |
|---|---|
| 1-2 files, no behavioral change | Direct inline |
| < 10 files, clear scope | Serial task list |
| 3+ units with sequential dependencies | Serial sub-agents |
| 3+ units with independent units (no shared files) | Parallel sub-agents |
| 10+ units needing inter-agent coordination | Swarm (Agent Teams) |
| Measurable optimization goal (prompt quality, latency, search relevance) | `ce-optimize` (metric-driven experiment loop) |

**Signal 3: Execution posture (auto-detected from plan content)**

| Detected Signal | Auto-triggered Skill |
|---|---|
| Implementation Unit has `Execution note: test-first` | `test-driven-development` (RED-GREEN-REFACTOR) |
| Implementation Unit has `Execution note: characterization-first` | Characterization tests before changes |
| Implementation Unit has `Execution note: external-delegate` | Codex delegation mode |
| Bug encountered during implementation | `ce-debug` (causal-chain-gated, 4-phase) / `investigate` |
| Multiple independent test failures | `dispatching-parallel-agents` |
| Files in `views/`, `components/`, `*.tsx`, `*.css` touched | `frontend-design` (auto-detects DESIGN.md) |
| Plan references a GitHub Issue | `reproduce-bug` |
| Goal is measurable metric improvement | `ce-optimize` (iterative experiment loop with convergence) |

## Workflow

1. **`ce:work` detects scene** and announces (中文):
   - "计划有 5 个单元，其中 2 个独立 -- 对 Unit 1-2 使用并行 Agent，Unit 3-5 使用串行。"
   - "裸提示，影响 2 个文件 -- 内联执行。"
   - "计划 Unit 3 标记为 test-first -- 该单元使用 TDD。"

2. **`ce:work` executes** with auto-selected strategy
   - Per task: Implement -> Test Discovery -> System-Wide Test Check -> Incremental commit
   - Every 2-3 units: Simplify pass (cross-unit dedup)

3. **REVIEW: `ce:review mode:autofix` 多轮循环** (内嵌在 `ce:work` Phase 3)
   - Tier 2 (default): 20+ persona 并行审查, safe_auto 修复, R-ID 追溯
   - Tier 1 (仅当全部满足: 纯新增 + 单一关注点 + 模式跟随 + 忠于计划)
   - 传入 `plan:<path>` 用于需求追溯验证
   - **循环**: 修复 -> 再审查，最多 2 轮 bounded re-review（Phase 4 是快速 autofix 通道，比 Phase 5 的 3 轮上限更紧凑）

   **GATE: 所有任务完成。测试通过。审查已应用。残余 todo 已记录。**

4. **Next**: `/dev:verify` (Phase 5)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Plan file path from Phase 3 (or bare prompt for small work) |
| **Output** | Committed code, passing tests, ce:review autofix applied |
| **Next** | `/dev:verify` (Phase 5) |

## Iron Laws

- **No failing test, no production code**
- **No root cause, no fix**
- **3 fix failures: stop and question the architecture**
