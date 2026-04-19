---
name: dev-wiki-search
description: "Use when a dev:* phase (discover/plan) needs to query existing knowledge before starting work, or when the user asks 'what do we already know about X'. Runs grep-based search across project wiki (<project>/wiki/) and global wiki (~/.claude/wiki/), ranks hits by location (index.md > concepts/entities > sources > synthesis), returns a compact brief with relative paths the caller can read. No LLM needed; the caller does interpretation."
---

# dev:wiki-search -- 双层 wiki 快速查询

## 通用规则

1. **始终用中文与用户交流。** 查询宣告、结果汇总使用中文。页面路径/引号内关键词保持英文。
2. **只读。** 不修改任何 wiki 文件、不创建、不重写 index.md。
3. **不调 LLM 解释。** 只负责**找**到候选页面并按相关性排序,**读取与解读**交给 caller 或用户。
4. **不预热空目录。** 若项目 wiki 或全局 wiki 不存在,明确告知"未初始化",不静默跳过。

## When to Use

- `dev-discover` 第 1 步(需求澄清前)—— 已有知识先注入 brainstorm 上下文
- `dev-plan` 并行研究步骤 —— 与 repo-research / learnings 同级并行触发
- 用户主动问"我们以前是不是做过 X"、"有没有相关的踩坑记录"
- `dev-learn` 做 Wiki Ingest 前先查是否已有对应页面,决定 update vs create

## Wiki 双层结构

```
<project>/wiki/                 ~/.claude/wiki/
├── index.md     (入口)         ├── index.md     (跨项目入口)
├── sources/     (源摘要)       ├── sources/
├── entities/    (人/系统/工具) ├── entities/
├── concepts/    (概念)         ├── concepts/
├── synthesis/   (综合答案)     ├── synthesis/
└── log.md       (操作日志)     └── log.md
```

## Workflow

1. **宣告开始**(中文):
   "开始 wiki 查询:关键词 `<keywords>`。扫描项目 wiki + 全局 wiki..."

2. **提取关键词**:
   - 从 caller 传入的 topic 或用户 prompt 抽取 2-5 个检索词
   - 中英混合时同时保留;英文术语保留大小写变体
   - 优先用**名词短语**,避免 stop word

3. **存在性检查**:
   ```bash
   PROJECT_WIKI="$(pwd)/wiki"
   GLOBAL_WIKI="$HOME/.claude/wiki"
   [ -d "$PROJECT_WIKI" ] && echo "PROJECT:OK" || echo "PROJECT:MISSING"
   [ -d "$GLOBAL_WIKI" ] && echo "GLOBAL:OK" || echo "GLOBAL:MISSING"
   ```
   两侧都 MISSING → 直接输出"wiki 未初始化(可跑 `/dev:wiki-init` 创建骨架)",结束。

4. **分层 grep**(按匹配强度从高到低):

   ```bash
   # L1: index.md(入口摘要,一句话匹配)
   grep -liE '<keyword1>|<keyword2>' {$PROJECT_WIKI,$GLOBAL_WIKI}/index.md 2>/dev/null

   # L2: concepts / entities(结构化知识)
   grep -rliE '<keyword1>|<keyword2>' {$PROJECT_WIKI,$GLOBAL_WIKI}/{concepts,entities}/ 2>/dev/null

   # L3: sources(原始源摘要)
   grep -rliE '<keyword1>|<keyword2>' {$PROJECT_WIKI,$GLOBAL_WIKI}/sources/ 2>/dev/null

   # L4: synthesis(综合查询答案)
   grep -rliE '<keyword1>|<keyword2>' {$PROJECT_WIKI,$GLOBAL_WIKI}/synthesis/ 2>/dev/null
   ```

5. **去重 + 排序**:
   - 同一页面在多层被命中 → 归入最高层
   - 按关键词命中数降序;平手按文件路径短的靠前(入口越近越相关)
   - 每层最多展示 5 条,超出折叠

6. **输出 Brief**(控制台,Markdown 格式):

   ```
   Wiki 查询结果:关键词 [<keywords>]
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   项目 wiki(<project>/wiki/)
     L2 concepts/caching-strategy.md        (3 命中)
     L3 sources/2024-redis-postmortem.md    (2 命中)

   全局 wiki(~/.claude/wiki/)
     L1 index.md                            (2 命中 → 跳 entities/redis.md)
     L2 patterns/rails-caching.md           (4 命中)

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   建议 caller 读取优先顺序:
     1. ~/.claude/wiki/patterns/rails-caching.md  (跨项目最佳实践)
     2. <project>/wiki/concepts/caching-strategy.md (本项目决策)
     3. <project>/wiki/sources/2024-redis-postmortem.md (踩坑原文)
   ```

7. **结束**:不自动读取页面内容;caller / 用户决定读哪个。

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | 关键词列表(caller 提供)或用户 prompt 中可抽取的 topic |
| **Output** | 分层排序的候选页面路径清单(中文 Brief) |
| **Side Effects** | 无(纯只读 grep) |
| **Next** | Caller 按推荐顺序读取相关页面,注入 brainstorm / plan 上下文 |

## Iron Laws

- **只读**:绝不改 wiki 文件
- **快速失败**:未初始化时立即告知,不尝试自动创建
- **不替 caller 读文件**:只给路径,不注入内容(避免 context 污染)
- **关键词透明**:输出 Brief 时明确列出实际使用的检索词,便于用户判断是否需要换词重查
