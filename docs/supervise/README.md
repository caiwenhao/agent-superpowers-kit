# dev-supervise

`dev:*` skill 库的元 skill：监督自身执行、收集纠正信号、产出改进建议。

## 三层结构

| 层 | 机制 | 触发 |
|---|---|---|
| L1 实时拦截 | `scripts/supervise/iron_law_guard.py` hook | 每次工具调用 |
| L2 会话复盘 | `scripts/supervise/extract_signals.py` | Phase 5.5 pre-ship 或 Phase 7 (dev-learn) |
| L3 历史扫描 | `/dev:supervise` 命令 | 用户手动触发，或 `dev:flow` Phase 5.5 有自省信号时按需触发 |

## L1 Hook 注册

在 `.claude/settings.json` 中添加以下配置（或使用 `/update-config`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 <repo>/scripts/supervise/iron_law_guard.py"
          }
        ]
      }
    ]
  }
}
```

将 `<repo>` 替换为仓库绝对路径。

## 事件日志

L1 拦截/警告事件记录在 `~/.claude/state/supervise-incidents.jsonl`（不入 git）。

## 反馈队列

L2 信号按 skill 分组追加到 `docs/supervise/feedback/<skill-name>.md`（入 git）。

## 聚合报告

L3 project scope 报告写入 `docs/supervise/aggregated/<date>.md`（入 git）。
L3 global scope 报告写入 `~/.claude/skill-feedback/aggregated-<date>.md`（不入 git）。
