---
name: dev-flow
description: "Use when starting any development task, or when unsure which dev: phase to begin with. Detects the current project state, identifies which phase the work is in, and orchestrates the full discover->design->plan->code->verify->ship->learn pipeline automatically. The single entry point for the entire AI Coding workflow."
argument-hint: "[mode:auto|mode:manual] [task description]"
---

<SUPERVISE-CHECK>
执行前自检（Codex 环境必读，Claude Code 环境由 L1 hook 覆盖）：
1. 铁律 6（工作区）：运行 `git rev-parse --abbrev-ref HEAD`。若在 main/master 且不在 `.worktrees/` 子路径 → STOP，创建 worktree。
2. 铁律 7（提交触发）：本 phase 禁止 `git commit` / `git push` / `gh pr create`。提交仅在 `/dev:ship` 中由用户触发。
3. 铁律 4（证据先行）：声称"完成/通过"前必须有测试命令的实际输出作为证据。
</SUPERVISE-CHECK>

# dev:flow -- 智能研发编排器

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、GATE 提示、路由宣告、错误信息均使用中文。技能名称、文件路径、代码保持英文原样。
2. **工作区前置（强制）。** 在创建任何文档或代码之前，必须确认当前在任务专属 git worktree / feature branch 中。若在 main/master 或分支与当前任务不匹配，STOP 并调用 `using-git-worktrees`（Claude Code 下解析为 `superpowers:using-git-worktrees`，Codex 下同名；见 `claude-skills/README.md` 的 Skill Naming 表）创建工作区后再继续。路径必须为 `<repo>/.worktrees/<task-name>/`。用户拒绝创建时，STOP 并要求显式确认"在当前分支继续"。
3. **提交由用户触发。** Phase 1-5 只修改文件、运行测试，不执行 `git commit` / `git push` / 创建 PR。每个 GATE 结束时不提交；提交仅发生在 Phase 6 `/dev:ship` 由用户显式触发。
4. **Review 采取多轮循环。** 所有涉及 review 的环节（`document-review`、`ce-review`、`plan-eng-review` 等），执行"审查 -> 修复 -> 再审查"循环，直到：(a) 零 P0/P1 发现，或 (b) 达到最大轮次（默认 3 轮），或 (c) 连续两轮发现相同问题（收敛）。
5. **技能名统一使用扁平规范名**（见 `claude-skills/README.md` 的 Skill Naming 表）。本 SKILL 正文引用的下游技能名（如 `ce-brainstorm`、`using-git-worktrees`、`document-review`、`git-commit-push-pr`、`gstack-*`）在两种环境下都可解析：Claude Code 下 agent 会自动加 `compound-engineering:` / `superpowers:` 前缀；Codex 下名字直接匹配。

## Overview

`dev:flow` is the single entry point for the entire AI Coding workflow. It **detects** where the current work stands in the 7-phase pipeline, **enters** at the right phase, and **drives** through to completion. 默认是 guided auto-advance：阶段通过且下一步唯一明确时自动继续，只在真实阻塞、重大疑问、风险取舍或破坏性动作前停下。

```
dev:flow
  |
  +-- Detect current state
  |
  +-- Enter at the right phase
  |
  +-- Drive: discover -> design -> plan -> code -> verify
      -> pre-ship learn/supervise decision -> ship -> post-ship learn
  |                                                                   |
  +-- <------------------------------- next work item ----------------+
```

You do not need to call individual `dev:*` skills manually. `dev:flow` detects and routes.

## Phase 0: Detect Run Mode

Parse the invocation arguments before any phase detection:

| Mode | How to activate | Behavior |
|---|---|---|
| guided (default) | Omit mode, or use ordinary requests | Auto-continue when success criteria are met and the next step is unique; stop only for meaningful decisions |
| `mode:manual` | Pass `mode:manual`, or explicitly ask for "每步确认" / "逐步确认" / "先停下等我确认" | Step-by-step mode; phase checkpoints stop and wait |
| `mode:auto` | Pass `mode:auto`, or explicitly ask for "全自动模式" / "自动跑完整个流程" / "不要每步确认" | Same as guided, plus explicit authorization to enter `/dev:ship` if no blocker exists |

Mode rules:
- Default guided mode and `mode:auto` both auto-advance non-destructive phase checkpoints when "当前阶段通过 + 下一步唯一明确"。
- `mode:auto` is an **explicit user authorization** to enter `/dev:ship` inside the same flow. Default guided mode still stops before commit/push/PR unless the user has separately authorized shipping.
- `mode:manual` 只有用户明确要求逐步确认时启用；不要把普通请求解释成"每个 phase 都问一次"。
- 编号选项只用于用户必须做选择的情况；不得为"是否继续下一阶段"这类唯一明确路径输出编号确认。

Hard blockers that still **STOP** in guided / `mode:auto`:
- 工作区前置不满足，或用户拒绝创建/切换 worktree
- 必需产物缺失且无法自动生成
- 测试失败、phase skill 返回 STOP、或本应产生产物却没有产物
- 强制 review gate 仍有未处理 P0/P1
- 当前阶段存在多个有效分支且不能安全自动替用户选一个
- 外部/系统失败：鉴权失败、网络失败、merge conflict、deploy 失败、缺少关键工具
- 进入 Phase 6 但没有显式 ship 授权（除非当前 invocation 是 `mode:auto` 或用户说了提交/PR/上线）

## Scene Detection: Where Are We?

On invocation, check these signals **in order** to determine which phase to enter:

### Signal 0: Are we in a task-scoped worktree?

```bash
# Check repo + current branch + worktree list
git rev-parse --is-inside-work-tree 2>/dev/null && echo "GIT: yes" || echo "GIT: no"
git rev-parse --abbrev-ref HEAD
git worktree list 2>/dev/null | head -5
```

| Finding | Action |
|---|---|
| Not in a git repo | STOP: "当前不在 git 仓库中，无法启动研发流程。" |
| On main/master | STOP: "当前在主分支。调用 `using-git-worktrees` 创建任务专属工作区,**路径必须在 `<repo>/.worktrees/<task-name>/`**。" |
| On a branch but not a task-scoped worktree (分支名与当前任务不匹配 / 共享分支多任务) | STOP: "当前分支与本任务不匹配。调用 `using-git-worktrees` 创建独立工作区,路径 `<repo>/.worktrees/<task-name>/`。" |
| User refuses to create a worktree | STOP: "需要用户显式确认 `在当前分支继续` 才能跳过工作区前置。" |
| Already in task-scoped worktree / feature branch | 继续 Signal 1 |

> **worktree 统一落点约定**:所有 `dev:*` phase 创建的 worktree 必须放在 `<repo>/.worktrees/<name>/`(已在仓库 `.gitignore`)。禁止创建到 `/tmp`、`$HOME/worktrees`、或仓库兄弟目录——方便清理、方便发现、避免遗漏。调用 `using-git-worktrees` 时明确传该路径;该 skill 若默认位置不同,在 prompt 里覆盖它。

### Signal 1: Is there unfinished work from a previous session?

```bash
# Check for in-progress plan
ls docs/plans/*-plan.md 2>/dev/null | head -5

# Check for uncommitted code changes
git status --short

# Check for open PR on current branch
gh pr view --json state,title 2>&1
```

| Finding | Enter At |
|---|---|
| Plan with `status: active`, unchecked Implementation Units | Phase 4 (code) -- resume execution |
| Uncommitted code changes + recent ce-review run | Phase 5.5 (pre-ship knowledge/supervision) -- decide whether to run `dev-learn` / `dev-supervise`, then Phase 6 |
| Uncommitted code changes, no review evidence | Phase 5 (verify) -- needs review |
| Open PR with unresolved review threads | Phase 6 (ship) -- resolve feedback, then ship |
| Plan with `status: active`, all units checked, no code changes | Phase 5 (verify) -- confirm completion |
| Nothing in progress | Check Signal 1b |

### Signal 1b: Issue Tracker 有待处理 Issue?

如果项目配置了 Issue Tracker（`/setup-matt-pocock-skills` 或等效配置），检测待处理 bucket：

| Finding | Action |
|---|---|
| `needs-triage` 有新 Issue | 展示待处理列表，用户选择后运行 `triage` -> 路由到 Phase 1 或 Bug Fix |
| `needs-info` 有 reporter 新回复 | 展示需重新评估的 Issue |
| `ready-for-agent` 有待认领 Issue | 展示可认领列表，用户选择后直接进入对应工作流 |
| 无待处理 Issue 或无 Issue Tracker | Check Signal 2a |

此信号是**信息性**的——展示后等用户选择，不自动认领。用户可跳过直接描述新工作。

### Signal 2a: Is this a bug fix?

检测关键词：bug / fix / 修复 / 报错 / crash / regression / broken / error when / stack trace，或引用 GitHub Issue / 粘贴错误日志。

| Finding | Action |
|---|---|
| Bug fix intent detected | **进入 Bug Fix 快速路径**（见下方专节） |
| Not a bug fix | Check Signal 2b |

### Signal 2b: What did the user provide?

| User Input | Enter At |
|---|---|
| No input / empty | Phase 1 (discover) -- "我们做什么？" |
| Vague idea: "improve the search", "make it faster" | Phase 1 (discover) -- needs requirements |
| Clear feature with spec: "Add OAuth per this doc" | Phase 3 (plan) -- requirements exist informally |
| File path to requirements doc | Phase 2 or 3 -- check if UI involved |
| File path to plan doc | Phase 4 (code) -- plan exists, execute it |
| "ship it" / "deploy" / "create PR" | Phase 5.5 (pre-ship knowledge/supervision) -- then Phase 6 delivery |
| "what did we learn" / "retro" | Phase 7 (learn) -- knowledge capture |
| Dependency upgrade: "upgrade X", "update deps" | Phase 3 (plan) -- 需要计划升级步骤和回滚策略 |
| Docs-only: "update README", "fix docs" | Phase 4 (code) -- bare prompt inline, skip Phase 1-3 |
| Greenfield: "new project", "init", "bootstrap" | Phase 1 (discover) -- 从头开始，含项目脚手架 |

### Signal 3: What artifacts already exist?

```bash
# Requirements docs
ls docs/brainstorms/*-requirements.md 2>/dev/null

# Design system
ls DESIGN.md 2>/dev/null

# Plans
ls docs/plans/*-plan.md 2>/dev/null

# Recent ce-review runs
ls .context/compound-engineering/ce-review/ 2>/dev/null
```

| Artifacts Present | Enter At |
|---|---|
| No requirements doc | Phase 1 (discover) |
| Requirements doc exists, no DESIGN.md, work has UI | Phase 2 (design) |
| Requirements doc exists, no plan | Phase 3 (plan) |
| Requirements + plan exist, plan not started | Phase 4 (code) |
| Code changes + review done | Phase 5.5 (pre-ship knowledge/supervision) -> Phase 6 |
| Everything shipped | Phase 7 (learn) |

## Orchestration Loop

Once the entry phase is determined, `dev:flow` drives through the pipeline:

```
[Entry Point Detected]
      |
      v
  Phase 1: /dev:discover
      |  Scene Detection -> ideate / office-hours / brainstorm
      |  Output: requirements doc with R-IDs
      |  GATE: requirements approved
      |
      |  Auto-detect: has UI? ----yes----> Phase 2
      |                  |
      |                  no
      |                  |
      v                  v
  Phase 2: /dev:design        |
      |  Scene Detection ->   |
      |  consultation /       |
      |  shotgun / skip       |
      |  Output: DESIGN.md    |
      |  GATE: design approved|
      |                       |
      v                       |
  Phase 3: /dev:plan  <-------+
      |  ce-plan -> auto-select review depth
      |  Output: plan doc with Impl Units
      |  GATE: plan-eng-review CLEARED
      |
      v
  Phase 4: /dev:code
      |  ce-work auto-selects strategy
      |  Built-in: ce-review mode:autofix
      |  GATE: all tasks done, tests pass
      |
      v
  Phase 5: /dev:verify
      |  ce-review full + auto-stack layers
      |  GATE: PASS verdict
      |
      v
  Phase 5.5: Pre-Ship Knowledge/Supervision Decision
      |  Decide whether `dev-learn` or `dev-supervise`
      |  must run before delivery artifacts are committed
      |  GATE: no required pre-ship capture remains
      |
      v
  Phase 6: /dev:ship
      |  Auto-select Path A or B
      |  land-and-deploy with canary
      |  GATE: merge confirmed
      |
      v
  Phase 7: /dev:learn
      |  Post-ship closeout only when still useful
      |  compound / retro / writing-skills
      |
      v
  [Loop back to Phase 1 for next work item]
```

## Bug Fix 快速路径

> 当 Signal 2a 检测到 bug 修复意图时，跳过标准 Phase 链，进入专用修复流程。
>
> 核心原则：**根因先于修复**（铁律 #3）。

```
用户报告 bug / 引用 Issue / 粘贴错误日志
    |
    v
Signal 0: 工作区检查（同标准流程）
    |
    v
Step 1: 复现
    reproduce-bug + diagnose Phase 1（构建 feedback loop）
    (涉及 UI 时叠加 dev-browser)
    diagnose 优先级: 失败测试 > curl > CLI > headless browser
      > replay trace > throwaway harness > property fuzz > bisection > HITL
    产出：可稳定触发的复现步骤 + 失败断言
    ⛔ 无法复现 -> 停下，向用户要更多上下文
    |
    v
Step 2: 根因定位
    diagnose Phase 3-4（3-5 可证伪假设 -> 仪器化）
    - 每个探针对应一个具体预测，一次只变一个量
    - 调试日志加 [DEBUG-xxxx] 前缀，便于清理
    fallback: ce-debug（因果链门控 4 阶段）
    产出：定位到具体代码行 + 因果链解释
    ⛔ 3 轮定位失败 -> 停下质疑架构
    |
    v
Step 3: 修复实现（= Phase 4 子集）
    TDD: 先将复现步骤固化为回归测试（RED）
         再写最小修复代码（GREEN）
    ⛔ 不扩大修复范围——只修根因，不顺手重构
    |
    v
Step 4: 回归验证（= Phase 5 子集）
    - 回归测试通过
    - 全量测试套件无新失败
    - 涉及 UI 时 dev-browser 验证修复效果
    |
    v
GATE: 报告修复结果，先进入 Phase 5.5 判断是否需要沉淀/自省，再决定是否进入 Phase 6 交付
```

### Bug Fix 路由细节

| 信号 | 路由 |
|---|---|
| 用户描述 bug + 提供复现步骤 | Step 1 快速确认 -> Step 2 |
| 用户粘贴 stack trace / 错误日志 | Step 2 直接开始（日志即复现证据） |
| 引用 GitHub Issue | `reproduce-bug` 从 Issue 提取复现步骤 -> Step 1 |
| 用户说"紧急"/"hotfix"/"线上" | 同上流程，但 GATE 提示优先交付，跳过非必要审查 |

### 与标准流程的关系

- Bug Fix 路径**不产出需求文档**（Phase 1 产物），bug 本身就是需求："恢复预期行为"。
- Bug Fix 路径**不产出设计文档**（Phase 2 产物），除非修复涉及 UI 变更且需要新的交互模式。
- 修复完成后先汇入 Phase 5.5（交付前沉淀/自省判断），再进入标准 Phase 6（交付），遵守铁律 #7（提交由用户触发）。
- 如果根因分析发现问题不是 bug 而是缺失功能，**退出 Bug Fix 路径，回到标准 Phase 1**。

### Bug Fix 铁律

- **无复现，不定位** —— 不能稳定复现的 bug 不进入 Step 2
- **无根因，不修复** —— 禁止"试试看"式修复
- **不扩大范围** —— 只修根因，不顺手清理周边代码；清理另开任务
- **回归测试必须先于修复代码** —— 铁律 #2 在 bug 场景的具体化

## GATE Behavior

`dev:flow` 区分两类出口：

| 出口 | 是否问用户 | 用法 |
|---|---|---|
| Status checkpoint | 不问；报告证据后继续 | 当前 phase 已通过，下一步唯一明确 |
| Decision GATE | 问；必须有明确选项 | 存在阻塞、重大疑问、风险取舍、破坏性动作、多个合理路线、或用户明确要求逐步确认 |

不要把每个 phase 的完成报告都写成编号确认。确认必须有决策价值；如果推荐项永远是"继续下一阶段"，那就不是 GATE。

```
--- Status: Phase 1 完成 ---
需求文档: docs/brainstorms/2026-04-04-user-auth-requirements.md
需求 ID: R1 (注册), R2 (登录), R3 (管理员禁用)
文档审查: 通过
UI 检测: 是 (R1, R2 中提到 views/components)
主干偏离: 0 commits behind main ✅

下一步唯一明确: 自动进入 Phase 2 (设计)。
```

Decision GATE examples:
- 需求/设计存在多个合理解释，无法安全选择
- Review 仍有 P0/P1，需要用户接受风险或改范围
- Phase 6 commit/push/PR 尚未获得显式授权
- 破坏性操作、数据迁移、删除 worktree 以外的文件
- 用户明确说"先停一下让我确认"

guided / `mode:auto` behavior:
- 若当前阶段通过且下一步唯一明确：自动进入下一阶段，并打印一行状态摘要
- 若遇到 hard blocker：立即 STOP，报告阻塞点和所需人工决策
- 若只是提醒级信息（例如主干偏离 6-15 commits）：打印提醒后继续，不额外停下

## 主干同步机制（Trunk Sync）

> 工作区离 main 越远，最终合并越痛苦。`dev:flow` 在每个 GATE 自动检测偏离度，及时提醒同步。

### 检测方式

每次 GATE 检查时，自动执行：

```bash
# 获取最新 main（仅 fetch，不改工作区）
git fetch origin main 2>/dev/null

# 计算 main 上有多少新 commit 尚未合入当前分支
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
echo "主干偏离: $BEHIND commits behind main"
```

### 同步阈值与动作

| 偏离度 | GATE 中的表现 | 动作 |
|---|---|---|
| 0-5 commits | ✅ 显示偏离数，不干预 | 无 |
| 6-15 commits | ⚠️ 黄色提醒 | `mode:manual` 下建议在当前 GATE 同步；`mode:auto` 下打印提醒后继续 |
| 16+ commits | 🔴 红色警告 | STOP，要求先同步主干再继续 |

### Phase 4 长实现阶段的额外检查

Phase 4 (`dev:code`) 中，如果 `ce-work` 执行超过 3 个 Implementation Unit，在每 3 个 Unit 完成后插入一次主干同步检查（与 `/simplify` 节奏类似）：

```
--- 主干同步检查 (Unit 3 完成后) ---
主干偏离: 8 commits behind main ⚠️
main 上新增: db/migrate/20260420_add_index.rb, config/routes.rb

建议: 暂停实现，先 rebase main 再继续。[同步 / 跳过]
```

用户选"跳过"时记录，Phase 6 前**强制**再检查一次。

## Phase 5.5: Pre-Ship Knowledge/Supervision Decision

在进入 Phase 6 (`dev:ship`) 前，`dev:flow` 必须先判断本次交付是否需要把知识沉淀或 skill 自省产物纳入同一个交付 diff。目标是避免"先 ship，再发现 `docs/solutions/`、`docs/supervise/` 或 `SKILL.md` 相关证据还没随代码交付"。

### 判定顺序

```
Phase 5 PASS / Bug Fix Step 4 PASS
  |
  v
检查 pre-ship 信号
  |
  +-- 需要 skill 自省? ---- yes -> dev-supervise (project scope)
  |
  +-- 需要知识沉淀? ------ yes -> dev-learn (匹配 Route A-F)
  |
  +-- 产出新文件? -------- yes -> 回到 Phase 5 做针对性验证
  |
  v
进入 Phase 6 (`dev:ship`)
```

### 智能信号

| 信号 | 动作 |
|---|---|
| 解决了非平凡 bug、定位了根因、形成了新的架构/运维/调试模式 | 先运行 `dev-learn`，通常走 Route A (`ce-compound`) |
| 用户明确说"记下来"、"沉淀"、"写成 skill"、"这个以后也要这么做" | 先运行 `dev-learn`，按 Route A/C/E/F 分流 |
| 本次 diff 修改 `claude-skills/`、`.agents/skills/`、`docs/ai-coding-workflow.md`、`scripts/supervise/` 或 `docs/supervise/` | 先运行 `dev-supervise --scope project --since 7d`；若还暴露 skill gap，再运行 `dev-learn` Route E |
| 本 session 出现用户打断、回滚、重复返工、L1 iron law 事件，或同一问题在 review 中反复出现 | 先运行 `dev-supervise` 收集证据，再判断是否需要 `dev-learn` Route E |
| 只是微小 typo、机械格式、无新决策的依赖锁文件变化，且无纠正信号 | 跳过 `dev-learn` 和 `dev-supervise`，直接进入 Phase 6 |

当两个动作都需要时，顺序固定为：**先 `dev-supervise`，后 `dev-learn`**。原因是自省报告可能成为 `dev-learn` Route E 的输入；反过来会漏掉本次流程摩擦。

### GATE 行为

- guided / `mode:auto`：若信号唯一明确，自动运行对应步骤；若信号为"无新知识/无自省必要"，自动跳过；若是否要沉淀存在产品/团队取舍，STOP 等用户决定。
- `mode:manual`：用户明确要求逐步确认时，报告判定结果并等待。
- 任一步骤写入新文件后，必须至少执行针对性验证（例如 `git status --short`、相关 markdown grep/链接检查、必要时 `/dev:verify` 的 docs-only 审查）再进入 Phase 6。
- `dev-supervise` 只产出报告，不自动 patch `SKILL.md`；如报告要求修改技能，回到 Phase 4/5 完成修改和验证后再重新进入 Phase 5.5。

### Phase 6 前强制同步

进入 Phase 6 (`dev:ship`) 前，主干同步是**强制前置步骤**（不可跳过）：

```bash
git fetch origin main
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
if [ "$BEHIND" -gt 0 ]; then
  echo "合并前必须同步主干。当前落后 $BEHIND 个提交。"
  echo "执行: git rebase origin/main"
fi
```

rebase 后如有冲突，协助用户解决后再继续交付流程。

## Resume Intelligence

When `/dev:flow` is called again in a subsequent session:

1. Scan for artifacts (Signal 3) to detect where the previous session left off
2. Read the most recent plan's `status` field and checkbox progress
3. Check git branch state and PR status
4. Announce: "Resuming from Phase 4 -- plan has 3/5 units completed on branch `feat/user-auth`."
5. Continue from the detected phase

## Handling Branches and Parallel Work

```
dev:flow (main line of work)
  |
  +-- User says "also fix this bug while we're at it"
  |   -> Assess: is this related to current work?
  |     yes -> add to current plan as a new Implementation Unit
  |     no  -> "This is separate work. Finish current flow first, or use
  |             /dev:flow in a new worktree for parallel development."
  |
  +-- User says "pause this, work on something else"
  |   -> 调用 `gstack-context-save` 保存当前状态 (branch, progress, decisions)
  |   -> Start new /dev:flow for the new work item
  |   -> When done, `gstack-context-restore` 恢复暂停的流程
```

## Phase Skip Rules

Not every work item needs all 7 phases. `dev:flow` auto-detects skippable phases:

| Condition | Skip |
|---|---|
| Pure backend, no UI in requirements | Phase 2 (design) |
| Bug fix (including trivial fix, emergency hotfix) | **走 Bug Fix 快速路径**（Signal 2a），不走标准 Phase 链 |
| Requirements already exist and approved | Phase 1 |
| DESIGN.md exists and no new UI patterns needed | Phase 2 |
| Plan already exists and reviewed | Phase 3 |
| Nothing novel learned and no self-review signal | Phase 5.5 pre-ship `dev-learn` / `dev-supervise`; Phase 7 post-ship learn |
| Docs-only change (README, CONTRIBUTING, etc.) | Phase 1, 2, 3 -- Phase 4 inline + Phase 5 (devex-review auto-stacked) |
| Dependency upgrade | Phase 2 -- 走 Phase 1(轻量需求)->3(升级计划)->4->5->6 |

When skipping, announce: "Skipping Phase 2 (design) -- pure backend work, no UI surface detected."

## Error Recovery

| Situation | Action |
|---|---|
| Phase fails (tests don't pass, review finds blockers) | Stay in current phase, fix issues, retry |
| User disagrees with routing | Accept redirect, re-enter at specified phase |
| Upstream artifact missing (no requirements, no plan) | Route back to the missing phase |
| 3 consecutive failures in same phase | Escalate: "Phase 4 has failed 3 times. Should we revisit the plan (Phase 3) or the requirements (Phase 1)?" |

## Full Example

```
用户: "我想在用户账号被禁用时发送邮件通知"

dev:flow 检测:
  - Signal 0: 在 feat/notifications 分支，工作区就绪
  - Signal 1: 无进行中的工作
  - Signal 2: 明确的功能描述，中等范围
  - 进入 Phase 1

Phase 1 (/dev:discover):
  场景: 明确功能，中等范围 -> Route C (Standard brainstorm)
  -> ce-brainstorm 产出需求文档 R1-R4
  -> document-review: 通过（2 轮循环，第 1 轮修复 1 个一致性问题）
  -> 检测到 UI: 是（通知设置页面）
  Status: "需求已就绪，检测到 UI；下一步唯一明确，自动进入 Phase 2。"

Phase 2 (/dev:design):
  场景: DESIGN.md 存在，该功能无 approved.json -> Route B
  -> design-shotgun 生成 3 个变体
  -> 用户选择变体 B
  Status: "设计方向已确认；下一步唯一明确，自动进入 Phase 3。"

Phase 3 (/dev:plan):
  -> ce-plan 产出 4 个实施单元
  -> document-review: 通过
  -> 检测到 4 单元 -> plan-eng-review + plan-design-review
  -> plan-eng-review: CLEARED
  Status: "计划已审查通过；下一步唯一明确，自动进入 Phase 4。"

Phase 4 (/dev:code):
  -> ce-work 检测 4 单元，2 个独立 -> 并行+串行策略
  -> Unit 1-2 (并行): 邮件服务 + 通知模型
  -> Unit 3-4 (串行): 控制器 + 设置页面
  -> ce-review mode:autofix: 修复 2 个 safe_auto 问题
  Status: "所有单元完成且测试通过；下一步唯一明确，自动进入 Phase 5。"

Phase 5 (/dev:verify):
  -> ce-review interactive: 8 个 persona 激活（含邮件处理的 security）
  -> 第 1 轮: 发现 1 个 P1 (邮件注入风险) + 1 个 P2
  -> 修复 -> 第 2 轮: 零 P0/P1 -> 通过
  -> test-browser: 通知设置页面测试通过
  Status: "验证通过；下一步唯一明确，自动进入交付前沉淀/自省判断。"

Phase 5.5 (Pre-Ship Knowledge/Supervision Decision):
  -> 检测: 新增邮件通知服务模式 + 无 skill 执行纠正信号
  -> 运行 dev-learn Route A，写入 docs/solutions/notifications/email-service.md
  -> 针对性验证: git status + markdown 链接检查通过
  Status: "交付前沉淀已完成；若已有 ship 授权则进入 Phase 6，否则在 Phase 6 前停下请求交付授权。"

Phase 6 (/dev:ship):
  场景: 无版本文件 -> Path A (squash 合并回 main)
  -> 主干同步: rebase origin/main，无冲突
  -> squash merge: 展示 diff 摘要 + 拟定 commit message
  -> 已有 ship 授权且无 blocker: 自动继续
  -> push to main，清理 feature branch
  Status: "已合并到 main；自动进入 Phase 7 处理部署后新增知识或跳过。"

Phase 7 (/dev:learn):
  场景: 交付前已完成知识沉淀，部署无新增经验 -> skip
  -> "知识已沉淀。准备进入下一个工作项。"
```

## Bug Fix Example

```
用户: "用户登录时报 500，日志里有 NullPointerException"

dev:flow 检测:
  - Signal 0: 在 fix/login-npe 分支，工作区就绪
  - Signal 1: 无进行中的工作
  - Signal 2a: bug 修复意图（"报 500" + stack trace）
  - 进入 Bug Fix 快速路径

Step 1 (复现):
  用户已提供 stack trace -> 跳过手动复现
  -> 从日志提取调用链，定位到 UserService.login()
  Status: "已确认复现路径；自动进入根因定位。"

Step 2 (根因定位):
  -> ce-debug 因果链分析
  -> 根因: UserService.login() 未处理 user.getProfile() 返回 null 的情况
     （新注册用户尚未创建 profile 记录）
  Status: "根因已定位；自动进入修复实现。"

Step 3 (修复实现):
  -> TDD RED: 写回归测试 -- 新注册用户登录应返回 200
  -> TDD GREEN: UserService.login() 添加 null check，无 profile 时创建默认 profile
  -> 不扩大范围（不顺手重构 UserService 其他方法）

Step 4 (回归验证):
  -> 回归测试通过 ✅
  -> 全量测试套件 142/142 通过 ✅
  Status: "修复已验证；自动进入交付前沉淀/自省判断。"

Phase 5.5:
  -> 检测: 根因明确且有回归测试；无 skill/process 变更
  -> 运行 dev-learn Route A，记录"profile 为空导致登录 500"的排查与预防
  -> 验证 docs/solutions 新文档可检索
  -> 进入 Phase 6

Phase 6 (/dev:ship):
  -> 用户确认 -> git commit -m "修复新注册用户登录 500: 处理 profile 为 null 的情况"
```

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Anything: idea, bug report, file path, `mode:auto`, `mode:manual`, "ship it", or nothing |
| **Output** | Completed work item: requirements -> design -> plan -> code -> verified -> shipped -> documented (bug fix 走快速路径: 复现 -> 根因 -> 修复 -> 验证 -> 交付) |
| **Next** | Self (next work item) |

## Iron Laws (inherited from all phases)

1. **Design before implement** -- no code without approved requirements
2. **Test before code** -- no production code without failing test
3. **Root cause before fix** -- no fix without understanding why (Bug Fix 快速路径 Step 2 强制执行)
4. **Evidence before assertion** -- no "it works" without proof
5. **Verify before adopt** -- no review feedback accepted without verification
6. **Worktree before work** -- 每次创建文档或代码前必须在任务专属 worktree/feature branch 中,且**路径统一在 `<repo>/.worktrees/<name>/`**
7. **Commit only on user trigger** -- Phase 1-5 不主动 commit/push/PR；提交仅在 `/dev:ship` 由用户显式触发

## 编码行为约束（贯穿 Phase 4-5）

七条铁律管**流程**，本节管**行为**。Phase 4 实现、Phase 5 审查时必须遵循：

- **明确假设 / 不懂就问**：实现前列出关键假设；多解释时让用户选，不要静默挑一个；不确定就 STOP 问；更简单方案主动说出来。**调用澄清工具时必须带推荐标识**——推荐项排第一并标 `(Recommended)`；无倾向时明说"无明确推荐"，不伪装中立。
- **手术刀修改**：只改任务直接相关的行；不顺手"改进"相邻代码/注释/格式；匹配现有风格即使你不认同；发现无关 dead code 只提及不删除。
- **孤儿清理**：仅清理你这次改动产生的未使用 import/变量；不动原有 dead code。

完整规则和 Phase 4 收尾自检清单见 `docs/ai-coding-workflow.md` 的"编码行为约束（贯穿 Phase 4-5）"节。
