---
name: dev-learn
description: 用于有意义的工作已经完成，且在 Codex CLI 会话中应该沉淀可复用知识或刷新既有模式时
---

# dev-learn

## Decision Rules
- solved problem -> `ce:compound`
- iteration end or retrospective request -> `retro`
- stale knowledge -> `ce:compound-refresh`
- reusable method -> `writing-skills`
- no durable learning -> skip and close the loop cleanly
- user-facing status and gate reporting stays in Chinese

## Exit / Handoff
| Condition | Outcome |
|---|---|
| reusable problem-solving knowledge exists | route to `ce:compound` |
| iteration-end or retrospective review is requested | route to `retro` |
| existing knowledge is stale or contradictory | route to `ce:compound-refresh` |
| the session produced a repeatable workflow or reusable agent behavior | route to `writing-skills` |
| nothing reusable was learned | skip Phase 7 |
