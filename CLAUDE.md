# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **skill library**, not an application. It authors an 8-skill `dev:*` orchestration layer that routes through a 7-phase AI coding workflow (discover → design → plan → code → verify → ship → learn), built on top of four upstream skill libraries vendored in-tree as reference sources.

There is no build, lint, or test target at the repo root. All "code" here is Markdown (`SKILL.md` files + design docs). `install-skills.sh` is a one-liner that lists discovered `SKILL.md` paths.

## Directory layout — what matters

| Path | Role |
|---|---|
| `claude-skills/` | **Single source of truth.** The 8 authored `dev-*/SKILL.md` files. Always edit here. |
| `.agents/skills/<name>/SKILL.md` | Codex/OMX runtime discovery path. Each entry is a **symlink** into `claude-skills/`. Never write real files here. |
| `.claude/skills/` | Claude Code runtime discovery path (may symlink to `claude-skills/`). |
| `docs/ai-coding-workflow.md` | **Authoritative workflow design.** 7-phase routing logic, scene detection, GATE mechanism, 7 iron laws + 编码行为约束. Read before editing any `dev-*` skill. |
| `docs/phase{1-7}-*-analysis.md` | Per-phase deep dives feeding the workflow doc. |
| `compound-engineering-plugin/`, `superpowers/`, `gstack/`, `agent-skills/` | Upstream skill libraries vendored as reference sources. Not edited from this repo — the `dev:*` layer delegates to them. |
| `oh-my-codex/` | External Codex orchestration layer (reference only; `.gitignore`d runtime data lives under `.omx/`). |
| `install-skills.sh` | Lists `.agents/skills/**/SKILL.md`. Used as a smoke check, not a real installer. |

## How `dev:*` composes

Each `dev-*/SKILL.md` is a **thin phase-gate router** — it detects context, announces the route in Chinese, then delegates to downstream skills. Most delegation targets (`ce:*`, `gstack-*`) live in the vendored upstream libraries.

- Claude Code environment: all referenced `ce:*` / `gstack-*` / `superpowers:*` skills are available via the installed plugins.
- Codex environment: `gstack-*` references degrade gracefully — users perform the step manually or substitute a `ce:*` / `superpowers:*` equivalent. We deliberately do **not** fork a Codex-specific variant; single-source is the working contract.

When editing a `dev-*` skill, verify that downstream references still resolve in Claude Code (the primary target) before worrying about Codex.

## Iron laws (codified in every `dev-*` skill)

These override generic coding practice. When in doubt, trust the skill body:

1. **设计先于实现** — never touch code before requirements approval
2. **测试先于代码** — no production code before a failing test
3. **根因先于修复** — no fix without understanding why
4. **证据先于断言** — no "it works" without running the command
5. **验证先于采纳** — verify review feedback before implementing
6. **工作区先于工作** — every `dev-*` phase starts by running `git rev-parse --abbrev-ref HEAD`; if on main/master or not in a task-scoped worktree, STOP and create one via `compound-engineering:git-worktree` (fallback `superpowers:using-git-worktrees`)
7. **提交由用户触发** — Phases 1-5 and 7 never `git commit` / `git push` / create PRs; commits only happen in Phase 6 (`/dev:ship`) after explicit user request

Rule 7 is strict: even when all tests pass and diffs look clean, leave changes staged/unstaged. The user triggers the commit.

## Language

User-facing status reports, GATE prompts, route announcements, and error messages in `dev-*` skills use **Chinese**. Skill names, file paths, shell commands, and code stay English. This is also the working language for conversations with the user.

## Editing workflow

- Edit `claude-skills/<name>/SKILL.md` (the real file). The `.agents/skills/` symlink updates automatically.
- If you change routing logic, update `docs/ai-coding-workflow.md` in the same change — the two are kept in sync.
- Do not create CLAUDE-specific variants of `dev-*` skills; cross-harness compat notes live in `claude-skills/README.md` instead.

## Commit messages

Use concise Chinese commit messages. First line states intent (为什么变，不是变了什么). Body optional — only when the change needs narrative context. Do not append AI-authorship footers unless the user asks.
