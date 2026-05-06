---
name: dev-learn
description: "Use after solving a significant problem, before shipping nontrivial work whose knowledge artifacts should be delivered with the code, after shipping a feature, or after completing a sprint."
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
2. **工作区前置（强制）。** 在写入任何知识文档（`docs/solutions/`、`learnings.jsonl`、wiki 页等）之前，执行 `git rev-parse --abbrev-ref HEAD` 检查当前分支。若在 main/master 或未进入任务专属 worktree，STOP 并调用 `using-git-worktrees` 创建工作区后再继续（路径 `<repo>/.worktrees/<task-name>/`；规范名与环境别名见 `claude-skills/README.md` 的 Skill Naming 表）。
3. **提交由用户触发。** 本阶段只写文件，不执行 `git commit` / `git push` / 创建 PR。知识文档的提交由用户显式触发。
4. **默认不为模式反复确认。** Route A 默认采用 **Full + session history**。只有在用户明确要求轻量模式、明确说不要查会话历史、或存在真实 blocker/歧义时才提问。

## Overview

Phase 7 is the compound interest phase. It **detects** what just happened and **routes** to the right knowledge capture mechanism. Knowledge captured here is **automatically injected** into future Phase 3 planning and Phase 5 review via learnings-researcher.

Position in workflow: Phase 5.5 pre-ship capture when knowledge artifacts should ship with the diff; otherwise Phase 6 (ship) -> **Phase 7** post-ship closeout -> Phase 1 (next work item).

## When to Use

- Just solved a hard bug or complex problem
- Phase 5 passed and the work produced knowledge artifacts that should be included before `dev:ship`
- Shipped a feature and want to document decisions
- End of sprint / weekly review
- Discovered a reusable cross-project pattern

**Skip when:** Trivial change with nothing novel learned.

## Scene Detection

Analyze the conversation history and recent git activity to classify the trigger:

**Signal 1: Was a problem just solved?**
- Conversation contains debugging/investigation (keywords: "fixed", "root cause", "the issue was", "resolved")
- Recent commits include `fix:` prefix
- -> Route A: Document the problem

**Signal 2: Is a feature ready to ship, or was it just shipped?**
- Phase 5 passed and the feature introduced non-trivial decisions
- Phase 6 just completed (PR merged, deploy verified)
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
- Same review finding appeared 3+ times in `learnings.jsonl`
- Same friction point appears in consecutive retro reports
- -> Route E: Skill improvement

**Signal 7: Is there external knowledge to ingest?**
- User provides an article, paper, document, or URL
- -> Route F: Wiki Ingest
