---
name: dev-code
description: "Use when a reviewed plan exists and it is time to write code. Routes through ce:work, which detects plan complexity and auto-selects execution strategy (inline, serial agents, parallel agents, or swarm)."
---

<SUPERVISE-CHECK>
执行前自检（Codex 环境必读，Claude Code 环境由 L1 hook 覆盖）：
1. 铁律 6（工作区）：运行 `git rev-parse --abbrev-ref HEAD`。若在 main/master 且不在 `.worktrees/` 子路径 → STOP，创建 worktree。
2. 铁律 7（提交触发）：本 phase 禁止 `git commit` / `git push` / `gh pr create`。提交仅在 `/dev:ship` 中由用户触发。
3. 铁律 4（证据先行）：声称"完成/通过"前必须有测试命令的实际输出作为证据。
</SUPERVISE-CHECK>

# Phase 4: Code -- "写代码"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示均使用中文。
2. **工作区前置（强制）。** 开始写代码前执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并调用 `compound-engineering:git-worktree`（或 `superpowers:using-git-worktrees`）创建工作区后再继续。
3. **提交由用户触发。** Phase 4 只做文件修改、运行测试、必要时 `git add` 暂存，**不执行** `git commit` / `git push` / 创建 PR。提交仅在 `/dev:ship`（Phase 6）由用户显式触发。
4. **Review 多轮循环。** 内嵌的 `ce:review mode:autofix` 执行多轮循环（最多 2 轮 bounded re-review）。

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
| Files in `views/`, `components/`, `*.tsx`, `*.css` touched | `frontend-design` (auto-detects DESIGN.md) + **`dev-browser`** (启动 dev server 后真机验证 golden path、表单、控制台无 error) |
| Plan references a GitHub Issue | `reproduce-bug` (UI 复现时叠加 `dev-browser`) |
| Goal is measurable metric improvement | `ce-optimize` (iterative experiment loop with convergence) |

## Workflow

1. **`ce:work` detects scene** and announces (中文):
   - "计划有 5 个单元，其中 2 个独立 -- 对 Unit 1-2 使用并行 Agent，Unit 3-5 使用串行。"
   - "裸提示，影响 2 个文件 -- 内联执行。"
   - "计划 Unit 3 标记为 test-first -- 该单元使用 TDD。"

2. **`ce:work` executes** with auto-selected strategy
   - Per task: Implement -> Test Discovery -> System-Wide Test Check -> 暂存变更（可 `git add`，**不 commit**）
   - Every 2-3 units: Simplify pass (cross-unit dedup, still no commit)

3. **REVIEW: `ce:review mode:autofix` 多轮循环** (内嵌在 `ce:work` Phase 3)
   - Tier 2 (default): 20+ persona 并行审查, safe_auto 修复, R-ID 追溯
   - Tier 1 (仅当全部满足: 纯新增 + 单一关注点 + 模式跟随 + 忠于计划)
   - 传入 `plan:<path>` 用于需求追溯验证
   - **循环**: 修复 -> 再审查，最多 2 轮 bounded re-review（Phase 4 是快速 autofix 通道，比 Phase 5 的 3 轮上限更紧凑）

4. **Phase 4 → Phase 5 过渡关：`/simplify`（默认手动调用一次）**
   - 所有 Unit 完成后、进入 `/dev:verify` 之前，调用 `/simplify`
   - 三 agent 并行扫整个累积 diff：复用（找已有 util 替换）/ 质量（冗余 state、参数堆砌、复制粘贴、stringly-typed、无用注释）/ 效率（重复计算、可并行化串行、热路径臃肿、no-op 更新、TOCTOU、内存泄漏）
   - 直接修复发现的问题，false positive 跳过不争论
   - **跳过条件**: diff < 10 行 trivial 改动 / 仅文档变更 / 中途某 Unit 已单独跑过且后续无重大新增

   **GATE: 所有任务完成。测试通过。审查已应用。`/simplify` 已扫过。残余 todo 已记录。**

5. **Next**: `/dev:verify` (Phase 5)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Plan file path from Phase 3 (or bare prompt for small work) |
| **Output** | 已修改的代码 + 通过的测试 + ce:review autofix 已应用 + `/simplify` 已扫过（**未 commit**，工作树留有变更） |
| **Next** | `/dev:verify` (Phase 5) |

## Iron Laws

- **No failing test, no production code**
- **No root cause, no fix**
- **3 fix failures: stop and question the architecture**
- **不主动提交** —— commit / push / PR 仅在 `/dev:ship` 中由用户触发；本阶段产出未提交的工作树变更

## 编码行为约束（本阶段强制）

实现过程中必须遵循以下行为约束（完整规则见 `docs/ai-coding-workflow.md`）：

- **明确假设 / 不懂就问**：写代码前列出关键假设；需求有多解释时列出让用户选；不确定 STOP 问；更简单方案主动提出。**调用澄清工具时必须带推荐标识**——推荐项排第一并标 `(Recommended)`；无倾向时明说"无明确推荐"，不伪装中立。
- **手术刀修改**：只改任务直接相关的行，每行能追溯到 Implementation Unit 或用户请求；不顺手改相邻代码/注释/格式；匹配现有风格；发现无关 dead code 只提及不删除。
- **孤儿清理**：仅清理本次改动产生的未使用 import/变量；不动原有 dead code。

**Phase 4 收尾自检（`/simplify` 之前）**：每行改动可追溯？有无添加未请求的灵活性？相邻代码有无被顺手改？有无删除非本次产生的 dead code？有无静默选方向而非问用户？任一"是" → 回滚或 `/simplify` 时清扫。
