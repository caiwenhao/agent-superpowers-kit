# Codex Skills

This directory exposes the Codex-native `dev:*` phase suite defined from [docs/ai-coding-workflow.md](/root/code/agent-superpowers-kit/docs/ai-coding-workflow.md).

## Bundle

| Phase | Skill | Primary lane |
|---|---|---|
| 入口编排 | `$dev-flow` | inspect repo state, resume or route |
| 发现 | `$dev-discover` | `ce:ideate` / `office-hours` / `ce:brainstorm` / `document-review` |
| 设计 | `$dev-design` | `design-consultation` / `design-shotgun` / `plan-design-review` |
| 规划 | `$dev-plan` | `ce:plan` + `plan-eng-review` (+ `autoplan` / `plan-design-review`) |
| 实现 | `$dev-code` | `ce:work` (+ `test-driven-development` / `systematic-debugging` / `frontend-design`) |
| 验证 | `$dev-verify` | `ce:review` (+ `test-browser` / `qa` / `design-review` / `cso` / `benchmark`) |
| 交付 | `$dev-ship` | `git-commit-push-pr` or `ship`, then `land-and-deploy` |
| 沉淀 | `$dev-learn` | `ce:compound` / `retro` / `ce:compound-refresh` / `writing-skills` |

## Structure

- `plugins/dev/skills/` is the authored source of truth.
- `codex-skills/` is the human-facing bundle view requested for this repo.
- `.codex/skills/` is the Codex runtime discovery path.
- `.agents/skills/` remains the legacy compatibility mirror.

Each `codex-skills/<skill>/SKILL.md` file is a symlink to the canonical skill source, so updates stay single-source.

## Use

- Browse this directory when you want the packaged Codex-facing workflow view.
- Activate repo-local runtime discovery with `omx setup --scope project` or a `CODEX_HOME=./.codex` launch.
- Invoke the suite through `$dev-flow` and the other `$dev-*` names; `dev:*` stays the public phase vocabulary.

## Contracts

- [alias-contract.md](/root/code/agent-superpowers-kit/codex-skills/alias-contract.md)
- [testing-matrix.md](/root/code/agent-superpowers-kit/codex-skills/testing-matrix.md)

## Validation

```bash
bash plugins/dev/tests/validate-frontmatter.sh
bash plugins/dev/tests/validate-discovery.sh
bash plugins/dev/tests/validate-bundle.sh
bash plugins/dev/tests/validate-trigger-fixtures.sh
bash plugins/dev/tests/validate-phase-contract.sh
```

Optional stronger smoke test:

```bash
bash plugins/dev/tests/validate-runtime-smoke.sh
```
