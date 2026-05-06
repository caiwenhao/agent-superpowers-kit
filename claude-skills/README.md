# Claude Skills — `dev:*` Phase Suite

This directory is the **canonical source** for the `dev:*` development workflow skills. See [docs/ai-coding-workflow.md](../docs/ai-coding-workflow.md) for the full workflow design.

## Bundle

| Phase | Skill | Primary lane |
|---|---|---|
| 入口编排 | `dev-flow` | inspect repo state, resume or route |
| 发现 | `dev-discover` | `ce-ideate` / `office-hours` / `ce-brainstorm` / `document-review` |
| 设计 | `dev-design` | `gstack-design-consultation` / `gstack-design-shotgun` / `gstack-plan-design-review` |
| 规划 | `dev-plan` | `ce-plan` + `gstack-plan-eng-review` (+ `gstack-autoplan` / `gstack-plan-design-review`) |
| 实现 | `dev-code` | `ce-work` (+ `test-driven-development` / `systematic-debugging` / `frontend-design` / `dev-browser`) → 收尾 `/simplify`（Phase 4→5 过渡关）|
| 验证 | `dev-verify` | `ce-review` (+ `test-browser` / `dev-browser` / `gstack-qa` / `gstack-design-review` / `gstack-cso` / `gstack-benchmark`) |
| 预交付判断 | `dev-flow` 内置 Phase 5.5 | 按需触发 `dev-learn` / `dev-supervise`，让知识和自省证据在 `dev-ship` 前进入同一交付 diff |
| 交付 | `dev-ship` | `git-commit-push-pr` or `gstack-ship`, then `gstack-land-and-deploy` (+ `dev-browser` canary 烟测) |
| 沉淀 | `dev-learn` | `ce-compound` / `gstack-retro` / `ce-compound-refresh` / `writing-skills` |
| 初始化 | `dev-init` | 写 CLAUDE.md preamble + 建 AGENTS.md 软链 + 迁移仓库级技能目录到 cross-harness 双软链布局,收尾调 dev:doctor |
| 诊断 | `dev-doctor` | 扫描下游依赖安装状态(Claude Code + Codex 两侧路径),报告缺失 + phase 降级评估(只读) |
| Wiki 查询 | `dev-wiki-search` | grep-based 双层 wiki 查询(项目 wiki + ~/.claude/wiki),供 discover/plan 注入已有知识(只读,无 LLM) |
| Wiki 编译 | `dev-wiki-ingest` | 把 docs/solutions/ retro 报告 / 外部源编译进 wiki(5-15 页/次),源不可变,带 GATE |
| Wiki 初始化 | `dev-wiki-init` | 创建项目或全局 wiki 骨架,供 search/ingest 使用 |
| 监督 | `dev-supervise` | 扫描会话历史，汇总 skill 执行质量（纠正信号、铁律违例），输出改进报告（只读） |

## Discovery Paths

`claude-skills/` is the authored single source of truth. Each harness finds skills via its own convention:

| Harness | Discovery path | Mechanism |
|---|---|---|
| Claude Code | `<proj>/.claude/skills/<name>/SKILL.md` | symlink into `claude-skills/` (or integral symlink of the whole directory) |
| Codex | `<proj>/.agents/skills/<name>/SKILL.md` | per-skill symlink into `claude-skills/` |

Each runtime path's `SKILL.md` is a symlink to `claude-skills/<name>/SKILL.md`, keeping a single source.

## Skill Naming — Cross-Harness Canon

**`dev-*` SKILL bodies cite downstream skills by their Codex-flat name.** Both Claude Code and Codex resolve the same canonical name; where Claude Code expects a plugin prefix, the agent substitutes it automatically using the table below.

| Role | Canonical name (use in SKILL body) | Claude Code alias | Codex alias |
|---|---|---|---|
| worktree 创建 | `using-git-worktrees` | `superpowers:using-git-worktrees` | `using-git-worktrees` |
| 头脑风暴 | `ce-brainstorm` | `compound-engineering:ce-brainstorm` | `ce-brainstorm` |
| 产品 ideate | `ce-ideate` | `compound-engineering:ce-ideate` | `ce-ideate` |
| 规划 | `ce-plan` | `compound-engineering:ce-plan` | `ce-plan` |
| 代码审查 | `ce-review` | `compound-engineering:ce-review` | `ce-review` |
| 实现执行 | `ce-work` | `compound-engineering:ce-work` | `ce-work` |
| 问题沉淀 | `ce-compound` | `compound-engineering:ce-compound` | `ce-compound` |
| 刷新沉淀 | `ce-compound-refresh` | `compound-engineering:ce-compound-refresh` | `ce-compound-refresh` |
| 调试 | `ce-debug` | `compound-engineering:ce-debug` | `ce-debug` |
| 性能/重构优化 | `ce-optimize` | `compound-engineering:ce-optimize` | `ce-optimize` |
| PR 描述生成 | `ce-pr-description` | `compound-engineering:ce-pr-description` | `ce-pr-description` |
| Slack 研究 | `ce-slack-research` | `compound-engineering:ce-slack-research` | `ce-slack-research` |
| 会话检索 | `ce-sessions` | `compound-engineering:ce-sessions` | `ce-sessions` |
| 文档审查 | `document-review` | `compound-engineering:document-review` | `document-review` |
| Office Hours | `office-hours` | `gstack-office-hours` | `office-hours` |
| 领域对齐 grilling | `grill-with-docs` | `grill-with-docs` | `grill-with-docs` |
| 决策树 grilling | `grill-me` | `grill-me` | `grill-me` |
| PRD 合成 | `to-prd` | `to-prd` | `to-prd` |
| 头脑风暴（SP） | `brainstorming` | `superpowers:brainstorming` | `brainstorming` |
| 写计划（SP） | `writing-plans` | `superpowers:writing-plans` | `writing-plans` |
| TDD | `test-driven-development` | `superpowers:test-driven-development` | `test-driven-development` |
| 完成前验证 | `verification-before-completion` | `superpowers:verification-before-completion` | `verification-before-completion` |
| 审查接收 | `receiving-code-review` | `superpowers:receiving-code-review` | `receiving-code-review` |
| 审查请求 | `requesting-code-review` | `superpowers:requesting-code-review` | `requesting-code-review` |
| 写 Skill | `writing-skills` | `superpowers:writing-skills` | `writing-skills` |
| commit+push+PR | `git-commit-push-pr` | `compound-engineering:git-commit-push-pr` | `git-commit-push-pr` |
| 浏览器测试 | `test-browser` | `compound-engineering:test-browser` | `test-browser` |
| PR 评论解决 | `pr-comment-resolver` | `compound-engineering:pr-comment-resolver` | `pr-comment-resolver` |
| 设计咨询 | `gstack-design-consultation` | `gstack-design-consultation` | `gstack-design-consultation` |
| 设计探索 | `gstack-design-shotgun` | `gstack-design-shotgun` | `gstack-design-shotgun` |
| 计划工程审查 | `gstack-plan-eng-review` | `gstack-plan-eng-review` | `gstack-plan-eng-review` |
| 计划设计审查 | `gstack-plan-design-review` | `gstack-plan-design-review` | `gstack-plan-design-review` |
| 计划 DevEx 审查 | `gstack-plan-devex-review` | `gstack-plan-devex-review` | `gstack-plan-devex-review` |
| 计划全量审查 | `gstack-autoplan` | `gstack-autoplan` | `gstack-autoplan` |
| 全站 QA | `gstack-qa` | `gstack-qa` | `gstack-qa` |
| 设计审查 | `gstack-design-review` | `gstack-design-review` | `gstack-design-review` |
| 安全审查 | `gstack-cso` | `gstack-cso` | `gstack-cso` |
| LLM 审查 | `gstack-review` | `gstack-review` | `gstack-review` |
| 性能基线 | `gstack-benchmark` | `gstack-benchmark` | `gstack-benchmark` |
| DevEx 审查 | `gstack-devex-review` | `gstack-devex-review` | `gstack-devex-review` |
| 回顾 | `gstack-retro` | `gstack-retro` | `gstack-retro` |
| 被动 learnings | `gstack-learn` | `gstack-learn` | `gstack-learn` |
| 发布路径 | `gstack-ship` | `gstack-ship` | `gstack-ship` |
| 文档发布 | `gstack-document-release` | `gstack-document-release` | `gstack-document-release` |
| 合并部署 | `gstack-land-and-deploy` | `gstack-land-and-deploy` | `gstack-land-and-deploy` |
| 部署配置 | `gstack-setup-deploy` | `gstack-setup-deploy` | `gstack-setup-deploy` |
| 录屏 | `feature-video` | `feature-video` | `feature-video` |
| learnings 搜索 | `learnings-researcher` | `learnings-researcher` | `learnings-researcher` |
| 架构深化 | `improve-codebase-architecture` | `improve-codebase-architecture` | `improve-codebase-architecture` |
| gstack-* 全家桶 | `gstack-<name>` | `gstack-<name>` | `gstack-<name>` |

**规则**：`dev-*` SKILL 正文统一写"canonical name"列（即 Codex 扁平名）。agent 在 Claude Code 里会自动加 `compound-engineering:` / `superpowers:` 前缀；Codex 直接匹配。若将来新增下游 skill，先在本表补行，再在 SKILL 里引用。

## Cross-Harness Compatibility

- **SKILL.md format** (frontmatter + Markdown): identical across Claude Code and Codex.
- **Downstream skill references**: use the canonical flat name from the table above. Both harnesses resolve it.
- **Reviewer fanout parity**: when `document-review` or `ce-review` is used, both Claude Code and Codex should dispatch reviewer roles as multi-agent review when subagent/task spawning is available. Single-thread synthesis is a fallback only when the harness truly cannot spawn reviewer agents.
- **`gstack-*` availability**: assumed to be installed in both harnesses. `dev-doctor` probes and reports missing ones, but does not auto-install.
- **No Claude-Code-only tool calls** (`Agent`, `TodoWrite`, `Skill(...)`) appear in the skill bodies — all invocations are described in neutral prose.

## Iron Laws (across all phases)

1. **设计先于实现** — no code before requirements approval
2. **测试先于代码** — no production code before failing test
3. **根因先于修复** — no fix without understanding why
4. **证据先于断言** — no "it works" without proof
5. **验证先于采纳** — verify review feedback before implementing
6. **工作区先于工作** — task-scoped worktree under `<repo>/.worktrees/<name>/` required before creating any doc or code
7. **提交由用户触发** — Phases 1-5/7 never auto-commit; commits only happen in Phase 6 `/dev:ship` after explicit user authorization. `mode:auto` is not ship authorization.

See [docs/ai-coding-workflow.md](../docs/ai-coding-workflow.md) for full routing logic, scene detection, and skill-composition rules per phase.
