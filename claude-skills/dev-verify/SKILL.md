---
name: dev-verify
description: "Use after implementation to run multi-layer quality verification. Detects diff content to auto-select which review personas and additive layers to activate. ce:review is always the core gate."
---

<SUPERVISE-CHECK>
执行前自检（Codex 环境必读，Claude Code 环境由 L1 hook 覆盖）：
1. 铁律 6（工作区）：运行 `git rev-parse --abbrev-ref HEAD`。若在 main/master 且不在 `.worktrees/` 子路径 → STOP，创建 worktree。
2. 铁律 7（提交触发）：本 phase 禁止 `git commit` / `git push` / `gh pr create`。提交仅在 `/dev:ship` 中由用户触发。
3. 铁律 4（证据先行）：声称"完成/通过"前必须有测试命令的实际输出作为证据。
</SUPERVISE-CHECK>

# Phase 5: Verify -- "质量关"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、审查结果均使用中文。
2. **工作区前置（强制）。** 执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并调用 `compound-engineering:git-worktree`（或 `superpowers:using-git-worktrees`）创建工作区。审查目标必须是当前任务的工作树（无论是否已 commit）。
3. **提交由用户触发。** 本阶段只读取代码、运行测试与审查工具、生成审查报告，不执行 `git commit` / `git push` / 创建 PR。审查中发现的修复同样不主动 commit；提交在 `/dev:ship`（Phase 6）由用户显式触发。
4. **Review 多轮循环。** `ce:review` interactive 模式执行"审查->修复->再审查"循环，直到零 P0/P1 或 3 轮上限。每个 additive layer 同样循环。

## Overview

Phase 5 is the quality gate. `ce:review` **detects** diff content and **auto-selects** 6-20+ persona reviewers. Additional verification layers are **auto-stacked** based on what changed.

Position in workflow: Phase 4 (code) -> **Phase 5** -> Phase 6 (delivery)

## When to Use

- Code changes are complete (无论 staged/unstaged/committed 均可，本阶段不要求已 commit)
- Ready to validate before creating a PR or shipping

**Never skip Phase 5.**

## Scene Detection

### Core Review (always, auto-detected by `ce:review`)

`ce:review` reads the diff and auto-selects reviewers:

**Always-on (every review, no detection needed):**
- correctness, testing, maintainability, project-standards, agent-native, learnings
- **Cross-model adversarial**: Claude + Codex always dispatched in parallel; large diffs (200+ lines) add Codex structured P1 gate

**Auto-detected by diff content:**

| Detected Signal in Diff | Auto-activated Persona |
|---|---|
| Files in `auth/`, `login`, `session`, `permission` | `security-reviewer` |
| Files with DB queries, `cache`, `async`, `worker` | `performance-reviewer` |
| Files in `routes`, `serializer`, `*.proto`, `openapi` | `api-contract-reviewer` |
| Files in `db/migrate/`, `schema`, backfill scripts | `data-migrations-reviewer` + `schema-drift-detector` |
| Files with `rescue`, `retry`, `timeout`, `circuit` | `reliability-reviewer` |
| Diff >= 50 changed lines OR touches auth/payments | `adversarial-reviewer` |
| Files in Rails `app/controllers/`, `app/models/` | `kieran-rails-reviewer` + `dhh-rails-reviewer` |
| Files `*.py` | `kieran-python-reviewer` |
| Files `*.ts`, `*.tsx` | `kieran-typescript-reviewer` |
| Files with Stimulus/Turbo controllers, DOM events | `julik-frontend-races-reviewer` |
| PR has existing review comments | `previous-comments-reviewer` |

### Additive Layers (auto-detected by diff file paths)

| Detected Signal | Auto-stacked Layer |
|---|---|
| Diff touches `views/`, `components/`, `*.tsx`, `*.css`, `*.html` | `test-browser` (affected routes) **或** `dev-browser`（轻量 stdin 脚本，跨 harness 通用） |
| 5+ UI files changed across multiple pages | `gstack/qa` (full site) + `design-review` **或** `dev-browser`（脚本化遍历多页路由） |
| Diff touches `auth`, `payment`, `secret`, `token`, `*.pem` | `gstack/cso` (OWASP + STRIDE) |
| Diff touches `prompt`, `llm`, `ai`, `openai`, `anthropic` | `gstack/review` (LLM trust boundary) |
| Diff touches hot API paths, rendering loops, `*.sql` | `gstack/benchmark` (Core Web Vitals) |
| Diff touches `README`, `docs/`, `CONTRIBUTING`, CLI help text | `gstack/devex-review` |
| AI-generated code quality patterns detected | `slop-scan` (informational, non-blocking) |

## Workflow

1. **`ce:review` auto-detects and announces team:**
   ```
   Review team:
   - correctness (always)
   - testing (always)
   - maintainability (always)
   - project-standards (always)
   - agent-native (always)
   - learnings (always)
   - security -- new endpoint in routes.rb accepts user input
   - kieran-rails -- controller changed in app/controllers/
   - adversarial -- diff is 120 lines touching auth
   ```

2. **REVIEW (Core): `/ce:review plan:<plan-path>`** (interactive mode, 完整独立审查, 多轮循环)
   - **Note**: Phase 4 已运行 `ce:review mode:autofix`（快速 safe_auto 修复）。Phase 5 运行 interactive 模式做完整审查，覆盖 autofix 未处理的 `gated_auto` 和 `manual` 类问题。
   - **无计划文件时**（trivial fix、emergency hotfix、bug fix 直接进入）：省略 `plan:<path>` 参数，跳过 R-ID 需求追溯验证，仅执行代码质量审查。宣告："无计划文件 -- 跳过 R-ID 需求追溯，仅审查代码质量。"
   - Confidence filter: >= 0.60 (P0 >= 0.50)
   - safe_auto 自动修复，`gated_auto` / `manual` 交用户决策
   - 有计划文件时：R-ID 需求追溯验证
   - Residual issues -> todo system
   - **循环**: 审查 -> 修复 -> 再审查，直到零 P0/P1 或 3 轮上限或收敛

   **GATE: PASS 裁决（零 P0/P1）。**

3. **If 未通过**: 修复发现（先验证再采纳），循环直到通过

4. **Auto-stack additive layers** based on detected signals. Announce (中文):
   - "Diff 涉及 auth + 前端 -- 叠加 CSO 安全审计和浏览器测试。"
   - "该 diff 不需要额外审查层。"

5. **Run `todo-resolve`** to batch-process remaining todos

6. **Next**: `/dev:ship` (Phase 6)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Code diff, plan file path (for R-ID verification) |
| **Output** | PASS verdict, safe_auto fixes applied, todos resolved |
| **Next** | `/dev:ship` (Phase 6) |

## Iron Laws

- **Evidence before assertions** -- never claim "tests pass" without running the command and reading output
- **Verify before adopting** -- review feedback must be verified against codebase before implementing

## 编码行为约束（本阶段强制）

审查与修复时同样遵循 Phase 4 的行为约束（完整规则见 `docs/ai-coding-workflow.md`）：

- **手术刀修改**：修复 review 发现时只改相关行，不扩大范围；不顺手重构；匹配现有风格。
- **孤儿清理**：仅清理本次修复产生的孤儿；不触碰既有 dead code。
- **明确假设 / 不懂就问**：审查反馈不清楚时 STOP 问用户或 reviewer；不要靠猜实现"可能意思"。**调用澄清工具时必须带推荐标识**——推荐项排第一并标 `(Recommended)`；无倾向时明说"无明确推荐"。
