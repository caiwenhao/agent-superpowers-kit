---
name: dev-supervise
description: "Use to review skill execution quality when there are user corrections, repeated rework, iron law incidents, skill/process changes, or pre-ship evidence needs."
---

<SUPERVISE-CHECK>
执行前自检（Codex 环境必读，Claude Code 环境由 L1 hook 覆盖）：
1. 铁律 6（工作区）：运行 `git rev-parse --abbrev-ref HEAD`。若在 main/master 且不在 `.worktrees/` 子路径 → STOP，创建 worktree。
2. 铁律 7（提交触发）：本 phase 禁止 `git commit` / `git push` / `gh pr create`。提交仅在 `/dev:ship` 中由用户触发。
3. 铁律 4（证据先行）：声称"完成/通过"前必须有测试命令的实际输出作为证据。
</SUPERVISE-CHECK>

# dev:supervise -- "技能自省"

## Overview

`dev-supervise` 是 `dev:*` skill 库的元 skill：扫描历史 session，收集纠正信号，产出按 skill 排行的改进建议报告。

它不是常规业务 phase，但可以被 `dev-flow` 的 Phase 5.5 交付前自省判断按需调用。其他入口为本命令（L3）和 `dev-learn` 中的 `skill-self-review` 子步（L2）。

## When to Use

- 想了解哪些 skill 被用户纠正最多
- 定期复盘 skill 质量趋势
- 收集改进证据，为 SKILL.md 修改提供数据支撑
- Phase 5 已通过、准备 `dev:ship`，但本次 diff 修改了 skill / workflow / supervise 相关文件
- Phase 5 已通过、准备 `dev:ship`，且本 session 出现用户打断、回滚、重复返工或 L1 iron law 事件

## Parameters

- `--since <duration>`: 回溯时间窗口，默认 `14d`（支持 `7d`, `24h`, `30d`）
- `--scope project|global`: 扫描范围，默认 `project`
  - `project`: 仅扫当前 repo 相关的 session
  - `global`: 扫所有 session，报告输出到 `~/.claude/skill-feedback/`

## Workflow

1. **宣告**（中文）："开始扫描历史 session，收集 skill 执行信号..."

2. **执行扫描**
   ```bash
   REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
   SCRIPT="$REPO_ROOT/scripts/supervise/scan_history.py"
   if [ ! -f "$SCRIPT" ]; then
     echo "⚠️  scripts/supervise/scan_history.py 未找到（跑 /dev:doctor 确认仓库完整性）"
     exit 0
   fi
   python3 "$SCRIPT" --since <duration> --scope <scope>
   ```

3. **保存报告**（将 stdout 重定向到目标文件）
   - `--scope project` → 重定向到 `docs/supervise/aggregated/<date>.md`（入 git）
   - `--scope global` → 重定向到 `~/.claude/skill-feedback/aggregated-<date>.md`（不入 git）

4. **宣告结果摘要**（中文）：
   - "扫描完成。共扫描 N 个 session，发现 M 个信号。"
   - "Top 问题：dev-plan / 重做 (12次)、dev-ship / L1 拦截 (8次)"
   - "报告已写入 docs/supervise/aggregated/2026-04-25.md"

5. **不修改任何 SKILL.md** — 仅报告，改进由人工落地

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | `--since` 时间窗口 + `--scope` 扫描范围 |
| **Output** | Markdown 排行榜报告 + 结构化改进建议 |
| **Next** | 人工阅读报告 → 决定是否修改 SKILL.md |

## Self Boundary

- 不作为 `dev-flow` 的常规串行 phase；只允许 Phase 5.5 在有自省信号时按需触发
- 不自动 patch SKILL.md
- 不读取 session 原文内容（仅引用路径+行号）
- global scope 输出到家目录，避免跨 repo 数据泄漏
