---
name: dev-flow
description: 用于开始开发任务、恢复中断工作，或在 Codex CLI 会话中当前应进入哪个 dev 阶段还不明确时
---

# dev-flow

`$dev-flow` is the thin phase router for Codex CLI work.

Keep it narrow: inspect repo state, choose the right phase, and hand off. User-facing status, gate prompts, and pause/resume guidance stay in Chinese. Literal invocation stays on `$dev-flow` and the other `$dev-*` names; `dev:*` is phase vocabulary only.

## Routing Rules
| Signal | Outcome |
|---|---|
| active plan or other unfinished work | resume the appropriate later phase, usually `$dev-code`, `$dev-verify`, or `$dev-ship` |
| dirty branch with review evidence | route to `$dev-ship` when delivery-ready; otherwise route to `$dev-verify` |
| explicit ship request | route to `$dev-ship` |
| plan path provided | route to `$dev-code` |
| no relevant artifacts or task still vague | route to `$dev-discover` |

## Decision Rules
- inspect artifacts first
- resume before restarting
- skip only when explicit phase-skip conditions apply
- route based on current repo evidence before asking the user for restatement
- keep the invocation surface consistent with `$dev-*`, not `dev:*`

## Gate / Stop Conditions
- stop at each phase gate and report in Chinese
- stop when a required artifact or verification proof is missing
- stop and surface destructive or materially branching actions before continuing

## Common Mistakes
- restarting discovery when an active plan already exists
- treating `dev:*` as literal invocation syntax or actual frontmatter names
