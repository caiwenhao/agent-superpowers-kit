# AI Coding 研发流程全景图

三套技能库（Superpowers / Compound Engineering / gstack）组合形成 **7 阶段研发流程**。

每个阶段标注了**最佳技能组合**和**核心产出文档**，基于对 80+ 个技能源码的深度分析。

```
┌──────────────────────────────────────────────────────────────────┐
│                     AI Coding 研发全流程                          │
│                                                                  │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐   │
│  │ 发现  │->│ 设计  │->│ 规划  │->│ 实现  │->│ 验证  │->│ 交付  │   │
│  │Phase1│  │Phase2│  │Phase3│  │Phase4│  │Phase5│  │Phase6│   │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘   │
│      ^                                                  │       │
│      │              ┌──────┐                            │       │
│      └──────────────│ 沉淀  │<───────────────────────────┘       │
│                     │Phase7│                                    │
│                     └──────┘                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 发现 -- "做什么"

> 目标：从模糊想法到明确的需求定义
>
> 核心产出：`docs/brainstorms/*-requirements.md`（带 R-ID 的需求文档）

### 最佳组合：按场景路由入口，统一汇聚到 `ce:brainstorm`

```
"不知道做什么"  -> ce:ideate (排名创意) ----+
"值不值得做"    -> office-hours (YC 验证) --+--> ce:brainstorm --> 需求文档
"加个功能"（模糊）-> 直接进入 ---------------+         |
"做这个具体的事"  -> 直接进入 (Lightweight) -+    document-review
                                                  (多人格审查)
```

| 技能 | 角色 | 何时用 |
|---|---|---|
| `ce:ideate` | 创意发散 | 不知道做什么时 |
| `office-hours` | 需求验证 | 有想法但不确定值不值得做 |
| **`ce:brainstorm`** | **需求定义（唯一出口）** | **所有场景最终汇聚于此** |

### 为什么是 `ce:brainstorm` 的需求文档

- **R-ID 追溯**（R1, R2, R3...）-- 贯穿规划、实现、审查全流程的锚点
- **阻塞问题分级** -- Resolve Before Planning / Deferred to Planning，防止技术问题阻塞需求、产品问题泄入规划
- **无实现泄漏** -- 明确排除架构/组件/数据流等 HOW，只定义 WHAT
- **document-review 集成** -- 多人格自动审查文档质量

### 铁律

**需求文档获得用户批准前，禁止任何实现行为。**

---

## Phase 2: 设计 -- "长什么样"

> 目标：确定视觉语言和交互方案
>
> 核心产出：`DESIGN.md`（设计体系）+ `approved.json`（视觉方案选择）

### 最佳组合：一条流水线，不是可替换选项

```
design-consultation --> design-shotgun --> plan-design-review --> design-html
  "建立设计语言"        "探索视觉方案"      "计划里补设计决策"      "设计变代码"
       |                     |                    |                    |
       v                     v                    v                    v
   DESIGN.md           approved.json         修订后的计划        finalized.html
```

| 场景 | 推荐组合 |
|---|---|
| 新项目，无设计体系 | `design-consultation` -> `design-shotgun` |
| 有体系，规划新功能 | `plan-design-review`（在 Phase 3 评审中） |
| 实现功能中 | `frontend-design`（ce:work 中自动启用） |
| 实现后视觉问题 | `design-review`（Phase 5 中叠加） |
| 纯后端需求 | **跳过 Phase 2** |

### 为什么是 `DESIGN.md`

**`DESIGN.md` 是贯穿设计->规划->实现->审查的设计锚点**，地位等同于 Phase 1 的 R-ID：

- `design-shotgun` 用它约束变体生成
- `plan-design-review` 根据它校验设计一致性
- `design-html` 从中提取 token
- `design-review` 根据偏离程度判定严重性
- `frontend-design` 在 ce:work 中自动检测并遵循

---

## Phase 3: 规划 -- "怎么做"

> 目标：从需求文档到可执行的实施计划
>
> 核心产出：`docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`

### 最佳组合：`ce:plan` 创建 + `autoplan`/`plan-eng-review` 评审

```
需求文档 (R1, R2, R3)
    |
    v
ce:plan
    |  并行研究 Agent (repo-research + learnings + best-practices + framework-docs)
    |  Requirements Trace 回链需求文档
    |  Implementation Units (每个 = 一个原子提交)
    |  Test Scenarios (枚举验证点，不预写代码)
    |
    v
autoplan (一键四视角评审)
    |  CEO: 质疑前提、Dream State
    |  Design: 7 维度（条件：有 UI）
    |  Eng: 架构/测试/性能/故障（必需，gate /ship）
    |  DX: 8 维度 DX 评分���（条件：面向开发者）
    |
    v
修订后的计划 + GSTACK REVIEW REPORT
```

| 场景 | 评审深度 |
|---|---|
| 新产品/大型功能 | `autoplan`（全部四种） |
| 普通功能 | `plan-eng-review`（必需）+ `plan-design-review`（有 UI 时） |
| 小修复/重构 | `plan-eng-review`（必需） |
| 开发者工具 | `plan-eng-review` + `plan-devex-review` |

### 为什么是 `ce:plan` 而非 `writing-plans`

**`ce:plan` 输出决策，`writing-plans` 输出代码。** AI Agent 需要方向，不需要抄写。

- **研究子 Agent** -- 并行扫描代码库模式、历史经验、外部最佳实践（`writing-plans` 完全没有）
- **R-ID 追溯** -- 从 Phase 1 需求文档直通 Phase 5 代码审查
- **深化机制** -- 信心不足时自动发现 gap 并加强
- **范围自适应** -- Lightweight (2-4 单元) / Standard (3-6) / Deep (4-8)

### 铁律

**计划解决"决策"而非"代码"。实现者拿到计划后应能直接开始。**

---

## Phase 4: 实现 -- "写代码"

> 目标：按计划执行开发，持续验证
>
> 核心产出：代码 + 增量提交

### 最佳组合：`ce:work` 作为唯一执行入口

```
计划文档
    |
    v
ce:work (自动选策略)
    |
    |-- Trivial (1-2 files)       -> 直接实现
    |-- Small/Medium (< 10 files) -> 内联或串行 Agent
    |-- Large (有依赖的 3+ 单元)   -> 串行 Agent
    |-- Large (有独立的 3+ 单元)   -> 并行 Agent
    |-- 10+ 单元需要协调           -> Swarm (Agent Teams)
    |
    v
每个任务内部：
    实现 -> Test Discovery -> System-Wide Test Check -> 增量提交
    每 2-3 单元: Simplify 通道（跨单元去重）
```

### 为什么是 `ce:work` 而非 `subagent-driven-development` / `executing-plans`

| 决定性优势 | 说明 |
|---|---|
| **策略自适应** | 自动选内联/串行/并行/Swarm，其他只有单一策略 |
| **完美消费 `ce:plan`** | 逐字段读取 Implementation Units / Test Scenarios / Execution Notes / Verification |
| **System-Wide Test Check** | 追溯回调两层、检查孤立状态、校验跨层错误策略 -- 子 Agent 隔离上下文做不到 |
| **Simplify 通道** | 每 2-3 单元去重，防止子 Agent 盲区导致的跨单元重复 |
| **强制 ce:review** | 默认 Tier 2（20+ 人格并行审查），不是新生成的审查 Agent |

### 辅助技能

| 技能 | 何时介入 |
|---|---|
| `test-driven-development` | 计划标注 `Execution note: test-first` 时 |
| `systematic-debugging` / `investigate` | 遇到 bug 时（四阶段根因分析） |
| `dispatching-parallel-agents` | 多个独立失败需要并行诊断 |
| `frontend-design` | 涉及前端 UI 时自动启用 |
| `reproduce-bug` | 从 GitHub Issue 复现 bug |

### 铁律

- **无失败测试，不写生产代码**
- **无根因分析，不尝试修复**
- **3 次修复失败，停下质疑架构**

---

## Phase 5: 验证 -- "质量关"

> 目标：多层级审查确保代码质量
>
> 核心产出：审查裁决（PASS / NEEDS_WORK）+ safe_auto 修复 + 残余 todo

### 最佳组合：`ce:review`（必须）+ 按场景叠加

```
代码变更 --> ce:review mode:autofix plan:<path>
                |
                |-- 6 始终启用: correctness, testing, maintainability,
                |               project-standards, agent-native, learnings
                |
                |-- 条件启用: security, performance, api-contract,
                |             data-migrations, reliability, adversarial,
                |             kieran-rails, kieran-python, kieran-typescript...
                |
                v
          置信度过滤 (>=0.60, P0 >=0.50)
                |
                v
          safe_auto 自动修复 --> 残余写入 todo --> todo-resolve
```

| 场景 | 核心 | 叠加 |
|---|---|---|
| 普通功能 | `ce:review` | -- |
| 有 UI 的功能 | `ce:review` | + `test-browser`（受影响路由） |
| 大型 UI 功能 | `ce:review` | + `gstack/qa`（全站）+ `design-review` |
| 涉及安全/支付 | `ce:review` | + `gstack/cso`（安全审计） |
| 涉及 LLM/AI | `ce:review` | + `gstack/review`（LLM 信任边界） |
| 性能敏感 | `ce:review` | + `gstack/benchmark` |

### 为什么 `ce:review` 是核心

- **20+ 人格自动组队** -- config 改动 = 6 审查者，Rails 支付功能 = 12+
- **R-ID 需求追溯** -- 从计划文件读 R1/R2/R3，验证每条需求是否被代码覆盖
- **四种模式** -- interactive / autofix / report-only / headless
- **safe_auto 修复** -- 确定性修复自动应用，残余写入 todo 系统

### 铁律

- **证据先于断言** -- 没跑命令不能说"通过了"
- **验证先于采纳** -- 审查反馈先验证再实现，技术正确性优先于社交礼貌

---

## Phase 6: 交付 -- "上线"

> 目标：从代码到生产环境
>
> 核心产出：PR + 部署

### 最佳组合：两条路径，共享终点

```
路径 A (CE, 轻量):
  git-commit-push-pr --> land-and-deploy
  (适合已走 ce:review 的日常交付)

路径 B (gstack, 完整):
  ship --> document-release --> land-and-deploy
  (适合需要版本号/CHANGELOG 的重要发布)
```

| 场景 | 推荐路径 |
|---|---|
| 日常功能（已走 CE 流程） | 路径 A: `git-commit-push-pr` -> `land-and-deploy` |
| 重要发布（需要版本号） | 路径 B: `ship` -> `document-release` -> `land-and-deploy` |
| 有 UI 变更 | 任一路径 + `feature-video`（PR 嵌入录屏） |
| PR 有评审反馈 | `resolve-pr-feedback` -> 继续交付 |
| 快速修复 | 路径 A（最短路径） |

### `gstack/ship` 独有能力（路径 B）

版本号管理、CHANGELOG 自动生成、测试覆盖审计（60%/80% 门）、计划完成度审计、可二分提交、Codex 对抗审查

### `land-and-deploy` 关键设计

- 合并前就绪报告（最后人工关卡）
- 金丝雀验证（按 diff 范围分级：docs 跳过、config smoke、backend 控制台、frontend 全量）
- 每个失败点提供回滚选项

---

## Phase 7: 沉淀 -- "学到什么"

> 目标：将经验转化为可复用的组织知识
>
> 核心产出：`docs/solutions/*.md` + `learnings.jsonl`

### 最佳组合：双层知识系统 + 周期回顾

```
底层（自动）:  gstack/learn      每个技能完成时自动写 1 条洞察
上层（主动）:  ce:compound       重要问题手动触发，完整文档
时间线:        gstack/retro      每周分析提交/质量/团队趋势
元层:          writing-skills    跨项目方法论编码为 SKILL.md
维护:          ce:compound-refresh  定期清理过期/矛盾文档
```

| 触发时机 | 使用技能 | 输出 |
|---|---|---|
| 刚修完 bug / 解决问题 | `ce:compound` | `docs/solutions/<category>/<slug>.md` |
| gstack 技能运行结束 | `gstack/learn`（自动） | `learnings.jsonl` 新条目 |
| 周末回顾 | `gstack/retro` | 回顾报告 + 趋势快照 |
| 发现跨项目通用做法 | `writing-skills` | `~/.claude/skills/<name>/SKILL.md` |
| 知识库可能过期 | `ce:compound-refresh` | 更新/合并/删除过期文档 |

### 知识闭环

```
Phase 4 (ce:work) -- 解决问题 --> Phase 7 (ce:compound) -- 沉淀 --> docs/solutions/
                                                                        |
Phase 3 (ce:plan) <-- learnings-researcher 搜索 -------------------------+
Phase 5 (ce:review) <-- learnings-researcher 始终启用 -------------------+
所有 gstack 技能 <-- preamble 自动搜索 learnings.jsonl ------------------+
```

**知识不只是被记录 -- 它被自动注入到未来的规划和审查中。这就是"compound"（复利）的含义。**

---

## 全自动编排器

两个"一键启动"技能串联 Phase 3-6：

### `lfg` -- 串行模式

```
ce:plan -> GATE -> ce:work -> GATE -> ce:review(autofix) -> todo-resolve -> test-browser -> feature-video -> DONE
```

### `slfg` -- 并行模式

```
ce:plan -> ce:work(swarm) -> +-- ce:review(report-only) --+ -> ce:review(autofix) -> todo-resolve -> DONE
                              +-- test-browser -------------+
                                  (并行读，串行写)
```

---

## 五条铁律（贯穿全流程）

| # | 铁律 | 守护技能 |
|---|---|---|
| 1 | **设计先于实现** -- 需求文档批准前不碰代码 | brainstorming, ce:brainstorm |
| 2 | **测试先于代码** -- 无失败测试不写生产代码 | test-driven-development |
| 3 | **根因先于修复** -- 不理解为什么坏就不能修 | systematic-debugging, investigate |
| 4 | **证据先于断言** -- 没跑命令不能说"通过了" | verification-before-completion |
| 5 | **验证先于采纳** -- 审查反馈先验证再实现 | receiving-code-review |

---

## 文档追溯链（贯穿全流程）

```
Phase 1            Phase 2            Phase 3            Phase 4         Phase 5         Phase 6
需求文档            DESIGN.md          实施计划            ce:work         ce:review       交付
R1,R2,R3 -------> Token/色值 -------> Req Trace -------> 实现代码 -----> R-ID 验证 ----> PR
                                       Impl Units         增量提交        safe_auto       部署
                                       Test Scenarios                     修复

每个阶段的产出是下一阶段的输入。R-ID 从 Phase 1 贯穿到 Phase 5。
```

---

## 三库定位总结

| 库 | 定位 | 核心价值 |
|---|---|---|
| **Superpowers** | 开发**方法论** | 定义"怎样才算做对了" -- TDD、根因调试、证据验证等铁律 |
| **Compound Engineering** | 开发**流水线** | 定义"数据怎么流" -- brainstorm->plan->work->review 的文档驱动管道 |
| **gstack** | 开发**工具箱** | 定义"用什么工具" -- 设计、评审、部署、安全审计 |

三者组合 = **有纪律的方法论** + **可追溯的文档管道** + **全栈工具支撑**

---

## 详细分析文档索引

| Phase | 分析文档 |
|---|---|
| Phase 1: 发现 | [phase1-discovery-analysis.md](phase1-discovery-analysis.md) |
| Phase 2: 设计 | [phase2-design-analysis.md](phase2-design-analysis.md) |
| Phase 3: 规划 | [phase3-planning-analysis.md](phase3-planning-analysis.md) |
| Phase 4: 实现 | [phase4-implementation-analysis.md](phase4-implementation-analysis.md) |
| Phase 5: 验证 | [phase5-verification-analysis.md](phase5-verification-analysis.md) |
| Phase 6: 交付 | [phase6-delivery-analysis.md](phase6-delivery-analysis.md) |
| Phase 7: 沉淀 | [phase7-knowledge-analysis.md](phase7-knowledge-analysis.md) |
