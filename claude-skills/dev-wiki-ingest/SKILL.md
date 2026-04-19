---
name: dev-wiki-ingest
description: "Use when dev-learn writes a new docs/solutions/*.md, after a retro is filed, or when the user says 'add this to the wiki' / 'ingest this source'. Compiles a new or updated knowledge source into the structured wiki (project or global) by creating/updating pages in sources/, entities/, concepts/, synthesis/, updating index.md and log.md. Single ingest may touch 5-15 pages. Always uses the dual-wiki pattern: project wiki for project-specific knowledge, ~/.claude/wiki/ for cross-project generalizable knowledge."
---

# dev:wiki-ingest -- 知识编译到 wiki

## 通用规则

1. **始终用中文与用户交流。** 编译进度、页面清单、GATE 使用中文。路径、标题锚点保持英文。
2. **源不可变。** `docs/solutions/*.md`、retro 报告、外部文章 URL 是**不可变源**;wiki 是它们的**编译产物**。绝不编辑源文件;只在 wiki 里创建或更新摘要/引用。
3. **工作区前置(强制)。** 执行 `git rev-parse --abbrev-ref HEAD`,若在 main/master,STOP 并要求创建 worktree —— 本技能会写 5-15 个 wiki 页面,算批量改动。
4. **GATE 必须展示页面清单。** 写入任何 wiki 文件前,先列出将要 create/update 的完整路径清单 + diff 摘要,等用户确认。
5. **提交由用户触发。** 写完即止,不 `git commit` / `git push`。

## When to Use

- `dev-learn` 的 `ce:compound` 写完 `docs/solutions/*.md` 后自动触发
- retro 报告写入后
- 用户手动:"把这篇文章/paper/postmortem ingest 到 wiki"
- 读完某个外部源(article/doc/URL)准备归档时

**不适用**:日常 commit 信息、一次性讨论、无沉淀价值的会话记录(那是 dev-learn 判断的事,不是本技能)。

## 路由判定:项目 wiki vs 全局 wiki

| 知识类型 | 去哪 |
|---|---|
| 本项目特定架构、踩坑、决策 | `<project>/wiki/` |
| 框架模式、工具通用经验、团队约定 | `~/.claude/wiki/` |
| 两者都适用(通用模式被本项目采用) | **两侧都写**,互相引用 |

模糊时 GATE 询问用户,带推荐标识。

## Wiki 页面类型

```
index.md        一句话目录,每个 entity/concept/source 一行链接 + 一行摘要
sources/        原始源摘要(摘取要点,不复制全文),标注来源 URL/path + ingest 日期
entities/       命名实体(人、团队、系统、库、工具)的累积 profile 页
concepts/       抽象概念/模式/决策(e.g. caching-strategy.md)
synthesis/      综合查询答案:"之前某次 Wiki Query 给出的好答案"被固化成页面
log.md          append-only 操作日志:时间戳 + 操作类型 + 源 + 触动的页面
```

## Workflow

1. **宣告开始**:
   "开始 wiki ingest:源 `<source-path-or-url>`。先判定路由 + 扫描已有相关页面..."

2. **前置检查**:
   - 工作区检查(见通用规则 3)
   - Wiki 存在性:`<project>/wiki/` 或 `~/.claude/wiki/` 至少一侧存在;都不存在时提示"先跑 `/dev:wiki-init`"并结束
   - 调用 `dev:wiki-search` 查"本次源的关键词"是否已有相关页面,拿到命中清单

3. **抽取(LLM)**:
   - 从源中抽取:
     - 主题句(1 句话总结)
     - 实体列表(出现的人/系统/工具/库)
     - 概念列表(引入或引用的抽象概念)
     - 决策列表(做过的选择 + 理由)
     - 反模式 / 踩坑(如果有)
   - 每项附**源页面锚点**(如 `sources/2024-redis-postmortem.md#section-2`),保证可追溯

4. **规划页面改动**:
   按抽取结果生成改动清单:

   | 操作 | 目标页面 | 理由 |
   |---|---|---|
   | CREATE | sources/<slug>.md | 新源摘要 |
   | UPDATE | entities/redis.md | 新增一条"2024 postmortem 中 X 失败" |
   | UPDATE | concepts/caching-strategy.md | 补 trade-off 段 |
   | CREATE | concepts/cache-stampede.md | 本源引入的新概念 |
   | UPDATE | index.md | 登记两个新页面 |
   | APPEND | log.md | 操作日志 |

   **单次 ingest 5-15 页**是设计预期;超过 15 页 → 拆分成两次 ingest,避免大批量难以 review。

5. **GATE**:
   展示完整改动清单(路径 + 每页的 diff 摘要),调用澄清工具:
   `执行全部 (Recommended) / 只执行 sources + index + log / 手动选择 / 取消`

6. **执行写入**(用户确认后):
   - 按清单写文件
   - 每个 update 保留原文件结构,只在相应节点追加/修改;**不重排**已有内容
   - `log.md` 追加格式:
     ```
     ## 2026-04-19 14:32 -- wiki-ingest
     Source: docs/solutions/2026-04-19-redis-cache-stampede.md
     Pages touched (5):
       - CREATE sources/2026-04-19-redis-cache-stampede.md
       - UPDATE entities/redis.md
       - UPDATE concepts/caching-strategy.md
       - CREATE concepts/cache-stampede.md
       - UPDATE index.md
     ```

7. **跨层传播(可选)**:
   若本次 ingest 写入的是项目 wiki,但内容有**跨项目通用价值**(抽象模式、框架经验),GATE 再询问:
   `是否同步 ingest 一份到 ~/.claude/wiki/?(Recommended 对抽象模式)`
   用户同意 → 以相同流程写全局 wiki,两侧 index.md 互加"See also"链接。

8. **宣告结束**:
   "Ingest 完成:项目 wiki 触动 M 页,全局 wiki 触动 N 页。查看 `wiki/log.md` 了解详情。提交留给你。"

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | 源路径(`docs/solutions/*.md` / retro 报告路径 / 外部 URL) + 用户对路由(项目/全局/双写)的偏好(会在 GATE 确认) |
| **Output** | 新建或更新的 5-15 个 wiki 页面 + log.md append |
| **Side Effects** | wiki 目录下的文件写入(不碰源文件,不 commit) |
| **Next** | 用户 review `wiki/log.md`,决定是否提交 |

## Iron Laws

- **源不可变**:绝不编辑 `docs/solutions/*.md`、retro 报告、外部源原文
- **可追溯**:每个 wiki 页面的每条信息必须带源锚点(文件:行 或 URL#section)
- **小批量**:单次 ingest ≤15 页;超过拆分
- **非重排**:update 操作只追加/修改相关段,不动其它内容
- **双写需理由**:跨层传播到全局 wiki 必须 GATE,不默认做
