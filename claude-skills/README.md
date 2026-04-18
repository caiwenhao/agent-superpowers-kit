# Claude Skills — `dev:*` Phase Suite

This directory is the **canonical source** for the 8-phase `dev:*` development workflow skills. See [docs/ai-coding-workflow.md](../docs/ai-coding-workflow.md) for the full workflow design.

## Bundle

| Phase | Skill | Primary lane |
|---|---|---|
| 入口编排 | `dev-flow` | inspect repo state, resume or route |
| 发现 | `dev-discover` | `ce:ideate` / `office-hours` / `ce:brainstorm` / `document-review` |
| 设计 | `dev-design` | `design-consultation` / `design-shotgun` / `plan-design-review` |
| 规划 | `dev-plan` | `ce:plan` + `plan-eng-review` (+ `autoplan` / `plan-design-review`) |
| 实现 | `dev-code` | `ce:work` (+ `test-driven-development` / `systematic-debugging` / `frontend-design` / `dev-browser`) → 收尾 `/simplify`（Phase 4→5 过渡关）|
| 验证 | `dev-verify` | `ce:review` (+ `test-browser` / `dev-browser` / `qa` / `design-review` / `cso` / `benchmark`) |
| 交付 | `dev-ship` | `git-commit-push-pr` or `ship`, then `land-and-deploy` (+ `dev-browser` canary 烟测) |
| 沉淀 | `dev-learn` | `ce:compound` / `retro` / `ce:compound-refresh` / `writing-skills` |

## Discovery Paths

`claude-skills/` is the authored single source of truth. Each harness finds skills via its own convention:

| Harness | Discovery path | Mechanism |
|---|---|---|
| Claude Code | `<proj>/.claude/skills/<name>/SKILL.md` | symlink into `claude-skills/` (or integral symlink of the whole directory) |
| Codex / OMX | `<proj>/.agents/skills/<name>/SKILL.md` | per-skill symlink into `claude-skills/` |

Each runtime path's `SKILL.md` is a symlink to `claude-skills/<name>/SKILL.md`, keeping a single source.

## Cross-harness Compatibility

- **SKILL.md format** (frontmatter + Markdown): identical across Claude Code and Codex.
- **Downstream skill references** (e.g. `ce:brainstorm`, `gstack-*`, `compound-engineering:git-worktree`): assume a Claude Code environment. On Codex, skills without a Codex equivalent degrade gracefully (user executes the intent manually or picks a `superpowers:*` fallback where provided).
- **No Claude-Code-only tool calls** (`Agent`, `TodoWrite`, `Skill(...)`) appear in the skill bodies — all invocations are described in neutral prose.

## Iron Laws (across all phases)

1. **设计先于实现** — no code before requirements approval
2. **测试先于代码** — no production code before failing test
3. **根因先于修复** — no fix without understanding why
4. **证据先于断言** — no "it works" without proof
5. **验证先于采纳** — verify review feedback before implementing
6. **工作区先于工作** — task-scoped worktree/feature branch required before creating any doc or code
7. **提交由用户触发** — Phase 1-5/7 never auto-commit; commits happen only in Phase 6 `/dev:ship` via explicit user trigger

See [docs/ai-coding-workflow.md](../docs/ai-coding-workflow.md) for full routing logic, scene detection, and skill-composition rules per phase.
