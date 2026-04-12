---
name: dev-design
description: Use when approved requirements involve UI, visual behavior, or interaction changes and a Codex CLI session must decide the correct design lane
---

# dev-design

## Decision Rules
- pure backend -> skip design
- existing design system + no new visual language -> route lightly
- new or unclear visual direction -> route to design exploration
- keep the literal invocation surface on `$dev-design`

## Design Lanes
| Condition | Outcome |
|---|---|
| pure backend or non-visual work | skip Phase 2 and hand off to `$dev-plan` |
| established design system and the change fits it | route lightly through `plan-design-review` |
| no design system, or the visual direction is new or unclear | route to `design-consultation` or `design-shotgun` before planning |
