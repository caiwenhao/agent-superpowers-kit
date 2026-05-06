---
name: dev-plan
description: "Use when a requirements doc exists and it is time to create an implementation plan. Detects scope to select review depth: autoplan for large features, plan-eng-review for ordinary work. Plan creation and core reviews use internal reference protocols."
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
2. **工作区前置（强制）。** 在创建任何计划文档或代码之前，执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并调用 `using-git-worktrees` 创建工作区后再继续（路径 `<repo>/.worktrees/<task-name>/`；规范名与环境别名见 `claude-skills/README.md` 的 Skill Naming 表）。
3. **提交由用户触发。** 本阶段只写文件、运行只读命令，不执行 `git commit` / `git push` / 创建 PR。提交动作只在 `/dev:ship`（Phase 6）由用户显式触发。
4. **Review 多轮门禁。** Layer 1 (doc-review-protocol) 和 Layer 2 (eng-review-protocol) 均是进入 `/dev:code` 前的门禁：执行"审查->修复/用户裁决->再审查"，直到零未处理 P0/P1、达到 3 轮上限、或连续两轮发现相同问题后升级给用户裁决。

## Overview

Phase 3 transforms requirements into an executable plan. The plan creation protocol (`references/plan-engine.md`) is the sole creator (decisions, not code). The skill **detects** plan scope and **auto-selects** the right review depth. Plans produce Implementation Units, Requirements Trace, and Test Scenarios consumed by Phase 4.

Position in workflow: Phase 2 (design) -> **Phase 3** -> Phase 4 (implementation)

## When to Use

- Requirements doc exists (`docs/brainstorms/*-requirements.md`)
- Work is non-trivial (more than a one-file fix)

**Skip when:** Plan already exists and has review-pass evidence for this work item (Layer 1 passed and Layer 2 review cleared). A freshly written plan file without completed review gates does **not** qualify.

## Scene Detection

**Signal 1: Does a plan already exist?**
- Search `docs/plans/` for plans matching the topic (within 30 days)
- If found with `status: active` and review-pass evidence present -> SKIP, go to `/dev:code`
- If found with `status: active` but missing Layer 1 pass or Layer 2 REVIEW REPORT -> resume at review step
- If found with `status: completed` -> SKIP or create new plan (ask user)

Layer 1 pass evidence means one of:
- the current `/dev:plan` invocation just ran doc-review-protocol on this exact plan path and cleared Layer 1, or
- the plan file already records the last Layer 1 result / override in `Deferred/Open Questions` or `Review Notes`, and there have been no material edits since that review.

Plan file existence by itself is **not** review-pass evidence.

**Signal 2: Does `DESIGN.md` exist? (from Phase 2)**
- Yes -> plan-engine will reference design tokens; design review dimension should run
- No -> skip design review dimension

**Signal 3: Plan scope (auto-detected after creating the plan)**
- Count Implementation Units produced:
  - 1-2 units -> Small scope
  - 3-9 units -> Standard scope
  - 10+ units -> Large scope
- Check if units touch developer-facing surfaces (API, CLI, SDK, docs):
  - Yes -> add DX review

## Routing

### Plan Creation (always the same)

Execute the plan creation protocol from `references/plan-engine.md` -- parallel research sub-agents, R-ID trace, Implementation Units, Test Scenarios.

### Review Depth (auto-selected after plan creation)

```
Plan created by plan-engine
  |
  +-- 10+ Implementation Units ---------> Multi-review pipeline (eng-review + doc-review full persona set)
  |   (large/cross-cutting)
  |
  +-- 3-9 Units ------------------------> eng-review-protocol (required)
  |   (standard)                           + gstack-plan-design-review (if DESIGN.md exists, OPTIONAL)
  |
  +-- 1-2 Units ------------------------> eng-review-protocol only
  |   (small)
  |
  +-- Units touch API/CLI/SDK/docs -----> + gstack-plan-devex-review (OPTIONAL, additive)
      (developer-facing)
```

**OPTIONAL skill degradation:** If `gstack-plan-design-review` or `gstack-plan-devex-review` is not installed:
> gstack-<name> 未安装 -- 使用内置 doc-review-protocol 的 design-lens/feasibility persona 覆盖。

Fall back to executing `references/doc-review-protocol.md` with the relevant persona (design-lens for design review, feasibility for devex review).

## Workflow

1. **Detect scene** using Signal 1. Announce (中文):
   - "找到已有计划，从审查步骤恢复。"
   - "无已有计划 -- 从需求文档创建。"

2. **Execute the plan creation protocol from `references/plan-engine.md`** with requirements doc path
   - Parallel research: repo-research, learnings, best-practices, framework-docs, **`/dev:wiki-search`**
   - **Wiki Query**: 调用 `/dev:wiki-search` 扫项目 `wiki/index.md` + 全局 `~/.claude/wiki/index.md`,获取既有模式、决策、相关知识,按 caller 推荐顺序读页面,注入 plan context。
   - Output: `docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`（frontmatter 必须含 `status: active`）
   - Scope auto-classified: Lightweight / Standard / Deep
   - plan-engine 写出 plan 文件后**不算完成**。即使它展示了 handoff 菜单或说"下一步可做 review / code"，`dev-plan` 也必须继续执行自己的 Layer 1 / Layer 2 gates。

3. **Post-creation enforcement: resolve plan path and enter Layer 1 immediately**
   - 读取产出的绝对 plan 路径。若没产出 plan 文件，STOP 并重新运行 plan-engine；不得进入 review depth 检测。
   - Ignore post-generation menu as a completion signal. In `/dev:plan`, plan creation is only the handoff into review gates.
   - 若是新创建或刚被改写的计划：立刻进入 Layer 1，不要向用户输出"如果你要，我继续做 review"之类的可选措辞。

4. **REVIEW GATE (Layer 1): Execute the document review protocol from `references/doc-review-protocol.md`**
   - 多人格审查: coherence / feasibility / scope-guardian（按文档内容自动叠加其他 persona）。
   - 在 Codex 下，若 reviewer-agent / task spawning 可用，必须按 reviewer role 分发为多 agent 审查（可 bounded parallel），不要在能力可用时退化成单线程综合。
   - 只有在当前 harness 明确拿不到 reviewer agents 时，才允许降级为串行 persona passes；降级时仍要保留按 role 分开的 findings，并在状态报告里显式标注。
   - 默认直接执行 doc-review-protocol `<plan-path>`。只有在调用链是 pipeline / disable-model-invocation / `mode:auto` 风格的非交互上下文时，才改用 `mode:headless <plan-path>`。
   - `safe_auto` 修复自动应用，`gated_auto` / `manual` 发现交用户判断；Codex 没有阻塞提问工具时，用编号选项停下等待用户，不得静默选项。
   - **循环**: 审查 -> 修复/用户裁决 -> 再审查，直到零未处理 P0/P1，或达到 3 轮上限，或连续两轮发现相同 P0/P1。
   - 若达到上限或收敛仍有 P0/P1：STOP，报告阻塞；只有用户显式接受风险并把理由写入计划的 Deferred/Open Questions 或 Review Notes 后，才允许继续 Layer 2。

   **CHECKPOINT:** 计划文件存在且有 Layer 1 通过证据（零未处理 P0/P1 或用户记录化 override）。
   - 零未处理 P0/P1 时直接进入 Layer 2；不要询问"是否继续审查"。
   - 只有存在 `gated_auto` / `manual` 取舍、P0/P1 override、或多个合理计划方向时才发起 Decision GATE。

5. **Detect review depth** from plan's Implementation Unit count (Signal 3). Announce (中文):
   - "计划有 12 个单元 -- 运行完整多视角审查流水线。"
   - "计划有 5 个单元含 UI -- 运行工程 + 设计审查。"
   - "计划有 2 个单元 -- 仅运行工程审查。"

6. **REVIEW (Layer 2): 多视角计划审查 多轮循环** (auto-selected)
   - Large: Run sequential multi-review: execute eng-review-protocol + doc-review-protocol with full persona set (CEO + Design + Eng + DX perspectives, serial)
   - Standard: Execute the engineering review protocol from `references/eng-review-protocol.md` (required gate) + `gstack-plan-design-review` (if UI, OPTIONAL)
   - Small: Execute `references/eng-review-protocol.md` only
   - Developer-facing: + `gstack-plan-devex-review` (OPTIONAL, additive)
   - **OPTIONAL skill degradation:** gstack-<name> 未安装 -- 使用内置 doc-review-protocol 的 design-lens/feasibility persona 覆盖。
   - **循环**: 每个审查协议内部执行多轮修复，直到零未处理 P0/P1、达到上限、或连续两轮发现相同问题。
   - 若内置协议均已执行但 gstack 可选审查不可用，Codex 路径优先保留多 agent 角色审查：至少运行一轮 doc-review-protocol reviewer fanout 覆盖 coherence/feasibility/scope/design/security/product/adversarial，并明确还缺少哪些维度；之后由用户选择手动补充或记录 override。不得直接进入 `/dev:code`。

   **CHECKPOINT:** REVIEW REPORT 写入计划文件。eng-review-protocol CLEARED（零未处理 P0/P1 或用户记录化 override）。
   - 通过后默认进入 `/dev:code`；不要为"继续 Phase 4"单独确认。
   - 若仍需用户接受风险、缩小范围、选替代架构，才发起 Decision GATE。

7. **Next**: `/dev:code` (Phase 4). 默认自动进入；只有 unresolved plan decision / risk override / 用户明确要求逐步确认时才停下。

### 计划后分解：`to-issues`（可选）

计划审查通过后，如果项目使用 Issue Tracker 且计划包含 3+ Implementation Units，自动建议运行 `to-issues`：

- 每个 Issue 是一个**垂直切片**（tracer bullet），端到端穿透所有集成层
- 标注 AFK（agent 可独立完成）/ HITL（需人工判断）
- 标注依赖关系（blocked by）
- 发布到 Issue Tracker 并打 `needs-triage` 标签

不强制——单人项目或 1-2 Unit 的小计划可跳过。用户拒绝时直接进入 `/dev:code`。

### 架构探索输入（`improve-codebase-architecture` 注入）

plan-engine 的研究子 Agent 在扫描代码库时，如果发现计划涉及的模块存在架构摩擦，使用精确词汇描述：

- **Module** — 有接口和实现的任何单元
- **Depth** — 接口后面隐藏了多少行为（深 = 高杠杆）
- **Seam** — 可以不编辑原处就改变行为的位置
- **Shallow module** — 接口几乎和实现一样复杂（反模式）

在计划中标注"此 Unit 包含架构深化"。不自动触发完整的 `/improve-codebase-architecture` 会话。

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Phase 1 requirements doc path, Phase 2 `DESIGN.md` (if exists) |
| **Output** | `docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`（frontmatter 包含 `status: active`）with R-Trace + Impl Units |
| **Next** | `/dev:code` (Phase 4), auto-continue when review gates are clear |

## Iron Law

> Plans resolve decisions, not code. The implementer starts confidently without the plan writing code for them.
