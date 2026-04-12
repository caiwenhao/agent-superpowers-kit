---
name: dev-ship
description: Use when verified work is ready for PR, merge, deployment, or post-deploy checks in a Codex CLI session
---

# dev-ship

## Decision Rules
- verified code only
- choose lightweight or full ship path from project state
- unresolved review feedback blocks delivery
- keep the literal invocation surface on `$dev-ship`

## Delivery Paths
| Project State | Route |
|---|---|
| small verified change with no release ceremony needed | `git-commit-push-pr`, then `land-and-deploy` when deployment is requested |
| release flow, versioned project, or broader delivery ceremony needed | `ship`, then `document-release` when docs or release notes need to be synced, then `land-and-deploy` |

## Stop Conditions
- unresolved review feedback
- missing verification evidence
- merge or deployment would be destructive or materially branching without user confirmation
