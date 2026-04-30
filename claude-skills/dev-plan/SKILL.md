---
name: dev-plan
description: "Use when a requirements doc exists and it is time to create an implementation plan. Detects scope to select review depth: autoplan for large features, plan-eng-review for ordinary work. Always uses ce-plan as the sole plan creator."
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
4. **Review 多轮门禁。** `document-review` 和 `plan-eng-review` 均是进入 `/dev:code` 前的门禁：执行"审查->修复/用户裁决->再审查"，直到零未处理 P0/P1、达到 3 轮上限、或连续两轮发现相同问题后升级给用户裁决。

## Overview

Phase 3 transforms requirements into an executable plan. `ce-plan` is the sole creator (decisions, not code). The skill **detects** plan scope and **auto-selects** the right review depth. Plans produce Implementation Units, Requirements Trace, and Test Scenarios consumed by `ce-work` in Phase 4.

Position in workflow: Phase 2 (design) -> **Phase 3** -> Phase 4 (implementation)

## When to Use

- Requirements doc exists (`docs/brainstorms/*-requirements.md`)
- Work is non-trivial (more than a one-file fix)

**Skip when:** Plan already exists and has review-pass evidence for this work item (`document-review` passed and `plan-eng-review`/selected Layer 2 review cleared). A freshly written plan file without completed review gates does **not** qualify.

## Scene Detection

**Signal 1: Does a plan already exist?**
- Search `docs/plans/` for plans matching the topic (within 30 days)
- If found with `status: active` and review-pass evidence present -> SKIP, go to `/dev:code`
- If found with `status: active` but missing `document-review` pass or Layer 2 REVIEW REPORT -> resume at review step
- If found with `status: completed` -> SKIP or create new plan (ask user)

`document-review` pass evidence means one of:
- the current `/dev:plan` invocation just ran `document-review` on this exact plan path and cleared Layer 1, or
- the plan file already records the last Layer 1 result / override in `Deferred/Open Questions` or `Review Notes`, and there have been no material edits since that review.

Plan file existence by itself is **not** review-pass evidence.

**Signal 2: Does `DESIGN.md` exist? (from Phase 2)**
- Yes -> `ce-plan` will reference design tokens; `plan-design-review` should run
- No -> skip design review dimension

**Signal 3: Plan scope (auto-detected by `ce-plan` after creating the plan)**
- Count Implementation Units produced:
  - 1-2 units -> Small scope
  - 3-9 units -> Standard scope
  - 10+ units -> Large scope
- Check if units touch developer-facing surfaces (API, CLI, SDK, docs):
  - Yes -> add DX review

## Routing

### Plan Creation (always the same)

`ce-plan` -- parallel research sub-agents, R-ID trace, Implementation Units, Test Scenarios.

### Review Depth (auto-selected after plan creation)

```
Plan created by ce-plan
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

2. **Run `ce-plan`** with requirements doc path
   - Parallel research: repo-research, learnings, best-practices, framework-docs, **`/dev:wiki-search`**
   - **Wiki Query**: 调用 `/dev:wiki-search` 扫项目 `wiki/index.md` + 全局 `~/.claude/wiki/index.md`,获取既有模式、决策、相关知识,按 caller 推荐顺序读页面,注入 plan context。
   - Output: `docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`（frontmatter 必须含 `status: active`）
   - Scope auto-classified: Lightweight / Standard / Deep
   - `ce-plan` 写出 plan 文件后**不算完成**。即使它展示了 handoff 菜单或说"下一步可做 review / code"，`dev-plan` 也必须继续执行自己的 Layer 1 / Layer 2 gates。

3. **Post-`ce-plan` enforcement: resolve plan path and enter Layer 1 immediately**
   - 读取 `ce-plan` 产出的绝对 plan 路径。若没产出 plan 文件，STOP 并重新运行 `ce-plan`；不得进入 review depth 检测。
   - Ignore `ce-plan`'s post-generation menu as a completion signal. In `/dev:plan`, plan creation is only the handoff into review gates.
   - 若是新创建或刚被 `ce-plan` 改写的计划：立刻进入 Layer 1，不要向用户输出"如果你要，我继续做 review"之类的可选措辞。

4. **REVIEW GATE (Layer 1): `document-review` 多轮门禁**
   - 多人格审查: coherence / feasibility / scope-guardian（`document-review` 按文档内容自动叠加其他 persona）。
   - 在 Codex 下，若 reviewer-agent / task spawning 可用，必须按 reviewer role 分发为多 agent 审查（可 bounded parallel），不要在能力可用时退化成单线程综合。
   - 只有在当前 harness 明确拿不到 reviewer agents 时，才允许降级为串行 persona passes；降级时仍要保留按 role 分开的 findings，并在状态报告里显式标注。
   - 默认直接调用 `document-review <plan-path>`。只有在调用链是 pipeline / disable-model-invocation / `mode:auto` 风格的非交互上下文时，才改用 `document-review mode:headless <plan-path>`。
   - `safe_auto` 修复自动应用，`gated_auto` / `manual` 发现交用户判断；Codex 没有阻塞提问工具时，用编号选项停下等待用户，不得静默选项。
   - **循环**: 审查 -> 修复/用户裁决 -> 再审查，直到零未处理 P0/P1，或达到 3 轮上限，或连续两轮发现相同 P0/P1。
   - 若达到上限或收敛仍有 P0/P1：STOP，报告阻塞；只有用户显式接受风险并把理由写入计划的 Deferred/Open Questions 或 Review Notes 后，才允许继续 Layer 2。
   - If `document-review` 只输出了"review 可作为下一步"、没有真正执行到本计划文件上，视为 Layer 1 未开始，立即重新调用，不得继续。

   **GATE: 计划文件存在且有 `document-review` 通过证据（零未处理 P0/P1 或用户记录化 override）。**

5. **Detect review depth** from plan's Implementation Unit count (Signal 3). Announce (中文):
   - "计划有 12 个单元 -- 运行完整 autoplan 审查流水线。"
   - "计划有 5 个单元含 UI -- 运行工程 + 设计审查。"
   - "计划有 2 个单元 -- 仅运行工程审查。"

6. **REVIEW (Layer 2): 多视角计划审查 多轮循环** (auto-selected)
   - Large: `gstack-autoplan` (CEO -> Design -> Eng -> DX, serial)
   - Standard: `gstack-plan-eng-review` (required gate) + `gstack-plan-design-review` (if UI)
   - Small: `gstack-plan-eng-review` only
   - Developer-facing: + `gstack-plan-devex-review`
   - **循环**: 每个审查技能内部执行多轮修复，直到零未处理 P0/P1、达到上限、或连续两轮发现相同问题。
   - 若 `gstack-*` 在当前环境未安装（`dev-doctor` 会报告），Codex 路径优先保留多 agent 角色审查：至少运行一轮 `document-review` reviewer fanout 覆盖 coherence/feasibility/scope/design/security/product/adversarial，并明确还缺少 eng-review 判断；之后由用户选择手动补 eng-review 或记录 override。不得直接进入 `/dev:code`。

   **GATE: GSTACK REVIEW REPORT 写入计划文件。`plan-eng-review` CLEARED（零未处理 P0/P1 或用户记录化 override）。**

7. **Next**: `/dev:code` (Phase 4)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Phase 1 requirements doc path, Phase 2 `DESIGN.md` (if exists) |
| **Output** | `docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`（frontmatter 包含 `status: active`）with R-Trace + Impl Units |
| **Next** | `/dev:code` (Phase 4) |

## Iron Law

> Plans resolve decisions, not code. The implementer starts confidently without the plan writing code for them.
