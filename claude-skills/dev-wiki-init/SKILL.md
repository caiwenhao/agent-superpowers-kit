---
name: dev-wiki-init
description: "Use when project wiki or global wiki is missing and a dev:* phase needs wiki search or wiki ingest to work."
---

# dev:wiki-init -- 初始化双层 wiki

## 通用规则

1. **始终用中文与用户交流。** 状态报告、GATE 提示使用中文。
2. **工作区前置。** 写项目 wiki 前必须在 `<repo>/.worktrees/<task-name>/`。只创建全局 wiki 时可在任意目录运行。
3. **提交由用户触发。** 创建文件后不 commit/push。

## When to Use

- `dev-wiki-search` 报告项目 wiki 和全局 wiki 都未初始化
- `dev-wiki-ingest` 需要写 wiki，但目标 wiki 不存在
- 用户要求“初始化 wiki / 创建知识库骨架”

## Quick Reference

| Need | Target |
|---|---|
| 项目知识库 | `<project>/wiki/` |
| 全局知识库 | `~/.claude/wiki/` |
| 两者都要 | 两侧都建同构骨架 |

## Common Mistakes

- 在主 checkout 上初始化项目 wiki
- 建空目录但没有 `index.md` / `log.md`
- 初始化后不返回调用方继续 search/ingest
- 把 init 当成自动提交动作

## Workflow

1. 判定目标：
   - 项目特定知识 -> `<project>/wiki/`
   - 跨项目通用知识 -> `~/.claude/wiki/`
   - 不确定 -> GATE 询问，带推荐项

2. 创建骨架：
   ```bash
   mkdir -p wiki/{sources,entities,concepts,synthesis}
   touch wiki/log.md
   cat > wiki/index.md <<'EOF'
   # Project Wiki

   ## Sources

   ## Entities

   ## Concepts

   ## Synthesis
   EOF
   ```

   全局 wiki 使用同样结构，根目录改为 `~/.claude/wiki/`。

3. 验证：
   ```bash
   test -f wiki/index.md && test -d wiki/sources && test -f wiki/log.md
   ```

4. 返回调用方：
   - 来自 `dev-wiki-search` -> 重新运行查询
   - 来自 `dev-wiki-ingest` -> 继续 ingest 规划 GATE

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | project/global target |
| **Output** | `wiki/` or `~/.claude/wiki/` skeleton |
| **Next** | return to `dev-wiki-search` or `dev-wiki-ingest` |
