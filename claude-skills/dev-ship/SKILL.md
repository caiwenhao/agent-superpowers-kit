---
name: dev-ship
description: "Use when Phase 5 has passed and code is ready to deliver. Detects project type and upstream quality to auto-select lightweight (CE) or full (gstack) delivery path. Both end with land-and-deploy."
---

# Phase 6: Ship -- "上线"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、路由宣告均使用中文。
2. **工作区前置（强制）。** 执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并要求用户先创建/切换到 feature branch；禁止在主分支直接 commit/push。
3. **提交由用户显式触发。** 前置阶段（Phase 1-5）绝不主动 commit/push/PR。本阶段（Phase 6）是**唯一**可以 commit/push/创建 PR 的阶段，且要求用户已显式调用 `/dev:ship` 或明确说"提交/commit/push/PR/上线"；每个关键写操作（commit / push / PR / merge / deploy）之前再次以 GATE 向用户确认。
4. **Review 多轮循环。** Path B 中 `gstack/ship` 的 pre-landing review 和 adversarial review 执行多轮循环。

## Overview

Phase 6 delivers verified code to production. It **detects** project type and upstream quality context to **auto-select** the right delivery path. Two paths share a single endpoint (`land-and-deploy`).

Position in workflow: Phase 5 (verify) -> **Phase 6** -> Phase 7 (knowledge)

## When to Use

- Phase 5 verification passed
- Code is ready to ship

**Never skip Phase 6.**

## Scene Detection

**Signal 1: Does the project use versioning?**
- `VERSION` file exists OR `package.json` has `version` field -> versioned project
- No version file -> unversioned project

**Signal 2: What upstream quality was already applied?**
- `ce:review` ran in Phase 4/5 (check `.context/compound-engineering/ce-review/` for recent run) -> upstream quality confirmed
- No ce:review evidence -> needs ship's built-in review

**Signal 3: PR feedback pending?**
- Run `gh pr view --json reviewDecision,comments` on current branch
- Unresolved review threads exist -> prepend `resolve-pr-feedback`

**Signal 4: UI changes in diff?**
- Scan diff for `views/`, `components/`, `*.tsx`, `*.css`, `*.html` -> add `feature-video` + 部署后 `dev-browser` 烟测（关键路由 + 控制台无 error）

## Routing

```
Verified code (from Phase 5)
  |
  +-- [Unversioned + upstream quality confirmed] -> Path A: CE Lightweight
  |   Daily feature, already passed ce:review
  |
  +-- [Versioned project] -----------------------> Path B: gstack Full
  |   Needs VERSION bump + CHANGELOG
  |
  +-- [No upstream review evidence] --------------> Path B: gstack Full
  |   Needs ship's built-in review gates
  |
  +-- [Emergency hotfix] -------------------------> Path A: CE Lightweight
      (user explicitly says "hotfix" or "urgent")
```

### Pre-delivery (auto-detected)

```
  +-- [PR has unresolved threads] -> resolve-pr-feedback first
  +-- [Diff has UI files] ---------> feature-video in parallel
```

## Workflow

1. **Detect scene** and announce (中文):
   - "版本化项目，有 VERSION 文件 -- 使用完整发布流程含 CHANGELOG。"
   - "上游 ce:review 已确认 -- 使用轻量提交+PR 路径。"
   - "PR 有 3 个未解决的审查线程 -- 先处理反馈。"

2. **Pre-delivery** (if detected):
   - Run `/ce:resolve-pr-feedback` for pending PR comments

3. **Execute detected path**

   **Path A: CE Lightweight**
   ```
   /ce:git-commit-push-pr
     - Delegates to `ce-pr-description` for PR title/body generation
     - Auto-detects conventions from repo history
     - Logical commit splitting (file-level)
     [+ feature-video in parallel if UI detected]
   /gstack-land-and-deploy
     - CI wait -> merge-readiness report -> merge -> deploy -> canary
   ```

   **Path B: gstack Full Release**
   ```
   /gstack-ship
     - Merge base branch -> parallel tests -> coverage audit (60%/80%)
     - Plan completion audit + scope drift detection
     - REVIEW: pre-landing code review (auto, Step 3.5, 最多 3 轮)
     - REVIEW: adversarial review -- Claude + Codex (auto, Step 3.8, 最多 3 轮)
     - Version bump + CHANGELOG generation
     - Bisectable commits (dependency-ordered)
     [+ feature-video in parallel if UI detected]
   /gstack-document-release
     - Cross-references all docs against diff
     - Auto-updates factual changes, asks on narrative changes
   /gstack-land-and-deploy
     - CI wait -> merge-readiness report -> merge -> deploy -> canary
   ```

4. **`land-and-deploy` auto-detects** deployment platform and canary depth:
   - Platform: from `fly.toml` / `vercel.json` / `render.yaml` / `Procfile` / GitHub Actions
   - **Greenfield 检测**: 如果没有任何部署配置文件，宣告："未检测到部署配置 -- 运行 `/gstack-setup-deploy` 创建部署设置。" 先配置再部署。
   - Canary depth by diff type: docs->skip, config->smoke, backend->console, frontend->full（frontend 全量优先用 `dev-browser --headless` + Playwright API 脚本跑关键路由 + 表单 + 控制台 error 检查）

   **GATE: Merge-readiness report shown to user. User confirms before merge.**

5. **过程文件归档(可选 GATE,land-and-deploy 之后触发)**:
   扫描本任务相关的过程文件:
   ```bash
   # 用本次 PR/分支关联的日期或 R-ID 关键词匹配
   ls docs/brainstorms/*-requirements.md docs/plans/*-plan.md docs/superpowers/{specs,plans}/*.md docs/ideation/*.md 2>/dev/null
   ```
   筛选条件:frontmatter `status: shipped` 或 修改日期落在本任务窗口内 或 文件名含本任务的 R-ID/topic。

   **GATE**(展示候选清单 + 推荐动作):
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

   **执行**(用户确认后):
   - 选 1: `mkdir -p docs/archive/$(date +%Y) && git mv <files> docs/archive/$(date +%Y)/`,提示用户**不主动 commit**(铁律 7),把归档作为下次 commit 的一部分
   - 选 2: 委托 `/dev:wiki-ingest <files>`,完成后再 GATE 是否 `git rm` 原文
   - 选 3 / 4: 跳过

6. **Next**: `/dev:learn` (Phase 7)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Verified code diff (Phase 5 PASS) |
| **Output** | Merged PR, deployed to production, canary verified;过程文件按用户选择归档/编译/保留 |
| **Next** | `/dev:learn` (Phase 7) |

## Iron Law

> Every failure point offers a rollback option. No deployment proceeds without user confirmation at the merge-readiness gate.
