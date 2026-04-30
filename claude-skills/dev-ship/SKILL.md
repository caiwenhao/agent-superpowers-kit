---
name: dev-ship
description: "Use when Phase 5 has passed and code is ready to deliver. Detects project type and upstream quality to auto-select lightweight (CE) or full (gstack) delivery path. Both end with land-and-deploy and automatic current worktree cleanup after merge."
---

<SUPERVISE-CHECK>
执行前自检（Codex 环境必读，Claude Code 环境由 L1 hook 覆盖）：
1. 铁律 6（工作区）：运行 `git rev-parse --abbrev-ref HEAD`。若在 main/master 且不在 `.worktrees/` 子路径 → STOP，创建 worktree。
2. 铁律 7（提交触发）：本 phase 豁免 — `/dev:ship` 是唯一允许 commit/push/PR 的阶段。
3. 铁律 4（证据先行）：声称"完成/通过"前必须有测试命令的实际输出作为证据。
4. 合并后收尾：代码确认合入 main 后，自动删除当前任务 worktree；不得让 `.worktrees/` 下的临时工作区长期滞留。
</SUPERVISE-CHECK>

# Phase 6: Ship -- "上线"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、路由宣告均使用中文。
2. **工作区前置（强制）。** 执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并要求用户先创建/切换到 feature branch；禁止在主分支直接 commit/push。
3. **提交由用户显式触发。** 前置阶段（Phase 1-5）绝不主动 commit/push/PR。本阶段（Phase 6）是**唯一**可以 commit/push/创建 PR 的阶段，且要求用户已显式调用 `/dev:ship` 或明确说"提交/commit/push/PR/上线"。这类指令一旦给出，就视为**对所选交付路径的整体授权**；不要把授权拆成 commit / push / merge / deploy 多次重复确认。
4. **Review 多轮循环。** Path B 中 `gstack-ship` 的 pre-landing review 和 adversarial review 执行多轮循环。
5. **合并后自动删除当前工作区。** 一旦代码已合入 main（Path A 成功 push main，Path B/C 的 `land-and-deploy` 确认 merge），`dev-ship` 自动删除当前任务 worktree 并清理本地 feature branch。Merge-readiness GATE 必须提前展示将删除的 worktree 路径；合并成功后不再二次确认。
6. **确认收敛到 phase 级。** 只有以下情况才再次 GATE：`(a)` 路径存在多个有效选择且无法安全自动判定；`(b)` merge-readiness / deploy 报告出现 blocker、风险取舍或缺少关键信息；`(c)` 用户明确要求逐步确认。除此之外，按已选路径直接执行到底。

## Overview

Phase 6 delivers verified code to production. It **detects** project type and upstream quality context to **auto-select** the right delivery path. Two paths share a single endpoint (`land-and-deploy`) and then automatically remove the current task worktree after merge.

Position in workflow: Phase 5 (verify) -> **Phase 6** -> Phase 7 (knowledge)

## When to Use

- Phase 5 verification passed
- Code is ready to ship

**Never skip Phase 6.**

## Scene Detection

**Signal 0: 主干同步（强制前置）**
- `git fetch origin main && git rev-list --count HEAD..origin/main` -> 落后 >0 则先 rebase
- rebase 有冲突时协助解决，解决后继续

**Signal 1: Does the project use versioning?**
- `VERSION` file exists OR `package.json` has `version` field -> versioned project -> Path C
- No version file -> check Signal 2

**Signal 2: 用户是否显式要求 PR?**
- 用户说"创建 PR"/"open PR"/"pull request" -> Path B (PR 路径)
- 项目有 CI/CD 依赖 PR（检测 `.github/workflows/` 中有 `pull_request` trigger）-> 建议 Path B
- 其他情况 -> Path A (squash 合并回 main，默认)

**Signal 3: What upstream quality was already applied?**
- `ce-review` ran in Phase 4/5 (check `.context/compound-engineering/ce-review/` for recent run) -> upstream quality confirmed
- No ce-review evidence + versioned project -> Path C (needs ship's built-in review)

**Signal 4: PR feedback pending?**
- Run `gh pr view --json reviewDecision,comments` on current branch
- Unresolved review threads exist -> prepend `pr-comment-resolver`

**Signal 5: UI changes in diff?**
- Scan diff for `views/`, `components/`, `*.tsx`, `*.css`, `*.html` -> add `feature-video` + 部署后 `dev-browser` 烟测（关键路由 + 控制台无 error）

## Routing

```
验证通过的代码 (from Phase 5)
  |
  +-- [默认] -----------------------------------------> Path A: Squash 合并回 main
  |   squash merge + 中文 commit message，保持主干干净 -> 自动删除当前 worktree
  |
  +-- [用户显式要求 PR / 团队协作项目] ----------------> Path B: PR 路径
  |   git-commit-push-pr -> land-and-deploy -> 自动删除当前 worktree
  |
  +-- [版本化项目 (有 VERSION 文件)] ------------------> Path C: gstack 完整发布
  |   ship -> document-release -> land-and-deploy -> 自动删除当前 worktree
  |
  +-- [无上游审查证据] --------------------------------> Path C: gstack 完整发布
```

### Pre-delivery (auto-detected)

```
  +-- [PR has unresolved threads] -> resolve-pr-feedback first
  +-- [Diff has UI files] ---------> feature-video in parallel
```

## Workflow

1. **Detect scene** and announce (中文):
   - "默认路径 -- squash 合并回 main，一个干净的中文 commit。"
   - "用户要求创建 PR -- 使用 PR 路径。"
   - "版本化项目，有 VERSION 文件 -- 使用完整发布流程含 CHANGELOG。"
   - "主干落后 8 个提交 -- 先 rebase 同步。"
   - "PR 有 3 个未解决的审查线程 -- 先处理反馈。"

2. **Pre-delivery** (if detected):
   - Run `pr-comment-resolver` for pending PR comments

3. **Execute detected path**

   **Path A: Squash 合并回 main（默认）**

   主干保持线性、干净、每个 commit 对应一个完整功能。

   ```bash
   # 0. 记录当前任务工作区（后续删除自己前必须先记下来）
   feature_branch=$(git branch --show-current)
   task_worktree=$(git rev-parse --show-toplevel)
   main_worktree=$(git worktree list --porcelain | sed -n 's/^worktree //p' | head -n 1)

   # 1. 强制主干同步（不可跳过）
   git fetch origin main
   git rebase origin/main
   # 冲突时协助解决，解决后继续

   # 2. 回到 main 所在工作区
   cd "$main_worktree"
   git checkout main
   git pull origin main

   # 3. Squash merge（不自动 commit）
   git merge --squash "$feature_branch"

   # 4. 用中文 commit message 提交
   git commit -m "<简洁中文描述：为什么变，不是变了什么>"

   # 5. Push
   git push origin main

   # 6. 合并成功后自动删除当前任务 worktree / feature branch
   git worktree remove "$task_worktree"
   git branch -D "$feature_branch"
   ```

   执行规则：
   - 若用户已明确要求"提交并合并到 main"或等价表述，且路径唯一、commit message 无歧义、`task_worktree` 删除目标清晰，则直接执行 `commit -> push -> cleanup`。
   - 只有在 commit message 难以确定、目标分支/路径不明确、或主干同步后出现新 blocker 时才停下 GATE。

   **GATE(仅在需要时): 展示 squash diff 摘要、拟定的 commit message、将删除的 `task_worktree` 路径。确认后执行 commit + push；push 成功后自动删除当前任务 worktree。**

   Commit message 规范：
   - 第一行：简洁中文，说明意图（为什么变），不超过 50 字
   - 可选 body：补充上下文，仅在变更需要叙事时添加
   - 不加 AI 署名 footer，除非用户要求

   **Path B: PR 路径（用户显式要求时）**
   ```
   git-commit-push-pr
     - Delegates to `ce-pr-description` for PR title/body generation
     - Auto-detects conventions from repo history
     - Logical commit splitting (file-level)
     [+ feature-video in parallel if UI detected]
   gstack-land-and-deploy
     - CI wait -> merge-readiness report -> merge -> deploy -> canary
   dev-ship cleanup
     - Merge 确认后自动删除当前任务 worktree + 本地 feature branch
   ```

   **Path C: gstack 完整发布路径（版本化项目）**
   ```
   gstack-ship
     - Merge base branch -> parallel tests -> coverage audit (60%/80%)
     - Plan completion audit + scope drift detection
     - REVIEW: pre-landing code review (auto, Step 3.5, 最多 3 轮)
     - REVIEW: adversarial review -- Claude + Codex (auto, Step 3.8, 最多 3 轮)
     - Version bump + CHANGELOG generation
     - Bisectable commits (dependency-ordered)
     [+ feature-video in parallel if UI detected]
   gstack-document-release
     - Cross-references all docs against diff
     - Auto-updates factual changes, asks on narrative changes
   gstack-land-and-deploy
     - CI wait -> merge-readiness report -> merge -> deploy -> canary
   dev-ship cleanup
     - Merge 确认后自动删除当前任务 worktree + 本地 feature branch
   ```

4. **`land-and-deploy` auto-detects** deployment platform and canary depth:
   - Platform: from `fly.toml` / `vercel.json` / `render.yaml` / `Procfile` / GitHub Actions
   - **Greenfield 检测**: 如果没有任何部署配置文件，宣告："未检测到部署配置 -- 运行 `gstack-setup-deploy` 创建部署设置。" 先配置再部署。
   - Canary depth by diff type: docs->skip, config->smoke, backend->console, frontend->full（frontend 全量优先用 `dev-browser --headless` + Playwright API 脚本跑关键路由 + 表单 + 控制台 error 检查）

   执行规则：
   - `land-and-deploy` 的 merge-readiness report 是 Phase 6 默认保留的**单一交付关卡**。
   - 若用户显式进入 `/dev:ship`，且报告无 blocker、路径唯一、无需产品取舍，则通过该关卡后直接继续，不再对 commit / push / merge / deploy 子步骤重复询问。
   - 若报告出现 blocker、缺失部署配置、未解决线程或需要用户承担风险的事项，STOP 并展示问题。

5. **过程文件收尾(默认不阻塞)**:
   扫描本任务相关的过程文件:
   ```bash
   # 用本次 PR/分支关联的日期或 R-ID 关键词匹配
   ls docs/brainstorms/*-requirements.md docs/plans/*-plan.md docs/superpowers/{specs,plans}/*.md docs/ideation/*.md 2>/dev/null
   ```
   筛选条件:frontmatter `status: shipped` 或 修改日期落在本任务窗口内 或 文件名含本任务的 R-ID/topic。

   默认行为：
   - 只在状态报告里列出候选文件，不阻塞交付，不额外发起确认。
   - 只有用户明确要求"归档过程文件"/"清理规划文档"/"写入 wiki"时，才进入下述处理分支。

   **GATE**(仅在用户要求处理时，展示候选清单 + 推荐动作):
   ```
   检测到本任务相关的过程文件 N 份:
     - docs/brainstorms/2026-04-19-foo-requirements.md
     - docs/plans/2026-04-19-001-feat-foo-plan.md
     - docs/superpowers/specs/2026-04-19-foo-design.md

   docs/solutions/ 永远不动(institutional memory)。

   选择处理方式:
     1. 归档到 docs/archive/<year>/ (Recommended) -- 用 git mv 保留 history,主目录留空
     2. 走 dev:wiki-ingest 编译进 wiki 后再删原文 -- 信息结构化沉淀,适合长期项目
     3. 保持原位 -- 文档本身就有长期参考价值
     4. 跳过 -- 我自己处理
   ```

   **执行**(用户要求处理后):
   - 选 1: `mkdir -p docs/archive/$(date +%Y) && git mv <files> docs/archive/$(date +%Y)/`,提示用户**不主动 commit**(铁律 7),把归档作为下次 commit 的一部分
   - 选 2: 委托 `/dev:wiki-ingest <files>`,完成后再 GATE 是否 `git rm` 原文
   - 选 3 / 4: 跳过

6. **自动删除当前工作区(强制收尾)**:
   代码已合入 main 后，`dev-ship` 自动删除当前任务 worktree，不保留临时工作区。

   ```bash
   # 在当前任务 worktree 中预先记录
   feature_branch=$(git branch --show-current)
   task_worktree=$(git rev-parse --show-toplevel)
   main_worktree=$(git worktree list --porcelain | sed -n 's/^worktree //p' | head -n 1)

   # merge/push main 或 land-and-deploy 成功后，从 main worktree 执行
   cd "$main_worktree"
   git pull origin main
   git worktree remove "$task_worktree"
   git branch -D "$feature_branch"
   ```

   安全约束:
   - 若 `task_worktree` 等于 `main_worktree`，或路径不在 `<repo>/.worktrees/` 下，STOP 并报告；禁止删除主 checkout。
   - 删除前运行 `git -C "$task_worktree" status --porcelain`;若过程文件归档产生未提交改动，暂停并报告，不使用 `--force` 删除。
   - Path A 是 squash merge，本地 feature branch 不会被 Git 认为已合并；只有在 `git push origin main` 成功后才允许 `git branch -D "$feature_branch"`。
   - Path B/C 只有在 `land-and-deploy` 明确确认 PR 已 merge 到 main 后才执行清理。

7. **Next**: `/dev:learn` (Phase 7)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Verified code diff (Phase 5 PASS) |
| **Output** | Squash 合并到 main（默认）或 PR + 部署（显式要求时）;过程文件按用户选择归档/编译/保留;合并后自动删除当前任务 worktree |
| **Next** | `/dev:learn` (Phase 7) |

## Iron Law

> Every failure point offers a rollback option. Explicit ship intent authorizes the normal path; only unresolved blockers or ambiguous choices reopen a gate.
