---
name: dev-learn
description: "Use after solving a significant problem, shipping a feature, or completing a sprint. Detects the trigger type and routes to the right knowledge capture skill: ce:compound for problems, retro for sprints, writing-skills for reusable methods."
---

<SUPERVISE-CHECK>
执行前自检（Codex 环境必读，Claude Code 环境由 L1 hook 覆盖）：
1. 铁律 6（工作区）：运行 `git rev-parse --abbrev-ref HEAD`。若在 main/master 且不在 `.worktrees/` 子路径 → STOP，创建 worktree。
2. 铁律 7（提交触发）：本 phase 禁止 `git commit` / `git push` / `gh pr create`。提交仅在 `/dev:ship` 中由用户触发。
3. 铁律 4（证据先行）：声称"完成/通过"前必须有测试命令的实际输出作为证据。
</SUPERVISE-CHECK>

# Phase 7: Learn -- "学到什么"

## 通用规则

1. **始终用中文与用户交流。** 所有状态报告、路由宣告均使用中文。
2. **工作区前置（强制）。** 在写入任何知识文档（`docs/solutions/`、`learnings.jsonl`、wiki 页等）之前，执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并调用 `compound-engineering:ce-worktree`（或 `superpowers:using-git-worktrees`）创建工作区后再继续。
3. **提交由用户触发。** 本阶段只写文件，不执行 `git commit` / `git push` / 创建 PR。知识文档的提交由用户显式触发（通常在后续 `/dev:ship` 或直接说"提交/commit/push"时）。
4. **Review 多轮循环。** `ce:compound` Phase 3 的可选领域审查执行修复循环。

## Overview

Phase 7 is the compound interest phase. It **detects** what just happened and **routes** to the right knowledge capture mechanism. Knowledge captured here is **automatically injected** into future Phase 3 planning and Phase 5 review via learnings-researcher.

Position in workflow: Phase 6 (ship) -> **Phase 7** -> Phase 1 (next work item, closes the loop)

## When to Use

- Just solved a hard bug or complex problem
- Shipped a feature and want to document decisions
- End of sprint / weekly review
- Discovered a reusable cross-project pattern

**Skip when:** Trivial change with nothing novel learned.

## Scene Detection

Analyze the conversation history and recent git activity to classify the trigger:

**Signal 1: Was a problem just solved?**
- Conversation contains debugging/investigation (keywords: "fixed", "root cause", "the issue was", "resolved", "that worked")
- Recent commits include `fix:` prefix
- -> Route A: Document the problem

**Signal 2: Was a feature just shipped?**
- Phase 6 just completed (PR merged, deploy verified)
- Recent commits include `feat:` prefix
- -> Route A (if non-trivial decisions were made) or skip (if straightforward)

**Signal 3: Is it end of sprint/week?**
- User explicitly mentions "retro", "weekly", "sprint review", "what did we do"
- -> Route B: Retrospective

**Signal 4: Was a reusable method discovered?**
- User mentions "this pattern works for any project", "we should always do this", "encode this as a skill"
- -> Route C: Write a skill

**Signal 5: Does the knowledge base feel stale?**
- User mentions "outdated", "stale", "contradicts", "wrong docs"
- `docs/solutions/` has files referencing deleted code paths
- -> Route D: Refresh

**Signal 6: Can an existing skill be improved?**
- Same review finding (same category) appeared 3+ times in `learnings.jsonl`
- Same friction point appears in consecutive retro reports
- Upstream submodule (compound-engineering / superpowers / gstack) has new capabilities
- A skill references a tool/skill name that no longer exists
- -> Route E: Skill improvement

**Signal 7: Is there external knowledge to ingest?**
- User provides an article, paper, document, or URL ("这篇文章", "研究一下这个", "ingest this")
- User shares learnings from another project or team
- -> Route F: Wiki Ingest

## Routing

```
Completed work
  |
  +-- [Problem solved] -----------> Route A: /ce:compound
  |   "fixed", "root cause",        -> docs/solutions/<category>/<slug>.md
  |   "the issue was"
  |
  +-- [Sprint/week end] ----------> Route B: /gstack-retro
  |   "retro", "weekly review"       -> Retro report + trend snapshot
  |
  +-- [Reusable method found] ----> Route C: superpowers:writing-skills
  |   "always do this",              -> ~/.claude/skills/<name>/SKILL.md
  |   "encode as a skill"
  |
  +-- [Knowledge stale] ----------> Route D: /ce:compound-refresh
  |   "outdated", "contradicts"      -> Updated/merged/deleted docs
  |
  +-- [Skill improvable] ---------> Route E: superpowers:writing-skills (REFACTOR)
  |   repeated findings,             -> Updated SKILL.md + workflow doc
  |   upstream new capabilities,
  |   process friction
  |
  +-- [External knowledge] -------> Route F: Wiki Ingest
  |   article, paper, doc, URL       -> wiki/sources/ + entity/concept updates
  |   cross-project learnings         -> index.md + log.md updated
  |
  +-- [Nothing novel] ------------> SKIP Phase 7 -> /dev:discover (next item)
```

## Workflow

0. **Skill self-review (L2 信号收集)**

   在执行任何 Route 之前，先收集本 session 的 skill 执行信号。

   宣告（中文）："正在收集本 session 的 skill 执行信号..."

   - 运行 `scripts/supervise/extract_signals.py` 处理当前 session transcript
   - Transcript 路径发现：`ls -t ~/.claude/projects/$(pwd | tr '/' '-')/conversations/*.jsonl 2>/dev/null | head -1`，或使用 `$CLAUDE_PROJECT_DIR/conversations/` 下最新的 `.jsonl` 文件
   - 若脚本不存在或执行失败 → 静默跳过，不打断后续流程
   - 若提取到信号 → 按 skill 分组追加到 `docs/supervise/feedback/<skill-name>.md`
   - 每条格式：`- YYYY-MM-DD / sess: <path> / 信号: <type> / 证据: <evidence> / phase: <phase>`
   - 若无信号 → 静默跳过，不创建空 feedback 文件
   - 确保 `docs/supervise/feedback/` 目录存在（不存在则创建）

1. **Detect scene** and announce (中文):
   - "Bug 修复伴随根因分析 -- 记录解决方案。"
   - "迭代结束 -- 运行回顾分析趋势。"
   - "发现可复用模式 -- 用 TDD 创建 skill。"

2. **Execute detected route**

   **Route A: `/ce:compound`** (problem documentation)
   - Parallel sub-agents: Context Analyzer + Solution Extractor + Related Docs Finder
   - Auto-detects track: Bug (Problem->Root Cause->Solution->Prevention) vs Knowledge (Context->Guidance->Why->Examples)
   - Auto-detects overlap with existing docs (5 dimensions, High/Moderate/Low)
   - REVIEW (Optional): domain-specific review auto-triggered by problem type (最多 3 轮):
     - `performance_issue` -> `performance-oracle`
     - `security_issue` -> `security-sentinel`
     - `database_issue` -> `data-integrity-guardian`
   - Selective refresh if new doc contradicts existing docs

   **Route B: `/gstack-retro`** (retrospective)
   - Analyzes: commit frequency, code LOC, test ratios, file hotspots, AI-assisted %
   - Compares vs last retro for trends
   - Per-contributor praise and growth areas

   **Route C: `superpowers:writing-skills`** (skill creation)
   - RED: pressure scenario without skill, document failures
   - GREEN: write minimal skill that fixes those failures
   - REFACTOR: close loopholes, re-test

   **Route D: `/ce:compound-refresh`** (knowledge maintenance)
   - Classify each doc: Keep / Update / Consolidate / Replace / Delete
   - Evidence-based: check if referenced files still exist

   **Route E: `superpowers:writing-skills`** (skill improvement, REFACTOR mode)
   - Analyze gap: which route/rule/signal is missing or outdated
   - For upstream updates: read new SKILL.md/changelog, judge impact on dev:* routing
   - For repeated findings: aggregate from `learnings.jsonl`, locate missing detection signal
   - For friction: trace retro friction points to specific Phase's Scene Detection
   - Update SKILL.md + `docs/ai-coding-workflow.md` in sync
   - Verify: improved skill routes correctly on historical cases from retro

   **Route F: Wiki Ingest** (knowledge compilation)
   - 委托给 **`/dev:wiki-ingest`** —— 它负责抽取实体/概念/决策、规划页面改动、GATE 展示清单、写入 5-15 页、追加 log.md、跨层传播询问
   - 本路由只负责把源路径(`docs/solutions/<file>.md` / retro 报告路径 / URL)传给 `dev:wiki-ingest`,具体编译逻辑在那边

3. **Wiki Ingest (auto, after Route A and B)**
   - After `ce:compound` writes `docs/solutions/*.md` -> 自动调 `/dev:wiki-ingest` 处理项目 wiki
   - After `gstack-retro` completes -> 自动调 `/dev:wiki-ingest` 处理 retro 发现
   - Announce (中文): "Solution 已写入 docs/solutions/。委托 dev:wiki-ingest 编译进 wiki..."

3. **Verify knowledge is discoverable**
   - `docs/solutions/`: YAML frontmatter searchable? `AGENTS.md`/`CLAUDE.md` points to it?
   - `learnings.jsonl`: entry written by gstack/learn (automatic)?

4. **Next**: `/dev:discover` (Phase 1) -- closes the loop

## Knowledge Feedback Loop

```
Phase 4 (ce:work) -- solve problem --> Phase 7 (ce:compound) -- docs/solutions/
                                                                      |
Phase 3 (ce:plan) <-- learnings-researcher auto-searches -------------+
Phase 5 (ce:code-review) <-- learnings-researcher always-on ---------------+
All gstack skills <-- preamble auto-searches learnings.jsonl ---------+
```

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Completed work (shipped feature, resolved bug, finished sprint) |
| **Output** | `docs/solutions/*.md`, `learnings.jsonl`, optional `SKILL.md` |
| **Next** | `/dev:discover` (Phase 1) -- closes the loop |

## Dual-Layer Architecture

| Layer | Mechanism | Granularity | Trigger |
|---|---|---|---|
| `gstack/learn` | Automatic, passive | One-line insight | Every gstack skill completion |
| `ce:compound` | Manual, active | Full document | Explicit invocation after solving a problem |

Knowledge is not just recorded -- it is automatically injected into future planning and review. That is what makes it compound.

## Iron Law

> Knowledge captured now compounds into every future planning and review cycle. Skipping documentation is borrowing from your future self.
