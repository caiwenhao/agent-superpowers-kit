---
name: dev-code
description: "Use when a reviewed plan exists and it is time to write code. Routes through ce-work, which detects plan complexity and auto-selects execution strategy (inline, serial agents, parallel agents, or swarm)."
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
2. **工作区前置（强制）。** 开始写代码前执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并调用 `using-git-worktrees` 创建工作区后再继续（路径 `<repo>/.worktrees/<task-name>/`；规范名与环境别名见 `claude-skills/README.md` 的 Skill Naming 表）。
3. **提交由用户触发。** Phase 4 只做文件修改、运行测试、必要时 `git add` 暂存，**不执行** `git commit` / `git push` / 创建 PR。提交仅在 `/dev:ship`（Phase 6）由用户显式触发。
4. **Review 自动修复回路。** `dev-code` 是外层编排器：按 2-3 个 Implementation Units 切批调用 `ce-work`，每批后运行 `ce-review mode:autofix`；所有 Unit 完成后先 `/simplify`，再运行最终 autofix。Phase 4 只自动应用 `safe_auto`，不做 `gated_auto/manual` 用户裁决；残余发现进入 Phase 5 的总体审查。

## Overview

Phase 4 executes the plan. The single entry point is `ce-work`, which **detects** plan complexity and **auto-selects** the best execution strategy. Auxiliary skills are **auto-triggered** by context signals -- not by the user.

Position in workflow: Phase 3 (planning) -> **Phase 4** -> Phase 5 (verification)

## When to Use

- A reviewed plan exists (`docs/plans/*.md`)
- Or: a bare prompt describes small, clear work

**Never skip Phase 4.**

## Scene Detection (performed by `ce-work` internally)

**Signal 1: Is there a plan file?**
- No plan file, no bare prompt -> STOP, return to `/dev:plan`
- No plan file, has bare prompt -> `ce-work` assesses complexity:
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
| Implementation Unit has `Execution note: test-first` | `tdd`（垂直切片 RED-GREEN-REFACTOR：一个测试 → 一个实现 → 重复；禁止水平切片；测试只验证公共接口行为；接口设计追求 deep module；mock 规则见 `tdd/mocking.md`） |
| Implementation Unit has `Execution note: characterization-first` | Characterization tests before changes |
| Implementation Unit has `Execution note: external-delegate` | Codex delegation mode |
| Bug encountered during implementation | `diagnose`（构建 feedback loop → 复现 → 3-5 可证伪假设 → 仪器化 → 修复 + 回归测试 → 清理 [DEBUG-xxxx] 标签）；fallback: `ce-debug` |
| Multiple independent test failures | `dispatching-parallel-agents` |
| Files in `views/`, `components/`, `*.tsx`, `*.css` touched | `frontend-design` (auto-detects DESIGN.md) + **`dev-browser`** (启动 dev server 后真机验证 golden path、表单、控制台无 error) |
| Plan references a GitHub Issue | `reproduce-bug` (UI 复现时叠加 `dev-browser`) |
| Goal is measurable metric improvement | `ce-optimize` (iterative experiment loop with convergence) |
| Agent 进入不熟悉的代码区域（多次跨文件跳转、读 3+ 个不相关模块仍无法定位） | `zoom-out`（上升一层抽象，用领域词汇表画出相关模块和调用者的地图） |
| 修复完成后发现架构摩擦（无好的测试 seam、浅模块、紧耦合） | 标记 `improve-codebase-architecture` 建议（不在 Phase 4 执行，留给 Phase 7 或独立任务） |

## Workflow

1. **`ce-work` detects scene** and announces (中文):
   - "计划有 5 个单元，其中 2 个独立 -- 对 Unit 1-2 使用并行 Agent，Unit 3-5 使用串行。"
   - "裸提示，影响 2 个文件 -- 内联执行。"
   - "计划 Unit 3 标记为 test-first -- 该单元使用 TDD。"

2. **`dev-code` slices execution into batches, then invokes `ce-work` for each batch**
   - Batch size: 2-3 Implementation Units by default; one batch is fine for small plans.
   - Pass the plan path plus the current batch's Unit IDs/goals to `ce-work`; instruct it to execute only that batch.
   - Use `ce-work` as an implementation executor only: Implement -> Test Discovery -> System-Wide Test Check -> stage allowed, **no commit**.
   - Do not let `ce-work` enter its own shipping workflow / residual-review gate. Phase 4 residuals are recorded and handed to Phase 5.

3. **REVIEW AUTOFIX LOOP: `ce-review mode:autofix`** (Phase 4 自动修复回路)
   - 默认 Tier 2: 20+ persona 并行审查, `safe_auto` 修复, R-ID 追溯
   - Tier 1 (仅当全部满足: 纯新增 + 单一关注点 + 模式跟随 + 忠于计划)
   - 传入 `plan:<path>` 用于需求追溯验证
   - **批次触发**: 每个 `ce-work` batch 完成后立即运行一次；若是单批次/小改动，至少在实现完成后运行一次
   - **最终触发**: 所有 Unit 完成并运行 `/simplify` 后，再运行一次最终 autofix，覆盖 simplification edits
   - **单次运行内部循环**: `mode:autofix` 自动执行 bounded re-review，应用 `safe_auto -> review-fixer` 后重审，直到无新的 `safe_auto` 或达到上游轮次上限
   - **边界**: Phase 4 不处理 `gated_auto` / `manual` / `human` / `release` 决策；这些残余必须记录为 downstream work/todo，交给 Phase 5 interactive 总体审查处理
   - **禁止降级**: 不得因为还会运行 `/dev:verify` 就跳过 Phase 4 的 autofix loop；Phase 5 是独立质量门，不是 Phase 4 自动修复的替代品

4. **Phase 4 → Phase 5 过渡关：`/simplify` + final autofix**
   - 所有 Unit 完成后、进入 `/dev:verify` 之前，调用 `/simplify`
   - 三 agent 并行扫整个累积 diff：复用（找已有 util 替换）/ 质量（冗余 state、参数堆砌、复制粘贴、stringly-typed、无用注释）/ 效率（重复计算、可并行化串行、热路径臃肿、no-op 更新、TOCTOU、内存泄漏）
   - 直接修复发现的问题，false positive 跳过不争论
   - `/simplify` 之后必须再运行一次 `ce-review mode:autofix plan:<path>`；这才是 Phase 4 的最终 autofix pass
   - **跳过条件**: diff < 10 行 trivial 改动 / 仅文档变更 / 中途某 Unit 已单独跑过且后续无重大新增

   **CHECKPOINT:** 所有任务完成。测试通过。`/simplify` 已扫过。final autofix 已覆盖 `/simplify` 后 diff，`safe_auto` 已应用。残余 `gated_auto/manual` todo 已记录并交给 Phase 5。
   - 条件满足时直接进入 `/dev:verify`；不要问"是否继续 Phase 5"。
   - 若测试失败、任务未完成、或残余问题需要用户取舍，才发起 Decision GATE / STOP。

5. **Next**: `/dev:verify` (Phase 5). 默认自动进入；只有 blocker / 用户取舍 / 用户明确要求逐步确认时才停下。

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Plan file path from Phase 3 (or bare prompt for small work) |
| **Output** | 已修改的代码 + 通过的测试 + Phase 4 多次 `ce-review mode:autofix` 的 `safe_auto` 已应用 + `/simplify` 已扫过（**未 commit**，工作树留有变更） |
| **Next** | `/dev:verify` (Phase 5), auto-continue when implementation checkpoint is clear |

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
