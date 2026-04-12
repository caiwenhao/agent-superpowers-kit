---
name: dev-flow
description: Use when starting a development task, resuming interrupted work, or when the correct workflow phase is unclear in a Codex CLI session
---

# dev-flow

## Overview
`$dev-flow` is the top-level phase router for Codex CLI work.

Keep the skill thin: inspect the current repo state, choose the right phase, and hand off. User-facing status, gate prompts, and pause/resume guidance should stay in Chinese where they are shown to the user. Literal skill invocation stays on `$dev-flow` and the other `$dev-*` forms; `dev:*` is phase vocabulary only.

## When to Use
- starting new work
- resuming interrupted work
- phase unclear

## Entry Signals
- active plan artifacts
- dirty branch
- user asks to ship
- user provides plan path

## Decision Rules
- inspect artifacts first
- resume before restarting
- skip only when explicit phase-skip conditions apply
- route based on current repo evidence before asking the user for restatement
- keep the invocation surface consistent with `$dev-*`, not `dev:*`

## REQUIRED SUB-SKILLS
- `dev-discover`
- `dev-design`
- `dev-plan`
- `dev-code`
- `dev-verify`
- `dev-ship`
- `dev-learn`

## Gate / Stop Conditions
- stop at each phase gate and report in Chinese
- stop when a required artifact or verification proof is missing
- stop and surface destructive or materially branching actions before continuing

## Common Mistakes
- restarting discovery when an active plan already exists
- treating `dev:*` as literal invocation syntax or actual frontmatter names
