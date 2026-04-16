---
name: dev-design
description: 用于已批准需求涉及 UI、视觉行为或交互变更，且在 Codex CLI 会话中需要确定正确设计路径时
---

# dev-design

## Decision Rules
- pure backend -> skip design
- existing design system + no new visual language -> route lightly
- new or unclear visual direction -> route to design exploration
- keep the literal invocation surface on `$dev-design`
- user-facing status and gate reporting stays in Chinese

## Design Lanes
| Condition | Outcome |
|---|---|
| pure backend or non-visual work | skip Phase 2 and hand off to `$dev-plan` |
| established design system and the change fits it | route lightly through `plan-design-review` |
| no design system, or the visual direction is new or unclear | route to `design-consultation` or `design-shotgun` before planning |
