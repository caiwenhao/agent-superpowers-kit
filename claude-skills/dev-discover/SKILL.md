---
name: dev-discover
description: "Use when starting any new work: a feature idea, vague request, product question, or 'I want to build X'. Detects intent clarity and routes to the right discovery skill, always producing a requirements doc with R-IDs before planning begins."
---

<SUPERVISE-CHECK>
执行前自检（Codex 环境必读，Claude Code 环境由 L1 hook 覆盖）：
1. 铁律 6（工作区）：运行 `git rev-parse --abbrev-ref HEAD`。若在 main/master 且不在 `.worktrees/` 子路径 → STOP，创建 worktree。
2. 铁律 7（提交触发）：本 phase 禁止 `git commit` / `git push` / `gh pr create`。提交仅在 `/dev:ship` 中由用户触发。
3. 铁律 4（证据先行）：声称"完成/通过"前必须有测试命令的实际输出作为证据。
</SUPERVISE-CHECK>

# Phase 1: Discover -- "做什么"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、路由宣告均使用中文。
2. **工作区前置（强制）。** 在创建任何文档或代码之前，执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并调用 `using-git-worktrees` 创建工作区后再继续（路径 `<repo>/.worktrees/<task-name>/`；规范名与环境别名见 `claude-skills/README.md` 的 Skill Naming 表）。
3. **提交由用户触发。** 本阶段只写文件、运行只读命令，不执行 `git commit` / `git push` / 创建 PR。提交动作只在 `/dev:ship`（Phase 6）由用户显式触发。
4. **Review 多轮门禁。** Route C/Deep 或高风险需求必须运行 `document-review`，并执行"审查->修复->再审查"循环，直到零未处理 P0/P1、达到 3 轮上限、或连续两轮发现相同问题后升级给用户裁决。

## Overview

Phase 1 is the mandatory entry point for all new work. It **detects** user intent clarity, **routes** to the best discovery skill, and **converges** all paths onto `ce-brainstorm` as the single exit, producing a requirements document with traceable R-IDs (R1, R2, R3...).

Position in workflow: **Phase 1** -> Phase 2 (design) or Phase 3 (planning)

## When to Use

- Starting a new feature, improvement, or product idea
- User describes something to build but scope is unclear
- User wants to explore what is worth building

**Skip when:** An approved requirements doc (`docs/brainstorms/*-requirements.md`) already exists for this work item.

## Scene Detection

Analyze user input to classify intent. Check these signals in order:

**Signal 0: Wiki Query (前置步骤)**
- 调用 `/dev:wiki-search`,关键词来自用户 prompt;它会扫项目 `wiki/index.md` + 全局 `~/.claude/wiki/index.md` 并按相关性返回页面清单(只读 grep,无 LLM)
- If relevant pages found -> read them and inject as brainstorm context
- Announce (中文): "Wiki 中找到 N 篇相关页面，注入 brainstorm 上下文。" or "Wiki 中无相关知识。"
- This step is informational — it enriches context but does not change routing

**Signal 1: Is there an existing requirements doc?**
- Search `docs/brainstorms/` for `*-requirements.md` matching the topic (within 30 days)
- If found and approved -> SKIP Phase 1, go to `/dev:design` or `/dev:plan`
- If found but incomplete -> RESUME, run `ce-brainstorm` on existing doc

**Signal 2: Does the user have a direction?**
- No direction detected (keywords: "ideas", "what should I", "improve", "suggest", "don't know what") -> Route A: Ideate first
- Has direction but uncertain about value (keywords: "worth building", "validate", "is this a good idea", "should I", "market") -> Route B: Validate first
- Has direction with clear scope -> Route C or D (see Signal 3)

**Signal 3: How specific is the request?**
- Multi-faceted / cross-cutting / 3+ independent concerns -> Route C: Standard/Deep brainstorm
- Single concern / clear boundary / small scope -> Route D: Lightweight brainstorm

**Signal 4: Is Phase 1 doc-review mandatory?**
After `ce-brainstorm` writes the requirements doc, require `document-review` when any signal is true:
- Route C / Deep brainstorm
- Requirements count >8 R-IDs
- External upstream/API/SDK integration, public endpoint, model alias, or protocol contract
- Auth, tokens, credentials, private assets, user data, billing, pricing, quota, or audit logs
- User explicitly asks for review

Route D stays opt-in only when none of these signals apply.

## Routing

```
User Input
  |
  +-- [No direction] -------> Route A: ce-ideate -> ce-brainstorm
  |   "give me ideas"
  |   "what should I improve"
  |
  +-- [Has direction,  -----> Route B: gstack-office-hours -> ce-brainstorm

  |    uncertain value]
  |   "is this worth building"
  |   "validate my idea"
  |
  +-- [Has direction,  -----> Route C: ce-brainstorm (Standard/Deep)
  |    multi-faceted]
  |   "add user auth with OAuth and RBAC"
  |
  +-- [Has direction,  -----> Route D: ce-brainstorm (Lightweight)
      clear & small]
      "add a logout button"
```

All routes converge to `ce-brainstorm` as the single exit.

## Workflow

1. **Detect scene** using the signals above. Announce the detected route (中文):
   - "输入是探索性的，没有明确方向 -- 先进行创意发散。"
   - "输入有方向但需要验证价值 -- 运行 Office Hours。"
   - "输入描述了一个多面向的功能 -- 启动标准头脑风暴。"
   - "输入清晰且范围小 -- 运行轻量头脑风暴。"

2. **Execute the detected route**

   **Route A**: Run `ce-ideate` -> user selects direction -> feed into `ce-brainstorm`
   **Route B**: Run `gstack-office-hours` -> validated direction -> feed into `ce-brainstorm`
   **Route C/D**: Run `ce-brainstorm` directly (scope auto-assessed by `ce-brainstorm` itself)

3. **REVIEW GATE: `document-review`（条件强制）**
   - Mandatory signals 命中时：立即运行 `document-review <requirements-path>`，不得只在 handoff 菜单里提供 opt-in。
   - 无 mandatory signals 时：保留 opt-in，由 `ce-brainstorm` Phase 4 handoff 提供选项。
   - 多人格审查覆盖 coherence / feasibility / product-lens / design-lens / security-lens / scope-guardian / adversarial。
   - 在 Codex 下，若 reviewer-agent / task spawning 可用，必须按角色分发为多 agent 审查（可 bounded parallel）。不要在能力可用时退化成单线程综合结论。
   - 只有在当前 harness 明确拿不到 reviewer agents 时，才允许降级为串行 persona passes；即便降级，也要保留按 reviewer role 分开的发现，并在状态报告里明确写出"已降级为串行角色审查"。
   - `safe_auto` 修复自动应用，`gated_auto` / `manual` 发现交用户判断；Codex 没有阻塞提问工具时，用编号选项停下等待用户，不得静默选项。
   - **循环**: 审查 -> 修复/用户裁决 -> 再审查，直到零未处理 P0/P1，或达到 3 轮上限，或连续两轮发现相同 P0/P1。
   - 若达到上限或收敛仍有 P0/P1：STOP，报告阻塞；只有用户显式接受风险并把理由写入需求文档的 Deferred/Open Questions 后，才允许进入 `/dev:plan`。

   **CHECKPOINT:** 需求文档必须存在；Mandatory review 命中时，必须有 `document-review` 通过证据（零未处理 P0/P1 或用户记录化 override）。
   - 若需求来自用户明确指令，且没有 open questions / scope tradeoff / P0/P1，报告状态后直接进入下一 phase。
   - 只有需求包含未决范围、多个合理方向、产品取舍、或需要用户批准 override 时，才发起 Decision GATE。
   - 不要在需求已清晰且下一步唯一明确时问"是否继续 Phase 2/3"。

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
