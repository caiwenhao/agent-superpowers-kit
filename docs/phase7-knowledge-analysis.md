# Phase 7: 沉淀 — 最佳技能组合分析

## Phase 7 的关键洞察：四种不同粒度的知识沉淀

Phase 7 的技能不是在做同一件事。它们在**不同粒度、不同时间尺度**上沉淀知识：

```
粒度从细到粗:

  gstack/learn           单条洞察 (key/insight JSON 元组)
       |                    "密码哈希在 Rails 7.2 中用 argon2 更好"
       |
  ce:compound            单个问题的完整文档
       |                    Problem -> Root Cause -> Solution -> Prevention
       |
  gstack/retro           一周/一个迭代的回顾
       |                    提交分析 + 质量趋势 + 团队贡献 + 模式发现
       |
  writing-skills         可复用的方法论
                            TDD 写流程文档，跨项目跨会话
```

---

## 技能对比

| 维度 | `ce:compound` (CE) | `gstack/learn` (gstack) | `gstack/retro` (gstack) | `writing-skills` (SP) | `ce:onboarding` (CE) |
|---|---|---|---|---|---|
| **捕获什么** | 单个已解决问题的完整文档 | 短洞察（key + insight） | 一段时间的提交/质量/团队分析 | 可复用的 Agent 行为文档 | 代码库入门指南 |
| **触发时机** | 刚修完 bug / 刚解决问题 | 每个 gstack 技能自动写入 | 周末 / 迭代结束 | 发现可��用技术时 | 任何时候 |
| **存储格式** | `.md` + YAML frontmatter | JSONL（追加日志） | JSON 快照 | `SKILL.md` | `ONBOARDING.md` |
| **存储位置** | `docs/solutions/<category>/` | `~/.gstack/projects/<slug>/learnings.jsonl` | `.context/retros/` | `~/.claude/skills/` | 仓库根目录 |
| **作用域** | 单项目（在仓库内） | 单项目（可选跨项目） | 单项目或全局 | **跨项目跨会话** | 单项目 |
| **自动注入** | 需要 AGENTS.md 指引 Agent 搜索 | **每个 gstack 技能的 preamble 自动搜索** | 无自动注入 | 通过 skill routing 自动加载 | 手动阅读 |
| **搜索方式** | YAML frontmatter 字段搜索 | `gstack-learnings-search --query` 模糊搜索 | 无直接搜索 | 按 skill 名称路由 | 无 |
| **维护机制** | `ce:compound-refresh`（定期清理过期文档） | `/learn prune`（检查引用文件存在性） | 趋势对比（vs Last Retro） | TDD 重构循环 | 每次重新生成 |

---

## 核心洞察：`ce:compound` 和 `gstack/learn` 是互补的双层系统

```
gstack/learn (底层：自动积累)
  |
  |  每个 gstack 技能完成时自动写入：
  |  {"skill":"investigate","type":"operational","key":"rails-7-argon2",
  |   "insight":"Rails 7.2 默认 bcrypt，但 argon2 在内存硬化上更强",
  |   "confidence":8,"source":"observed","files":["config/initializers/devise.rb"]}
  |
  |  特点：
  |  - 自动、被动、低摩擦
  |  - 短条目（几句话）
  |  - 每个 gstack 技能 preamble 自动搜索并注入
  |  - 跨会话持久化
  |
  v
ce:compound (上层：主动沉淀)
  |
  |  解决重要问题后手动触发：
  |  并行子 Agent (Context Analyzer + Solution Extractor + Related Docs Finder)
  |  -> 完整文档：Problem -> Root Cause -> Solution -> Prevention
  |  -> YAML frontmatter (category, problem_type, tags, module...)
  |
  |  特点：
  |  - 主动、有意识、高质量
  |  - 完整叙事（一页文档）
  |  - 被 ce:plan 的 learnings-researcher 子 Agent 搜索
  |  - 有重叠检测和去重机制
  |
  v
ce:plan / ce:review (下游消费)
  |
  |  ce:plan Phase 1.1: learnings-researcher 搜索 docs/solutions/
  |  ce:review: learnings-researcher 始终启用，搜索相关历史问题
  |  gstack 所有技能: preamble 搜索 learnings.jsonl
```

**`gstack/learn` 是被动积累（每次都写一点），`ce:compound` 是主动沉淀（重要问题写完整）。两者都被下游技能自动消费。**

---

## `ce:compound` 的独特价值

### 1. 并行子 Agent 研究

```
ce:compound Phase 1 (并行):
  Context Analyzer    -> 分类 bug/knowledge，提取 YAML frontmatter
  Solution Extractor  -> 根据 track 输出不同结构
                          Bug: Problem -> Symptoms -> What Didn't Work -> Solution -> Why -> Prevention
                          Knowledge: Context -> Guidance -> Why -> When to Apply -> Examples
  Related Docs Finder -> 搜索 docs/solutions/ 评估重叠度 (High/Moderate/Low)
```

### 2. 重叠检测与去重

```
Related Docs Finder 评估五个维度的重叠：
  problem statement / root cause / solution approach / referenced files / prevention rules

  High (4-5 维度匹配)   -> 更新已有文档，不创建新的
  Moderate (2-3 维度)    -> 创建新的，标记待整合
  Low (0-1 维度)         -> 创建新的
```

**防止知识库膨胀 — 相同问题不会产生多份文档。**

### 3. 选择性刷新触发

```
ce:compound Phase 2.5:
  新文档是否与旧文档矛盾？
    是 -> 触发 ce:compound-refresh（定向刷新）
    否 -> 不刷新
```

### 4. 可发现性检查

```
ce:compound Discoverability Check:
  AGENTS.md / CLAUDE.md 是否提到 docs/solutions/?
    否 -> 建议添加指引，确保未来 Agent 能找到知识库
    是 -> 跳过
```

---

## `gstack/retro` 的独特价值

**不同于 ce:compound 的"单点"视角，retro 提供"时间线"视角：**

```
gstack/retro 分析窗口内的：
  - 提交频率和分布
  - 代码行数变化（新增/删除）
  - 测试比例
  - 文件热点（最频繁修改的文件）
  - gstack 技能使用统计
  - 会话数和时长
  - AI 辅助提交百分比
  - 工作模式连续性（streaks）
  - 团队贡献分解（per-contributor praise + growth areas）
  - vs Last Retro 趋势对比
```

**这是唯一能回答"我们这周效率怎样？质量趋势如何？谁贡献了什么？"的技能。**

---

## `writing-skills` 的独特价值

**ce:compound 沉淀的是"项目知识"（这个项目的这个问题怎么解决）。writing-skills 沉淀的是"方法论"（任何项目都适用的做事方式）。**

```
writing-skills 的 TDD 循环：
  RED:    运行压力场景（无 skill）-> 记录 Agent 的具体偏离行为
  GREEN:  写最小 skill 修复那些偏离 -> 同样场景验证 Agent 合规
  REFACTOR: 发现新的偏离/漏洞 -> 补上 -> 再验证

  输出: SKILL.md（永久改变所有未来 Agent 会话的行为）
```

**这是唯一跨项目、跨会话的知识沉淀。一个 skill 写好后，所有未来项目都受益。**

---

## 最佳组合

### 每次解决问题后

```
问题解决
    |
    v
ce:compound (主动沉淀)
    |  并行子 Agent -> 完整文档 -> 重叠检测 -> 选择性刷新
    |  输出: docs/solutions/<category>/<slug>.md
    |
    +-- gstack/learn (被动积累，自动发生)
    |     由其他 gstack 技能自动写入 learnings.jsonl
    |
    v
下一次 ce:plan / ce:review 自动搜索并引用
```

### 每周/迭代结束

```
gstack/retro
    |  分析提交/质量/团队趋势
    |  输出: 回顾报告 + 趋势快照
    |
    +-- 发现可复用模式？
          |
          v
        writing-skills (TDD 写 SKILL.md)
```

### 定期维护

```
ce:compound-refresh (按需触发)
    |  搜索 docs/solutions/ 中过期/矛盾的文档
    |  分类: Keep / Update / Consolidate / Replace / Delete
    |
    +-- gstack/learn prune (按需触发)
          搜索 learnings.jsonl 中引用已删除文件的条目
```

### 新人加入

```
ce:onboarding
    |  爬取仓库 -> 生成 ONBOARDING.md
    |  6 部分: What Is This / How Used / How Organized /
    |          Key Concepts / Primary Flows / Developer Guide
```

---

## 按场景选择

| 场景 | 使用技能 | 输出 |
|---|---|---|
| 刚修完一个 bug | `ce:compound` | `docs/solutions/<category>/<slug>.md` |
| 学到了一个最佳实践 | `ce:compound` (knowledge track) | `docs/solutions/<category>/<slug>.md` |
| gstack 技能运行结束 | `gstack/learn`（自动） | learnings.jsonl 新条目 |
| 周五回顾 | `gstack/retro` | 回顾报告 + 趋势快照 |
| 发现跨项目通用的做法 | `writing-skills` | `~/.claude/skills/<name>/SKILL.md` |
| docs/solutions/ 可能过期 | `ce:compound-refresh` | 更新/合并/删除过期文档 |
| 新人入职 | `ce:onboarding` | `ONBOARDING.md` |

---

## 知识沉淀的闭环

```
Phase 4 (ce:work) ──解决问题──> Phase 7 (ce:compound) ──沉淀知识──> docs/solutions/
                                                                        |
Phase 3 (ce:plan) <──learnings-researcher 搜索──────────────────────────+
Phase 5 (ce:review) <──learnings-researcher 始终启用搜索────────────────+
所有 gstack 技能 <──preamble 自动搜索 learnings.jsonl───��────────────────+
                                                                        |
                          ce:compound-refresh <──定期清理过期─────────────+
```

**知识不只是被记录 — 它被自动注入到未来的规划和审查中。这就是"compound"（复利）的含义。**

---

## 一句话结论

**Phase 7 = `ce:compound`（主动沉淀，完整文档）+ `gstack/learn`（被动积累，自动注入）+ `gstack/retro`（周期回顾，趋势追踪）。三者构成双层知识系统：learn 是底层自动积累（每个技能都写），compound 是上层主动沉淀（重要问题写完整），retro 提供时间线视角。所有沉淀的知识通过 learnings-researcher 和 preamble 搜索自动注入到未来的 ce:plan 和 ce:review 中。`writing-skills` 是元层 — 将跨项目通用的方法论编码为永久的 Agent 行为文档。**
