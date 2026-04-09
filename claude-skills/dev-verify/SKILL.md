---
name: dev-verify
description: "Use after implementation to run multi-layer quality verification. Detects diff content to auto-select which review personas and additive layers to activate. ce:review is always the core gate."
---

# Phase 5: Verify -- "质量关"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、审查结果均使用中文。
2. **工作区检查。** 确认在正确的 feature branch 上，避免审查错误的代码。
3. **Review 多轮循环。** `ce:review` interactive 模式执行"审查->修复->再审查"循环，直到零 P0/P1 或 3 轮上限。每个 additive layer 同样循环。

## Overview

Phase 5 is the quality gate. `ce:review` **detects** diff content and **auto-selects** 6-20+ persona reviewers. Additional verification layers are **auto-stacked** based on what changed.

Position in workflow: Phase 4 (code) -> **Phase 5** -> Phase 6 (delivery)

## When to Use

- Code changes are complete and committed
- Ready to validate before creating a PR or shipping

**Never skip Phase 5.**

## Scene Detection

### Core Review (always, auto-detected by `ce:review`)

`ce:review` reads the diff and auto-selects reviewers:

**Always-on (every review, no detection needed):**
- correctness, testing, maintainability, project-standards, agent-native, learnings

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
| Diff touches `views/`, `components/`, `*.tsx`, `*.css`, `*.html` | `test-browser` (affected routes) |
| 5+ UI files changed across multiple pages | `gstack/qa` (full site) + `design-review` |
| Diff touches `auth`, `payment`, `secret`, `token`, `*.pem` | `gstack/cso` (OWASP + STRIDE) |
| Diff touches `prompt`, `llm`, `ai`, `openai`, `anthropic` | `gstack/review` (LLM trust boundary) |
| Diff touches hot API paths, rendering loops, `*.sql` | `gstack/benchmark` (Core Web Vitals) |
| Diff touches `README`, `docs/`, `CONTRIBUTING`, CLI help text | `gstack/devex-review` |

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
