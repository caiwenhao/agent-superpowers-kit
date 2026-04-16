---
name: dev-ship
description: 用于已验证的工作在 Codex CLI 会话中已经准备好进入 PR、合并、部署或部署后检查时
---

# dev-ship

## Decision Rules
- verified code only
- choose lightweight or full ship path from project state
- unresolved review feedback blocks delivery
- keep the literal invocation surface on `$dev-ship`
- user-facing status and gate reporting stays in Chinese

## Delivery Paths
| Project State | Route |
|---|---|
| small verified change with no release ceremony needed | `git-commit-push-pr`, then `land-and-deploy` when deployment is requested |
| release flow, versioned project, or broader delivery ceremony needed | `ship`, then `document-release` when docs or release notes need to be synced, then `land-and-deploy` |

## Stop Conditions
- unresolved review feedback
- missing verification evidence
- merge or deployment would be destructive or materially branching without user confirmation
