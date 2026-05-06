---
name: dev-ship
description: "Use when code has passed verification and the user explicitly wants to enter delivery, merge, push, PR, or release work."
---

<SUPERVISE-CHECK>
执行前自检（Codex 环境必读，Claude Code 环境由 L1 hook 覆盖）：
1. 铁律 6（工作区）：运行 `git rev-parse --abbrev-ref HEAD` 和 `git rev-parse --show-toplevel`。若在 main/master 或不在 `<repo>/.worktrees/<task-name>/` → STOP，创建 worktree。
2. 铁律 7（提交触发）：本 phase 豁免 — `/dev:ship` 是唯一允许 commit/push/PR 的阶段。
3. 铁律 4（证据先行）：声称"完成/通过"前必须有测试命令的实际输出作为证据。
4. 合并后收尾：代码确认合入 main 后，自动删除当前任务 worktree；不得让 `.worktrees/` 下的临时工作区长期滞留。
</SUPERVISE-CHECK>

# Phase 6: Ship -- "上线"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、路由宣告均使用中文。
2. **工作区前置（强制）。** 执行 `git rev-parse --abbrev-ref HEAD` 和 `git rev-parse --show-toplevel` 检查当前分支与 worktree。若在 main/master 或不在 `<repo>/.worktrees/<task-name>/`，STOP 并要求用户先创建/切换到任务专属 worktree；禁止在主分支直接 commit/push。
3. **提交由用户显式触发。** 前置阶段（Phase 1-5）绝不主动 commit/push/PR。本阶段（Phase 6）是**唯一**可以 commit/push/创建 PR 的阶段，且要求用户已显式调用 `/dev:ship` 或明确说"提交/commit/push/PR/上线/deploy/合并到 main"。`/dev:ship` 只授权进入交付流程，不等于默认授权写 main。
4. **Review 多轮循环。** Path C 中 `gstack-ship` 的 pre-landing review 和 adversarial review 执行多轮循环。
5. **合并后自动删除当前工作区。** 一旦代码已合入 main（Path A 在用户明确授权下成功 push main，Path B/C 确认 merge），`dev-ship` 自动删除当前任务 worktree 并清理本地 feature branch。Merge-readiness GATE 必须提前展示将删除的 worktree 路径；合并成功后不再二次确认。
6. **确认收敛到 phase 级。** 只有以下情况才再次 GATE：`(a)` 路径存在多个有效选择且无法安全自动判定；`(b)` merge-readiness / deploy 报告出现 blocker、风险取舍或缺少关键信息；`(c)` 用户明确要求逐步确认。`mode:auto` 不是 ship 授权。除此之外，按已选路径直接执行到底。

## Overview

Phase 6 delivers verified code to production. It **detects** project type and upstream quality context to **auto-select** the right delivery path. Two paths share a single endpoint (land-deploy protocol) and then automatically remove the current task worktree after merge.

Position in workflow: Phase 5.5 (pre-ship knowledge/supervision decision) -> **Phase 6** -> Phase 7 (post-ship knowledge closeout)

## When to Use

- Phase 5 verification passed and Phase 5.5 pre-ship knowledge/supervision decision has no remaining required action
- Code is ready to ship

**Never skip Phase 6.**

## Quick Reference

| User intent | Path |
|---|---|
| 明确要求合并/push main | Path A |
| 明确要求创建 PR | Path B |
| 明确要求 release/bump/deploy | Path C |
| 只说 `/dev:ship` / `ship it` | 进入交付流程并 GATE 选路径；不默认写 main |

## Common Mistakes

- 把 `/dev:ship` 或 `mode:auto` 当成 Path A 授权
- 在没有当前 diff PASS 证据时交付
- 在主 checkout 或非 `.worktrees/` 路径上执行交付
- merge 后清理 worktree 前不验证删除目标

## Scene Detection

**Signal 0: 主干同步（强制前置）**
- `git fetch origin main && git rev-list --count HEAD..origin/main` -> 落后 >0 则先 rebase
- rebase 有冲突时协助解决，解决后继续

**Signal 1: 用户是否显式要求发布 / 版本变更 / 自动部署?**
- 用户明确说"release"/"版本发布"/"bump version"/"更新 CHANGELOG"/"自动部署"/"deploy to prod" -> Path C（发布路径）
- 其他情况 -> check Signal 2

**Signal 2: 用户是否显式要求合并到 main?**
- 用户明确说"合并到 main"/"push main"/"squash 到 main" -> Path A (squash 合并回 main)
- 用户说"创建 PR"/"open PR"/"pull request" -> Path B (PR 路径)
- 其他情况 -> GATE 选择 Path B (推荐) / Path A / Path C；不得静默写 main

**Signal 3: What upstream quality was already applied?**
- Phase 4/5 review evidence exists for current HEAD/tree/diff (check `.context/compound-engineering/ce-review/` or equivalent current-diff evidence) -> upstream quality confirmed
- No review evidence -> STOP，先回 `/dev:verify`

**Signal 4: PR feedback pending?**
- Run `gh pr view --json reviewDecision,comments` on current branch
- Unresolved review threads exist -> prepend `pr-comment-resolver`

**Signal 5: UI changes in diff?**
- Scan diff for `views/`, `components/`, `*.tsx`, `*.css`, `*.html` -> add `feature-video` + 部署后 `dev-browser` 烟测

## Routing

```
验证通过且完成 Phase 5.5 交付前判断的代码
  |
  +-- [用户显式要求合并/push main] --------------------> Path A: Squash 合并回 main
  |   squash merge + 中文 commit message，保持主干干净 -> 自动删除当前 worktree
  |
  +-- [用户显式要求 PR] ------------------------------> Path B: PR 路径
  |   commit-push-pr protocol -> gstack-land-and-deploy -> 自动删除当前 worktree
  |
  +-- [用户显式要求 release / bump / deploy] ---------> Path C: gstack 完整发布
      gstack-ship -> gstack-document-release -> gstack-land-and-deploy -> 自动删除当前 worktree
```

### Pre-delivery (auto-detected)

```
  +-- [PR has unresolved threads] -> pr-comment-resolver first
  +-- [Diff has UI files] ---------> feature-video in parallel
```

## Workflow

1. **Detect scene** and announce (中文):
   - "用户明确要求合并到 main -- squash 合并回 main，一个干净的中文 commit。"
   - "用户要求创建 PR -- 使用 PR 路径。"
   - "用户明确要求版本发布/自动部署 -- 使用完整发布流程含 CHANGELOG。"
   - "主干落后 8 个提交 -- 先 rebase 同步。"
   - "PR 有 3 个未解决的审查线程 -- 先处理反馈。"
   - "没有 Phase 5 review 证据 -- 先回 `/dev:verify`。"

2. **Pre-delivery** (if detected):
   - Run `pr-comment-resolver` for pending PR comments

3. **Execute detected path**

   **Path A: Squash 合并回 main（仅用户明确要求）**

   主干保持线性、干净、每个 commit 对应一个完整功能。

   ```bash
   # 0. 记录当前任务工作区
   feature_branch=$(git branch --show-current)
   task_worktree=$(git rev-parse --show-toplevel)
   main_worktree=$(git worktree list --porcelain | sed -n 's/^worktree //p' | head -n 1)

   # 1. 强制主干同步
   git fetch origin main
   git rebase origin/main

   # 2. 回到 main 所在工作区
   cd "$main_worktree"
   git checkout main && git pull origin main

   # 3. Squash merge
   git merge --squash "$feature_branch"

   # 4. 中文 commit message
   git commit -m "<简洁中文描述：为什么变，不是变了什么>"

   # 5. Push
   git push origin main

   # 6. 清理
   git worktree remove "$task_worktree"
   git branch -D "$feature_branch"
   ```

   执行规则：
   - 若用户已明确要求"提交并合并到 main"或等价表述，且路径唯一、commit message 无歧义、`task_worktree` 删除目标清晰，则直接执行。
   - 若用户只说 `/dev:ship`、"ship it" 或 `mode:auto`，不得进入 Path A；先 GATE 选择 PR 路径或要求明确 main 授权。
   - 只有在 commit message 难以确定、目标分支/路径不明确、或主干同步后出现新 blocker 时才停下 GATE。

   **GATE(仅在需要时): 展示 squash diff 摘要、拟定的 commit message、将删除的 `task_worktree` 路径。**

   Commit message 规范：
   - 第一行：简洁中文，说明意图（为什么变），不超过 50 字
   - 可选 body：补充上下文，仅在变更需要叙事时添加
   - 不加 AI 署名 footer，除非用户要求

   **Path B: PR 路径（仅在用户显式要求时）**

   Execute the commit-push-pr protocol from `references/commit-push-pr-protocol.md`:
   - Delegates to PR description generation
   - Auto-detects conventions from repo history
   - Logical commit splitting (file-level)
   - [+ feature-video in parallel if UI detected]

   Then execute the gstack-land-and-deploy protocol from `references/land-deploy-protocol.md`:
   - CI wait -> merge-readiness report -> merge -> deploy -> canary

   dev-ship cleanup:
   - Merge 确认后自动删除当前任务 worktree + 本地 feature branch

   **Path C: gstack 完整发布路径（仅在用户显式要求 release / bump / deploy 时）**

   OPTIONAL enhancements (degradation: 若 `gstack-ship` 未安装 -- 回退到 Path B 流程):
   ```
   gstack-ship
     - Merge base branch -> parallel tests -> coverage audit (60%/80%)
     - Plan completion audit + scope drift detection
     - REVIEW: pre-landing code review (auto, 最多 3 轮)
     - REVIEW: adversarial review -- Claude + Codex (auto, 最多 3 轮)
     - Version bump + CHANGELOG generation
     - Bisectable commits (dependency-ordered)
     [+ feature-video in parallel if UI detected]
   gstack-document-release
     - Cross-references all docs against diff
     - Auto-updates factual changes, asks on narrative changes
   ```

   Then execute the gstack-land-and-deploy protocol from `references/land-deploy-protocol.md`:
   - CI wait -> merge-readiness report -> merge -> deploy -> canary

   dev-ship cleanup:
   - Merge 确认后自动删除当前任务 worktree + 本地 feature branch

4. **Land-deploy protocol auto-detects** deployment platform and canary depth:
   - Platform: from `fly.toml` / `vercel.json` / `render.yaml` / `Procfile` / GitHub Actions
   - **Greenfield 检测**: 如果没有任何部署配置文件，宣告："未检测到部署配置 -- 运行 `gstack-setup-deploy` 创建部署设置。"
   - Canary depth by diff type: docs->skip, config->smoke, backend->console, frontend->full

   执行规则：
   - merge-readiness report 是 Phase 6 默认保留的**单一交付关卡**。
   - 若报告无 blocker、路径唯一、无需产品取舍，则通过该关卡后直接继续。
   - 若报告出现 blocker、缺失部署配置、未解决线程或需要用户承担风险的事项，STOP 并展示问题。

5. **过程文件收尾(默认不阻塞)**:
   扫描本任务相关的过程文件。默认行为：只在状态报告里列出候选文件，不阻塞交付。
   只有用户明确要求"归档过程文件"时，才进入处理分支（归档到 `docs/archive/<year>/` / wiki ingest / 保持原位）。

6. **自动删除当前工作区(强制收尾)**:
   代码已合入 main 后，自动删除当前任务 worktree。

   安全约束:
   - 若 `task_worktree` 等于 `main_worktree`，或路径不在 `<repo>/.worktrees/` 下，STOP 并报告
   - 删除前运行 `git -C "$task_worktree" status --porcelain`；若有未提交改动，暂停并报告
   - Path A 只有在 `git push origin main` 成功后才允许 `git branch -D`
   - Path B/C 只有在 land-deploy protocol 确认 PR 已 merge 后才执行清理

7. **Next**: `/dev:learn` (Phase 7)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Verified code diff (Phase 5 PASS) |
| **Output** | 用户明确 main 授权时 squash 合并到 main，或 PR + 部署；合并后自动删除当前任务 worktree |
| **Next** | `/dev:learn` (Phase 7) |

## Iron Law

> Every failure point offers a rollback option. Explicit ship intent authorizes the normal path; only unresolved blockers or ambiguous choices reopen a gate.
