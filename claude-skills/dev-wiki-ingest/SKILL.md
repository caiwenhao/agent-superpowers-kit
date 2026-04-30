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

- `dev-learn` 的 `ce-compound` 写完 `docs/solutions/*.md` 后自动触发
- retro 报告写入后
- 用户手动:"把这篇文章/paper/postmortem ingest 到 wiki"
- 读完某个外部源(article/doc/URL)准备归档时
- **批量场景**:仓库已有大量历史文档(`docs/`、`design/`、`postmortems/`),首次接入 wiki 时一次性迁移 → 走 **批量模式**(见下)

**不适用**:日常 commit 信息、一次性讨论、无沉淀价值的会话记录(那是 dev-learn 判断的事,不是本技能)。

## 批量模式(首次迁移历史文档专用)

触发:用户传入**目录或 glob**(如 `docs/`、`design/**/*.md`)而非单文件路径。

### 与单源模式的差异

| 维度 | 单源 | 批量 |
|---|---|---|
| 输入 | 一个文件/URL | 目录/glob,展开成 N 个源 |
| GATE 频率 | 1 次(整体清单) | **1 次必需**:首轮规划清单；后续批次默认只报进度,有 blocker/试点模式时才再 GATE |
| 一次写入页数 | 5-15 | **每个源仍 5-15**,但跨源累积可达数百页 |
| 进度跟踪 | 不需要 | **需要** —— 必须维护 `wiki/_migration.md` checklist 文件 |
| 可中断 | N/A | **必须**支持 —— 每处理 K 个源后 GATE,用户可暂停 |
| 跨层传播询问 | 每源问 | **整批结束后统一问** —— 避免被打断 N 次 |

### 批量 Workflow

1. **展开输入**:把目录/glob 解析成具体文件列表,按文件大小(小的先,快速验证流程)或字母序排列
2. **首轮规划**:
   - 对每个源**只**抽取主题句和关键实体/概念(不展开成完整页面)
   - 输出 `wiki/_migration.md`:
     ```markdown
     # Wiki Migration Plan
     总源数: 47
     已完成: 0 / 47

     - [ ] docs/architecture.md → 主题"系统架构总览";命中实体: api-server, postgres, redis;命中概念: event-sourcing, cqrs
     - [ ] docs/postmortems/2024-redis.md → 主题"2024 Redis 缓存击穿";命中实体: redis, cache-stampede
     - [ ] ...
     ```
   - GATE:展示 `_migration.md`,询问 `按计划全量迁移 (Recommended) / 只跑前 5 个试点 / 调整顺序 / 只迁某个子目录 / 取消`
   - 若用户选择 **按计划全量迁移**，即视为对后续批处理的**整体授权**；不要在每批结束后重复询问“继续下一批”
3. **批处理**:
   - 默认每批 5 个源,每批结束后:
     - 更新 `_migration.md` 的 checkbox
     - 显示"已完成 5/47,触动 wiki 页面 23 个"
     - 若当前模式是**全量迁移**且无 blocker / 无大规模冲突 / 无用户新指令: **自动继续下一批**
     - 仅在以下情况 GATE:`继续下一批 (Recommended) / 暂停 / 调整批量大小 / 跳过下一个源`
       - 当前模式是"只跑前 5 个试点"
       - 出现跨源冲突激增、目标页面爆量、或抽取质量明显异常
       - 用户中途要求暂停 review 或调整批量策略
   - 用户暂停后,下次再调 `dev:wiki-ingest` 传同样目录,会**读 `_migration.md` 续跑**未完成项
4. **去重处理**:跨源命中同一实体/概念页 → **同一页面累积**,不重复 create;追加段落标注源
5. **冲突解决**:同一概念在两个源里描述矛盾 → 在 concept 页里**两段并列保留**,前缀标源,由用户事后调和(不静默选一个)
6. **整批结束**:
   - 删除/归档 `_migration.md` 到 `wiki/log.md`
   - 统一 GATE 询问跨层传播:`将这批新增 wiki 中标记为'通用模式'的页面同步到 ~/.claude/wiki/?`

### 批量模式 Iron Laws(单源规则之上额外的)

- **可恢复**:中途任何时刻都能 ctrl-c 退出,`_migration.md` 是真实进度;再跑续传不重做已完成项
- **小步快跑**:默认每批 5 个源,不一口气吞所有;允许用户随时暂停 review
- **授权收敛**:用户一旦选择"按计划全量迁移",后续批次默认自动推进;不要把同一授权拆成每批一次确认
- **不删源**:迁移过程中绝不动 `docs/`、`design/` 等源目录的原文件;wiki 是**编译产物**,源永远是真理
- **`_migration.md` 短命**:整批完成后从 wiki 根目录删除(只在 `log.md` 里留摘要);它是临时进度文件,不是 wiki 一等公民

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
   - **孤儿 `_migration.md` 扫描**: 检查 `<project>/wiki/_migration.md` 和 `~/.claude/wiki/_migration.md` 是否存在。若存在:
     ```bash
     for wiki in wiki ~/.claude/wiki; do
       mig="$wiki/_migration.md"
       [ -f "$mig" ] || continue
       age_sec=$(( $(date +%s) - $(stat -c %Y "$mig" 2>/dev/null || stat -f %m "$mig") ))
       age_hr=$(( age_sec / 3600 ))
       echo "发现 $mig (更新于 ${age_hr}h 前)"
     done
     ```
     - 若 mtime 距今 < 1 小时 **且** 当前调用与原批量输入匹配 → 视为续跑,读 `_migration.md` 恢复进度
     - 若 mtime ≥ 1 小时 → 视为孤儿,GATE 询问 `清理后重新开始 / 强制续跑 / 取消`；孤儿不得默认处理
     - 若本次是单源模式,只是扫描到孤儿 → 宣告存在但不清理,提示用户显式启动批量模式才处理
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
