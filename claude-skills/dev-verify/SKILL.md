---
name: dev-verify
description: "Use after implementation is complete, before delivery, when the current diff needs quality review, tests, browser checks, security checks, or release readiness evidence."
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
2. **工作区前置（强制）。** 执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并调用 `using-git-worktrees` 创建工作区（路径 `<repo>/.worktrees/<task-name>/`；规范名与环境别名见 `claude-skills/README.md` 的 Skill Naming 表）。审查目标必须是当前任务的工作树（无论是否已 commit）。
3. **提交由用户触发。** 本阶段只读取代码、运行测试与审查工具、生成审查报告，不执行 `git commit` / `git push` / 创建 PR。审查中发现的修复同样不主动 commit；提交在 `/dev:ship`（Phase 6）由用户显式触发。
4. **总体审查门禁。** Phase 5 是完整 diff / 当前产物的 interactive 总体审查，不替代 Phase 4 的自动修复回路。Interactive review protocol 处理 `safe_auto` 之外的 `gated_auto` / `manual` 用户裁决，并执行"审查->修复/裁决->再审查"直到零未处理 P0/P1 或 3 轮上限。每个 additive layer 同样循环。

## Overview

Phase 5 is the quality gate for the whole current artifact. The interactive review protocol **detects** diff content and **auto-selects** 6-20+ persona reviewers. Additional verification layers are **auto-stacked** based on what changed. Phase 4 should already have run `mode:autofix`; Phase 5 reviews the complete result and handles residual or judgment-requiring findings.

Position in workflow: Phase 4 (code) -> **Phase 5** -> Phase 5.5 (pre-ship knowledge/supervision decision) -> Phase 6 (delivery)

## When to Use

- Code changes are complete (无论 staged/unstaged/committed 均可，本阶段不要求已 commit)
- Ready to validate before creating a PR or shipping

**Never skip Phase 5.**

## Quick Reference

| Need | Action |
|---|---|
| 核心质量门 | `references/review-interactive.md` |
| UI diff | `test-browser` or `dev-browser` |
| 多页 UI 变更 | `gstack-qa` + `gstack-design-review` fallback aware |
| 安全敏感 diff | `gstack-cso` |
| README/docs/CLI diff | `gstack-devex-review` |

## Common Mistakes

- core review 过了就宣布 PASS：还要跑命中的 additive layers
- 复用旧 PASS 证据：必须绑定当前 HEAD/tree/diff
- 因工具缺失跳过必需验证层：需要 fallback 或 STOP
- 在审查阶段顺手扩大修复范围

## Scene Detection

### Core Review (always, auto-detected)

The interactive review protocol reads the diff and auto-selects reviewers:

In Codex, reviewer-role fanout should use multiple reviewer agents when subagent/task spawning is available. Do not collapse to a single synthesized pass when the harness can spawn reviewer agents. If the harness truly cannot spawn reviewer agents, fall back to serial persona passes and explicitly report the degraded mode.

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
| 5+ UI files changed across multiple pages | `gstack-qa` (full site) + `gstack-design-review` **或** `dev-browser`（脚本化遍历多页路由） |
| Diff touches `auth`, `payment`, `secret`, `token`, `*.pem` | `gstack-cso` (OWASP + STRIDE) |
| Diff touches hot API paths, rendering loops, `*.sql` | `gstack-benchmark` (Core Web Vitals) |
| Diff touches `README`, `docs/`, `CONTRIBUTING`, CLI help text | `gstack-devex-review` |
| AI-generated code quality patterns detected | `slop-scan` (informational, non-blocking) |

**Additive layer degradation**: 每个 gstack-* 层在调用前检测可用性。若 `gstack-<name>` 未安装 -- 跳过该增强层。宣告："gstack-<name> 未安装 -- 跳过该增强层。"

## Workflow

1. **Interactive review protocol auto-detects and announces team:**
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

2. **REVIEW (Core): Execute the interactive review protocol from `references/review-interactive.md`** (完整独立审查, 多轮循环)
   - **Note**: Phase 4 必须已运行多次 autofix（批次后 + 收尾，快速 `safe_auto` 修复）。Phase 5 运行 interactive 模式做完整总体审查，覆盖 autofix 未处理的 `gated_auto` 和 `manual` 类问题，也可由用户手动用于审查当前环节产物。
   - 在 Codex 下，优先使用 reviewer-agent / task spawning 做角色审查 fanout；若支持并发则采用 bounded parallel。只有在当前 harness 明确拿不到 reviewer agents 时，才允许串行 persona passes。
   - **无计划文件时**（trivial fix、emergency hotfix、bug fix 直接进入）：省略 `plan:<path>` 参数，跳过 R-ID 需求追溯验证，仅执行代码质量审查。宣告："无计划文件 -- 跳过 R-ID 需求追溯，仅审查代码质量。"
   - Confidence filter: >= 0.60 (P0 >= 0.50)
   - safe_auto 自动修复，`gated_auto` / `manual` 交用户决策
   - 有计划文件时：R-ID 需求追溯验证
   - Residual issues -> todo system
   - **循环**: 审查 -> 修复 -> 再审查，直到零 P0/P1 或 3 轮上限或收敛

   **CORE CHECKPOINT:** Core review 零未处理 P0/P1 后继续 additive layers；此时还不能宣布 Phase 5 PASS。
   - 只有 core review 仍有 P0/P1、需要用户接受风险、或无法继续附加层时才发起 Decision GATE / STOP。

3. **If 未通过**: 修复发现（先验证再采纳），循环直到通过

4. **Auto-stack additive layers** based on detected signals. Announce (中文):
   - "Diff 涉及 auth + 前端 -- 叠加 CSO 安全审计和浏览器测试。"
   - "该 diff 不需要额外审查层。"
   - 每个 gstack-* 层调用前检测：若未安装则宣告 "gstack-<name> 未安装 -- 跳过该增强层。" 并继续。

5. **Resolve remaining todos** (inline logic):
   - 遍历审查中标记为 approved 的 todo 项
   - 对每个 todo：定位相关代码位置，应用修复
   - 若修复超出当前 cycle 范围或需要更多上下文，标记为 deferred 并记录原因
   - 宣告处理结果："已处理 N 个 todo，M 个延迟到下一 cycle。"

   **PHASE 5 PASS CHECKPOINT:** core review、所有命中的 additive layers、todo-resolve 都无 blocker，并且 PASS 证据绑定当前 HEAD/tree/diff。
   - PASS 时直接进入 Phase 5.5 交付前沉淀/自省判断；不要问"是否继续"。
   - 任一 additive layer 失败、缺少必须工具且无可接受 fallback、或 PASS 证据不能绑定当前 diff时，STOP。

6. **Next**: `/dev:flow` Phase 5.5 pre-ship knowledge/supervision decision, then `/dev:ship` (Phase 6). 默认自动进入 Phase 5.5；Phase 6 仍需 ship 授权。

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Code diff, plan file path (for R-ID verification) |
| **Output** | PASS verdict bound to current HEAD/tree/diff, safe_auto fixes applied, additive layers clear, todos resolved |
| **Next** | `/dev:flow` Phase 5.5, then `/dev:ship` (Phase 6); auto-continue to Phase 5.5 when PASS |

## Iron Laws

- **Evidence before assertions** -- never claim "tests pass" without running the command and reading output
- **Verify before adopting** -- review feedback must be verified against codebase before implementing

## 编码行为约束（本阶段强制）

审查与修复时同样遵循 Phase 4 的行为约束（完整规则见 `docs/ai-coding-workflow.md`）：

- **手术刀修改**：修复 review 发现时只改相关行，不扩大范围；不顺手重构；匹配现有风格。
- **孤儿清理**：仅清理本次修复产生的孤儿；不触碰既有 dead code。
- **明确假设 / 不懂就问**：审查反馈不清楚时 STOP 问用户或 reviewer；不要靠猜实现"可能意思"。**调用澄清工具时必须带推荐标识**——推荐项排第一并标 `(Recommended)`；无倾向时明说"无明确推荐"。
