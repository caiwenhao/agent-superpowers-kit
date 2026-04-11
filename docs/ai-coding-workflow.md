# AI Coding 研发流程全景图

四套技能库（Agent Skills / Superpowers / Compound Engineering / gstack）+ `dev:` 编排层，组合形成 **7 阶段研发流程**。

每个阶段标注了**智能路由逻辑**、**最佳技能组合**和**核心产出文档**，基于对 120+ 个技能源码的深度分析。

```
┌──────────────────────────────────────────────────────────────────────┐
│                      AI Coding 研发全流程                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              dev:flow -- 智能编排器（单一入口）                  │    │
│  │  自动检测当前阶段，驱动流水线前进，GATE 暂停等待用户确认          │    │
│  └──────────────────────────────────────────────────────────────┘    │
│      |                                                               │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │ 发现  │->│ 设计  │->│ 规划  │->│ 实现  │->│ 验证  │->│ 交付  │       │
│  │Phase1│  │Phase2│  │Phase3│  │Phase4│  │Phase5│  │Phase6│       │
│  │dev:  │  │dev:  │  │dev:  │  │dev:  │  │dev:  │  │dev:  │       │
│  │disco-│  │design│  │plan  │  │code  │  │verify│  │ship  │       │
│  │ver   │  │      │  │      │  │      │  │      │  │      │       │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘       │
│      ^                                                  │           │
│      │              ┌──────┐                            │           │
│      └──────────────│ 沉淀  │<───────────────────────────┘           │
│                     │Phase7│                                        │
│                     │dev:  │                                        │
│                     │learn │                                        │
│                     └──────┘                                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## dev:flow -- 智能编排器

> **用户不需要手动选择技能组合。** `dev:flow` 是唯一入口，自动检测当前状态并路由到正确阶段。

### 场景检测（按优先级）

| 信号 | 检测方式 | 路由结果 |
|---|---|---|
| Signal 0: 是否在工作区 | `git worktree list` | 不在 -> 先创建 worktree |
| Signal 1: 有无未完成工作 | plan status + git status + PR | 恢复到中断的阶段 |
| Signal 2: 用户输入了什么 | 意图分类 | 路由到匹配阶段 |
| Signal 3: 存在哪些产物 | 扫描 docs/ + DESIGN.md + .context/ | 跳到最近的未完成阶段 |

### GATE 机制

每个阶段结束时，`dev:flow` **暂停并报告状态**，用户可以：
- **继续** -- 进入下一阶段
- **跳过** -- 跳过当前阶段（如后端无需设计）
- **暂停** -- 保存进度，稍后用 `/dev:flow` 恢复
- **回退** -- 回到更早的阶段修改

### 阶段跳过规则

| 条件 | 跳过 |
|---|---|
| 纯后端，需求无 UI | Phase 2 (design) |
| 微小修复（1-2 文件） | Phase 1, 2, 3 |
| 紧急热修复 | Phase 1, 2, 3 -> 直达 Phase 4 |
| 需求文档已存在且已批准 | Phase 1 |
| DESIGN.md 已存在且无新 UI 模式 | Phase 2 |
| 计划已存在且已审查 | Phase 3 |
| 仅文档变更 | Phase 1, 2, 3 -> Phase 4 内联 |
| 依赖升级 | Phase 2 |

### 恢复智能

再次调用 `/dev:flow` 时，自动扫描产物（plan status、git branch、PR state），宣告恢复位置并继续。

---

## Phase 1: 发现 -- "做什么"

> 目标：从模糊想法到明确的需求定义
>
> 路由器：`dev:discover`
>
> 核心产出：`docs/brainstorms/*-requirements.md`（带 R-ID 的需求文档）

### 智能路由：按意图清晰度分流

```
"不知道做什么"     -> Route A: ce:ideate (排名创意) -> ce:brainstorm
"值不值得做"       -> Route B: office-hours (YC 验证) -> ce:brainstorm
"加个功能"（模糊） -> Route C: ce:brainstorm (Standard/Deep)
"做这个具体的事"   -> Route D: ce:brainstorm (Lightweight)
                                        |
                                  document-review
                                  (多人格多轮审查循环)
```

`dev:discover` 自动检测用户输入的意图清晰度（无方向 / 有方向但不确定价值 / 多面向 / 清晰小范围），路由到正确的入口技能。**所有路径最终汇聚到 `ce:brainstorm`。**

| 技能 | 角色 | 何时触发 |
|---|---|---|
| `ce:ideate` | 创意发散 | 无方向时，生成 20-30 候选，筛选到 Top 5-7 |
| `office-hours` | 需求验证 | 有想法但不确定值不值得做 |
| **`ce:brainstorm`** | **需求定义（唯一出口）** | **所有场景最终汇聚于此** |
| `document-review` | 多人格审查 | 内嵌在 brainstorm 中，多轮循环直到零 P0/P1 |

### 为什么是 `ce:brainstorm` 的需求文档

- **R-ID 追溯**（R1, R2, R3...）-- 贯穿规划、实现、审查全流程的锚点
- **阻塞问题分级** -- Resolve Before Planning / Deferred to Planning
- **无实现泄漏** -- 只定义 WHAT，不泄漏 HOW
- **document-review 多轮循环** -- coherence / feasibility / product-lens / design-lens / security-lens / scope-guardian 并行审查

### 自动检测下一阶段

需求批准后，`dev:discover` 扫描需求内容：
- 涉及 UI (views, pages, components) -> **Phase 2 (design)**
- 纯后端 / API / CLI -> **Phase 3 (plan)**

### 铁律

**需求文档获得用户批准前，禁止任何实现行为。**

---

## Phase 2: 设计 -- "长什么样"

> 目标：确定视觉语言和交互方案
>
> 路由器：`dev:design`
>
> 核心产出：`DESIGN.md`（设计体系）+ `approved.json`（视觉方案选择）

### 智能路由：按设计成熟度分流

```
需求文档 (from Phase 1)
  |
  +-- 无 DESIGN.md --------> Route A: design-consultation -> design-shotgun
  |   (新项目无设计体系)        创建设计体系，再探索视觉方案
  |
  +-- 有 DESIGN.md, -------> Route B: design-shotgun
  |   无 approved.json        在现有体系内探索视觉方案
  |   (体系存在，无视觉方向)
  |
  +-- 有 DESIGN.md, -------> Route C: plan-design-review (推迟到 Phase 3)
  |   有 approved.json,       计划需要设计维度审查
  |   计划缺设计决策
  |
  +-- 全部就绪 ------------> 跳过 Phase 2 -> dev:plan
```

`dev:design` 自动检测 `DESIGN.md` 是否存在、`approved.json` 是否已选定、前端代码库的设计信号数量，路由到正确的设计流水线阶段。

| 场景 | 推荐组合 |
|---|---|
| 新项目，无设计体系 | `design-consultation` -> `design-shotgun` |
| 有体系，新功能需视觉方向 | `design-shotgun`（受 DESIGN.md 约束） |
| 有视觉方向，规划中补设计审查 | `plan-design-review`（在 Phase 3 中） |
| 实现中 | `frontend-design`（ce:work 自动启用） |
| 实现后视觉问题 | `design-review`（Phase 5 叠加） |
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
> 路由器：`dev:plan`
>
> 核心产出：`docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`

### 智能路由：`ce:plan` 创建 + 按规模自动选评审深度

```
需求文档 (R1, R2, R3)
    |
    v
ce:plan (唯一创建器)
    |  并行研究 Agent (repo-research + learnings + best-practices + framework-docs)
    |  Requirements Trace 回链需求文档
    |  Implementation Units (每个 = 一个原子提交)
    |  Test Scenarios (枚举验证点，不预写代码)
    |
    v
document-review (Layer 1, 多轮循环)
    |  coherence / feasibility / scope-guardian
    |
    v
dev:plan 检测 Implementation Unit 数量，自动选审深度 (Layer 2)
    |
    +-- 10+ 单元 (大型) ------> autoplan (CEO + Design + Eng + DX, 串行)
    +-- 3-9 单元 (标准) ------> plan-eng-review (必需) + plan-design-review (有 UI 时)
    +-- 1-2 单元 (小型) ------> plan-eng-review only
    +-- 涉及 API/CLI/SDK -----> + plan-devex-review (叠加)
    |
    v
修订后的计划 + GSTACK REVIEW REPORT
```

### 为什么是 `ce:plan` 而非 `writing-plans`

**`ce:plan` 输出决策，`writing-plans` 输出代码。** AI Agent 需要方向，不需要抄写。

- **研究子 Agent** -- 并行扫描代码库模式、历史经验、外部最佳实践
- **R-ID 追溯** -- 从 Phase 1 需求文档直通 Phase 5 代码审查
- **深化机制** -- 信心不足时自动发现 gap 并加强
- **范围自适应** -- Lightweight (2-4 单元) / Standard (3-6) / Deep (4-8)

### 铁律

**计划解决"决策"而非"代码"。实现者拿到计划后应能直接开始。**

---

## Phase 4: 实现 -- "写代码"

> 目标：按计划执行开发，持续验证
>
> 路由器：`dev:code`
>
> 核心产出：代码 + 增量提交

### 智能路由：`ce:work` 自动选执行策略

```
计划文档
    |
    v
ce:work (自动检测策略)
    |
    +-- 1-2 files, 无行为变更    -> 直接内联实现
    +-- < 10 files, 清晰范围     -> 串行任务列表
    +-- 3+ 单元有顺序依赖        -> 串行 Agent
    +-- 3+ 单元互相独立          -> 并行 Agent
    +-- 10+ 单元需要协调         -> Swarm (Agent Teams)
    |
    v
每个任务内部：
    实现 -> Test Discovery -> System-Wide Test Check -> 增量提交
    每 2-3 单元: Simplify 通道（跨单元去重）
    |
    v
内嵌 ce:review mode:autofix (快速 safe_auto 修复, 最多 2 轮)
```

### 自动触发的辅助技能

`dev:code` 不需要手动选择辅助技能，**由 plan 内容和运行时信号自动触发**：

| 检测到的信号 | 自动触发技能 |
|---|---|
| Implementation Unit 标记 `test-first` | `test-driven-development` (RED-GREEN-REFACTOR) |
| Implementation Unit 标记 `characterization-first` | 先写特征测试再修改 |
| Implementation Unit 标记 `external-delegate` | Codex 委托模式 (`ce:work-beta`) |
| 运行时遇到 bug | `systematic-debugging` / `investigate` |
| 多个独立测试失败 | `dispatching-parallel-agents` |
| 触碰 `views/`, `components/`, `*.tsx`, `*.css` | `frontend-design`（自动检测 DESIGN.md） |
| Plan 引用 GitHub Issue | `reproduce-bug` |

### 铁律

- **无失败测试，不写生产代码**
- **无根因分析，不尝试修复**
- **3 次修复失败，停下质疑架构**

---

## Phase 5: 验证 -- "质量关"

> 目标：多层级审查确保代码质量
>
> 路由器：`dev:verify`
>
> 核心产出：审查裁决（PASS / NEEDS_WORK）+ safe_auto 修复 + 残余 todo

### 智能路由：`ce:review` 自动组队 + `dev:verify` 自动叠加

```
代码变更
    |
    v
ce:review interactive plan:<path> (核心, 多轮循环最多 3 轮)
    |
    |-- 6 始终启用: correctness, testing, maintainability,
    |               project-standards, agent-native, learnings
    |
    |-- 按 diff 内容自动启用:
    |   auth/login/session    -> security-reviewer
    |   DB/cache/async        -> performance-reviewer
    |   routes/serializer     -> api-contract-reviewer
    |   db/migrate/schema     -> data-migrations-reviewer + schema-drift-detector
    |   rescue/retry/timeout  -> reliability-reviewer
    |   diff >= 50 行或 auth  -> adversarial-reviewer
    |   Rails controllers     -> kieran-rails + dhh-rails
    |   *.py                  -> kieran-python
    |   *.ts/*.tsx            -> kieran-typescript
    |   Stimulus/Turbo        -> julik-frontend-races
    |
    v
置信度过滤 (>=0.60, P0 >=0.50)
    |
    v
safe_auto 自动修复 -> gated_auto/manual 交用户 -> 残余写入 todo
    |
    v
dev:verify 自动叠加额外层:
    |
    +-- diff 涉及 views/components/css   -> test-browser (受影响路由)
    +-- 5+ UI 文件跨多页变更             -> gstack/qa (全站) + design-review
    +-- diff 涉及 auth/payment/secret    -> gstack/cso (OWASP + STRIDE)
    +-- diff 涉及 prompt/llm/ai          -> gstack/review (LLM 信任边界)
    +-- diff 涉及热 API/SQL              -> gstack/benchmark (性能基线)
    +-- diff 涉及 README/docs/CLI        -> gstack/devex-review
    |
    v
todo-resolve (批量处理残余)
```

### Phase 4 vs Phase 5 的 ce:review 区别

| | Phase 4 (内嵌) | Phase 5 (完整) |
|---|---|---|
| 模式 | `mode:autofix` | `interactive` |
| 目的 | 快速 safe_auto 修复 | 完整审查含 gated_auto 和 manual |
| 轮次 | 最多 2 轮 | 最多 3 轮 |
| 叠加层 | 无 | 按 diff 自动叠加 |

### 铁律

- **证据先于断言** -- 没跑命令不能说"通过了"
- **验证先于采纳** -- 审查反馈先验证再实现，技术正确性优先于社交礼貌

---

## Phase 6: 交付 -- "上线"

> 目标：从代码到生产环境
>
> 路由器：`dev:ship`
>
> 核心产出：PR + 部署

### 智能路由：按项目类型和上游质量自动选路径

```
验证通过的代码 (from Phase 5)
  |
  +-- [未版本化 + 上游 ce:review 已确认] -> Path A: CE 轻量
  |   git-commit-push-pr -> land-and-deploy
  |
  +-- [版本化项目 (有 VERSION 文件)] ----> Path B: gstack 完整
  |   ship -> document-release -> land-and-deploy
  |
  +-- [无上游审查证据] ------------------> Path B: gstack 完整
  |
  +-- [紧急热修复] ----------------------> Path A: CE 轻量
```

### 自动检测的前置和叠加操作

| 检测到的信号 | 自动动作 |
|---|---|
| PR 有未解决的审查线程 | 先 `resolve-pr-feedback` |
| Diff 涉及 UI 文件 | 并行 `feature-video` (PR 嵌入录屏) |
| 无部署配置文件 (greenfield) | 先 `setup-deploy` 配置部署 |

### Path A: CE 轻量路径

```
git-commit-push-pr (自适应 PR 描述)
  -> land-and-deploy (CI -> merge-readiness 报告 -> 合并 -> 部署 -> 金丝雀)
```

### Path B: gstack 完整发布路径

```
ship (合并基准分支 -> 测试 -> 覆盖率审计 60%/80% -> 计划完成度审计
      -> pre-landing review 多轮 -> adversarial review 多轮
      -> VERSION bump -> CHANGELOG 生成 -> 可二分提交)
  -> document-release (交叉引用 diff 同步所有文档)
  -> land-and-deploy (同上)
```

### `land-and-deploy` 关键设计

- 自动检测部署平台（Fly.io / Vercel / Render / Netlify / Heroku / GitHub Actions）
- 合并前就绪报告（最后人工关卡）
- 金丝雀验证按 diff 范围分级：docs 跳过、config smoke、backend 控制台、frontend 全量
- 每个失败点提供回滚选项

---

## Phase 7: 沉淀 -- "学到什么"

> 目标：将经验转化为可复用的组织知识
>
> 路由器：`dev:learn`
>
> 核心产出：`docs/solutions/*.md` + `learnings.jsonl` + 可选 `SKILL.md`

### 智能路由：按触发类型分流

```
完成的工作
  |
  +-- [问题被解决] ("fixed", "root cause") -> Route A: ce:compound
  |   并行子 Agent: Context Analyzer + Solution Extractor + Related Docs Finder
  |   -> docs/solutions/<category>/<slug>.md
  |
  +-- [迭代/周末结束] ("retro", "weekly") --> Route B: gstack/retro
  |   提交频率/代码量/测试比/文件热点/AI辅助比 + 趋势分析
  |
  +-- [发现可复用方法] ("always do this") -> Route C: writing-skills
  |   RED-GREEN-REFACTOR 创建 skill (TDD for docs)
  |
  +-- [知识库过期] ("outdated", "stale") --> Route D: ce:compound-refresh
  |   分类: Keep / Update / Consolidate / Replace / Delete
  |
  +-- [无新知识] --------------------------> 跳过 -> dev:discover (下一项)
```

### 双层知识架构

| 层 | 机制 | 粒度 | 触发 |
|---|---|---|---|
| `gstack/learn` | 自动、被动 | 一行洞察 | 每个 gstack 技能完成时 |
| `ce:compound` | 手动、主动 | 完整文档 | 显式调用 |
| `ce:compound-refresh` | 维护 | 更新/合并/删除 | 知识库过期时 |
| `writing-skills` | 方法论 | SKILL.md | 发现跨项目模式时 |
| `gstack/retro` | 周期 | 回顾报告 | 每周分析 |

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

## 编排器对比

### `dev:flow` -- 智能编排（推荐）

```
dev:flow
  |
  自动检测 -> 进入正确阶段 -> 驱动到完成
  |
  dev:discover -> GATE -> dev:design -> GATE -> dev:plan -> GATE
      -> dev:code -> GATE -> dev:verify -> GATE -> dev:ship -> GATE
      -> dev:learn -> 闭环
```

- **智能路由**: 每个阶段内部自动检测场景，选最优技能组合
- **GATE 暂停**: 用户确认后才继续
- **恢复智能**: 跨会话自动检测中断位置
- **阶段跳过**: 自动检测哪些阶段可跳过

### `lfg` -- 全自动编排

```
ce:plan -> GATE -> ce:work -> GATE -> ce:review(autofix) -> todo-resolve -> test-browser -> feature-video -> DONE
```

- 串行执行，适合明确知道从 Phase 3 开始的场景
- 无场景检测，无阶段跳过

### 何时用哪个

| 场景 | 推荐 |
|---|---|
| 不确定从哪开始 | `dev:flow` |
| 从零开始新功能 | `dev:flow` |
| 跨会话恢复工作 | `dev:flow` |
| 有明确计划，一键执行 | `lfg` |
| 已有需求，快速走完 plan->ship | `lfg` |

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

## 多轮审查循环（贯穿全流程）

所有涉及 review 的环节执行统一的循环模式：

```
审查 -> 发现问题 -> 修复 -> 再审查 -> ...
                                    |
                                    终止条件:
                                    (a) 零 P0/P1 发现
                                    (b) 达到最大轮次（Phase 4: 2 轮, 其余: 3 轮）
                                    (c) 连续两轮发现相同问题（收敛）
```

---

## 文档追溯链（贯穿全流程）

```
Phase 1            Phase 2            Phase 3            Phase 4         Phase 5         Phase 6
需求文档            DESIGN.md          实施计划            ce:work         ce:review       交付
R1,R2,R3 -------> Token/色值 -------> Req Trace -------> 实现代码 -----> R-ID 验证 ----> PR
                                       Impl Units         增量提交        safe_auto       部署
                                       Test Scenarios                     修复
                                                                                     Phase 7
                                                                                     docs/solutions/
                                                                                     learnings.jsonl
                                                                                         |
Phase 3 (ce:plan) <-- learnings-researcher 自动搜索 ------------------------------------+

每个阶段的产出是下一阶段的输入。R-ID 从 Phase 1 贯穿到 Phase 5。知识从 Phase 7 回流到 Phase 3/5。
```

---

## 四库定位总结

| 库 | 技能数 | 定位 | 核心价值 |
|---|---|---|---|
| **Agent Skills** | 21 | 工程**基础** | 20 个通用工程实践（TDD、调试、代码审查、API 设计、安全加固、性能优化等）-- 独立于工具链的基本功 |
| **Superpowers** | 14 | 开发**方法论** | 定义"怎样才算做对了" -- TDD、根因调试、证据验证等铁律 + 技能激活与编排机制 |
| **Compound Engineering** | 42 | 开发**流水线** | 定义"数据怎么流" -- brainstorm->plan->work->review 的文档驱动管道 + 知识复利系统 |
| **gstack** | 41 | 开发**工具箱** | 定义"用什么工具" -- 设计探索、多视角评审、部署验证、安全审计、浏览器测试等专业工具 |

### 四库分层关系

```
┌─────────────────────────────────────────────────┐
│          dev: 编排层 (8 技能)                     │  "该进哪个阶段，用哪些技能"
│  dev:flow / discover / design / plan /           │
│  code / verify / ship / learn                    │
├─────────────────────────────────────────────────┤
│          gstack 工具箱 (41 技能)                  │  "专业工具：设计/评审/部署/安全/QA"
├─────────────────────────────────────────────────┤
│   Compound Engineering 流水线 (42 技能)           │  "文档驱动管道 + 知识复利"
├─────────────────────────────────────────────────┤
│        Superpowers 方法论 (14 技能)               │  "铁律 + 反合理化"
├─────────────────────────────────────────────────┤
│       Agent Skills 基础层 (21 技能)               │  "通用工程实践"
└─────────────────────────────────────────────────┘
```

四者组合 = **通用工程基础** + **有纪律的方法论** + **可追溯的文档管道** + **全栈工具支撑** + **智能编排路由**

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
