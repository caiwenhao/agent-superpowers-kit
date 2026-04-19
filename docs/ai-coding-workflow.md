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
| Signal 0: 是否在任务专属工作区 | `git rev-parse --abbrev-ref HEAD` + `git worktree list` | 在 main/master 或未进入任务专属 worktree -> 调用 `compound-engineering:git-worktree`（或 `superpowers:using-git-worktrees`）先创建工作区，再进入任何 Phase |
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

**前置步骤：Wiki Query** -- 路由前先查询项目 wiki + 全局 wiki，已有相关知识注入 brainstorm 上下文。

```
用户输入
    |
    v
Wiki Query (项目 wiki/index.md + ~/.claude/wiki/index.md)
    |  找到相关页 -> 读取并注入 brainstorm context
    |  无相关页 -> 跳过
    |
    v
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
    |  并行研究 Agent (repo-research + learnings + best-practices + framework-docs + wiki-search)
    |  Wiki Query: 搜索项目 wiki/ + 全局 ~/.claude/wiki/ 获取已有模式和决策
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
    +-- 可度量优化目标            -> ce-optimize (迭代实验循环)
    |
    v
每个任务内部：
    实现 -> Test Discovery -> System-Wide Test Check -> 暂存变更（git add，不 commit）
    每 2-3 单元: Simplify 通道（跨单元去重，仍不 commit）
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
| 运行时遇到 bug | `ce-debug`（因果链门控 4 阶段）/ `investigate` |
| 多个独立测试失败 | `dispatching-parallel-agents` |
| 触碰 `views/`, `components/`, `*.tsx`, `*.css` | `frontend-design`（自动检测 DESIGN.md） + `dev-browser`（启动 dev server 后真机验证 golden path） |
| Plan 引用 GitHub Issue | `reproduce-bug`（涉及 UI 复现时叠加 `dev-browser`） |
| 目标为可度量指标优化（prompt/性能/搜索质量） | `ce-optimize`（实验循环 + 度量收敛） |

### Phase 4 → Phase 5 过渡关：`/simplify`

所有 Unit 完成、准备进入 Phase 5 前，默认手动调用一次 `/simplify`——它并行派三个 agent（复用 / 质量 / 效率）扫整个累积 diff 并直接修复：

| Agent | 抓什么 |
|---|---|
| **Agent 1: 复用** | 新写的代码是否有现成 util / helper 可替换；内联手写的字符串/路径处理/类型守卫是否有已有函数 |
| **Agent 2: 质量** | 冗余 state、参数堆砌、复制粘贴微变、泄漏抽象、stringly-typed、无用 JSX 嵌套、无用注释（解释 WHAT 而非 WHY） |
| **Agent 3: 效率** | 重复计算、可并行化的串行 I/O、热路径臃肿、轮询里无变更检测的 no-op 更新、TOCTOU 前置 exists 检查、无界内存、过度读取 |

**调用时机**：

- ✅ 所有 Unit 完成、Phase 4 收尾时（**默认**）
- ✅ 中途某个 Unit 改动量大 / 重构密集 / 引入新抽象时可选插一次
- ❌ 每个 Unit 都跑（太频繁，`ce:work` 已自动每 2-3 Unit 做内置 simplify pass）
- ❌ `ce:review` 完成后再跑（维度重叠）

**与 `ce:work` 内置 simplify pass 的区别**：

| | ce:work 内置 | 手动 `/simplify` |
|---|---|---|
| 频率 | 每 2-3 Unit 自动 | Phase 4 收尾一次 |
| 扫描范围 | 跨单元去重 | 完整累积 diff 三维（复用/质量/效率） |
| 执行方式 | 单 agent 串行 | 三 agent 并行 |
| 修复策略 | 保守去重 | 直接修 + 跳过 false positive |

### 铁律

- **无失败测试，不写生产代码**
- **无根因分析，不尝试修复**
- **3 次修复失败，停下质疑架构**
- **不主动提交** —— Phase 4 结束时变更可能 staged 或 unstaged，但绝不自动创建 commit；提交在 Phase 6 由用户触发

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
    |-- 跨模型对抗审查: Claude + Codex 始终并行派发
    |   大 diff (200+ 行) 额外加 Codex 结构化 P1 门控
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
    +-- diff 涉及 views/components/css   -> test-browser (受影响路由) | `dev-browser`（轻量 stdin 脚本，跨 harness 通用）
    +-- 5+ UI 文件跨多页变更             -> gstack/qa (全站) + design-review | `dev-browser`（脚本化遍历多页路由）
    +-- diff 涉及 auth/payment/secret    -> gstack/cso (OWASP + STRIDE)
    +-- diff 涉及 prompt/llm/ai          -> gstack/review (LLM 信任边界)
    +-- diff 涉及热 API/SQL              -> gstack/benchmark (性能基线)
    +-- diff 涉及 README/docs/CLI        -> gstack/devex-review
    +-- AI 生成代码质量检测              -> slop-scan (信息性，非阻塞)
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
| 叠加层 | 无 | 按 diff 自动叠加 + 跨模型对抗 + slop-scan |

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
git-commit-push-pr (ce-pr-description 生成描述 -> 自适应 PR)
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
- 金丝雀验证按 diff 范围分级：docs 跳过、config smoke、backend 控制台、frontend 全量（frontend 优先用 `dev-browser --headless` + Playwright API 脚本验证关键路由 / 表单 / 控制台无 error）
- 每个失败点提供回滚选项

---

## 工作流引导 -- `dev:init`

> 让任意仓库开始遵循 `dev:*` 工作流的入口工具。不参与流程编排。

`dev:init` 向目标仓库的 `CLAUDE.md` **追加**"dev:* preamble"节（七条铁律 + 编码行为约束 + 中文工作语言 + 提交由用户触发），带 `<!-- dev:* preamble: start/end -->` 锚点。已有同节时询问"保留 / 替换 / 手动编辑"，**默认保留**。随后建 `AGENTS.md -> CLAUDE.md` 软链(Codex 兼容),并把仓库级技能目录迁移为 cross-harness 单源布局:

```
<project>/
├── skills/                     # 单源
├── .claude/skills -> ../skills
└── .agents/skills -> ../skills
```

已是目标形态时幂等跳过;`.claude/skills/` 或 `.agents/skills/` 已是真目录的历史布局走 GATE 确认后迁移;两侧都是真目录且有冲突时询问合并策略。

### 与 Claude Code 内置 `/init` 的分工

| 工具 | 管什么 |
|---|---|
| `/init`（内置） | "**项目是什么**" —— 扫代码生成通用 CLAUDE.md |
| `/dev:init`（本套） | "**项目按什么工作流走**" —— 注入 `dev:*` 契约 preamble + 建 cross-harness 技能目录 |

两者正交。典型顺序：先 `/init` → 再 `/dev:init` → 最后 `/dev:doctor` 体检依赖。

### 不做的事（保持轻量）

- ❌ 修改 `.claude/settings.json`
- ❌ 创建 `docs/brainstorms/plans/solutions/` 空目录
- ❌ 安装 plugin / symlink 上游 skills
- ❌ 自动 `git commit`
- ❌ 自动改 `.gitignore`（只提示白名单写法）

---

## 依赖健康检查 -- `dev:doctor`

> 跨 phase 的诊断工具，不参与流程编排。

`dev:*` 流程引用大量第三方技能（`compound-engineering:*`、`superpowers:*`、`gstack-*`、`ce:*`）和 CLI（`dev-browser`）。当机器 / harness 切换、plugin 升级、或某个 phase 路由到的 skill 报"not found"时，调用 `/dev:doctor` 一次性扫描全部依赖，给出三态报告：

- ✅ **已安装** -- 在默认位置找到
- ❌ **缺失** -- 默认位置和 PATH 都没找到 → 影响哪些 phase 必须列出
- ⚠️ **可疑** -- 默认位置没找到，但可能由 plugin marketplace 加载（不是错误）

### 何时调用

| 场景 | 为什么 |
|---|---|
| 仓库 clone 到新机器 / 新 harness | 第一次跑 `/dev:flow` 前先体检 |
| 某个 phase 路由失败、skill not found | 定位是依赖缺失还是路由错误 |
| 上游 plugin 升级后 | 确认没有重命名失效的引用 |
| Codex ↔ Claude Code 切换 | gstack-* 缺失属预期降级，要让用户知道哪些 phase 受影响 |

### 与流程的关系

`dev:doctor` **不是 phase**，不出现在 `dev:flow` 的串行链中。它是横切诊断：

```
            ┌───────────────────────────┐
            │  dev:doctor (按需调用)      │
            │  ✅/❌/⚠️ 三态 + phase 影响  │
            └───────────┬───────────────┘
                        ↓
       ┌────┬────┬────┬────┬────┬────┬────┐
       │ P1 │ P2 │ P3 │ P4 │ P5 │ P6 │ P7 │
       └────┴────┴────┴────┴────┴────┴────┘
       discover/design/plan/code/verify/ship/learn
```

### 铁律

- **只读诊断** -- 不安装、不修改、不提交
- **不预设位置** -- plugin 加载路径因 harness 而异，默认位置没找到时标 ⚠️ 而非 ❌
- **降级不是错误** -- Codex 上 gstack-* 缺失是预期，报告中明确"已知降级"

---

## 浏览器自动化工具选择（贯穿 Phase 4/5/6）

涉及 UI 验证、QA 测试、金丝雀检查时的工具优先级：

| 场景 | 推荐工具 | 理由 |
|---|---|---|
| **本地启动 dev server 后跑 golden path / 表单 / 控制台无 error**（Phase 4 收尾、Phase 5 PR 前自检） | **`dev-browser`** | 单二进制 CLI，stdin 接 JS 脚本，QuickJS 沙箱内调用 Playwright API；跨 harness 通用（Claude Code / Codex / 任意 shell）；自动 attach 已开 Chrome 或 launch Chromium |
| 受影响路由的回归用例（Phase 5 自动叠加） | `test-browser`（gstack） | 与 ce:review 联动产生结构化报告 |
| 全站 QA 与 bug 修复闭环（Phase 5，5+ UI 文件） | `gstack/qa` | 报告 + 自动修复 + 重验证一体；浏览器层用 dev-browser 也可作 fallback |
| 视觉 / 设计回归 | `design-review`（gstack） | 截图对比 + 严重性评分 |
| 部署后金丝雀（Phase 6） | `dev-browser` 脚本 + `gstack-canary` 长期监控 | dev-browser 一次性烟测，gstack-canary 持续观测 |

### dev-browser 调用约定

```bash
# 安装一次（pre-approve in .claude/settings.json: "Bash(dev-browser *)"）
npm install -g dev-browser && dev-browser install

# 标准调用：stdin 传脚本
dev-browser --headless <<'EOF'
const page = await browser.getPage("main");
await page.goto("http://localhost:3000/login", { waitUntil: "domcontentloaded" });
await page.fill('input[name="email"]', "test@example.com");
await page.click('button[type="submit"]');
console.log(await page.title());
await page.screenshot({ path: "/tmp/after-login.png" });
EOF

# 连接已开 Chrome（保留登录态、跨脚本持久化页面）
dev-browser --connect <<'EOF' ...
```

**何时不用 dev-browser**：需要与 ce:review / gstack 报告管线集成时优先 `test-browser` / `gstack/qa`；纯 MCP 工作流可继续用 Playwright MCP。dev-browser 的优势是**轻量 + 跨 harness + 沙箱安全**，适合作为 Phase 4-6 的默认 UI 验证刀。

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
  +-- [技能可改进] ("同一发现反复出现",  -> Route E: writing-skills (REFACTOR 模式)
  |   "流程总在此卡住",                    审查现有 SKILL.md -> 识别 gap -> 更新
  |   "上游有新能力")                      验证: 改进后的技能在历史场景中表现更好
  |
  +-- [外部知识源] ("这篇文章",           -> Route F: Wiki Ingest
  |   "这个文档", "研究一下这个")           读源 -> 写摘要页 -> 更新 entity/concept 页
  |                                        更新 index.md + 追加 log.md
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
| `writing-skills` (REFACTOR) | 技能改进 | 更新 SKILL.md | 重复发现 / 流程摩擦 / 上游更新 |
| Wiki Ingest | 知识编译 | wiki 页面（5-15 页/次） | 每次 solution/retro 写入后 + 外部源 |
| `gstack/retro` | 周期 | 回顾报告 | 每周分析 |

### 知识闭环

```
Phase 4 (ce:work) -- 解决问题 --> Phase 7 (ce:compound) -- 沉淀 --> docs/solutions/
                                                                        |
                                                                   Wiki Ingest
                                                                        |
                                                                   wiki/ (结构化互链)
                                                                        |
Phase 1 (ce:brainstorm) <-- Wiki Query 注入已有知识 --------------------+
Phase 3 (ce:plan) <-- learnings-researcher + wiki-search ---------------+
Phase 5 (ce:review) <-- learnings-researcher 始终启用 -------------------+
所有 gstack 技能 <-- preamble 自动搜索 learnings.jsonl ------------------+
```

**知识不只是被记录 -- 它被��译成结构化知识网，自动注入到未来的发现、规划和审查中。**

---

## 技能演进机制（跨阶段）

> Phase 7 的 Route E 处理运行时发现的改进。本节定义**定期巡检和上游同步**的独立机制。

### 触发信号

| 信号 | 来源 | 检测方式 |
|---|---|---|
| **重复发现** | Phase 5 review 多次报告同类 P1 | `learnings.jsonl` 中同一 category 出现 3+ 次 |
| **流程摩擦** | Phase 4 实现中反复踩同一坑 | retro 报告中相同文件热点连续 2 周 |
| **上游新能力** | compound-engineering / superpowers / gstack 子模块更新 | `git submodule status` delta 非零 |
| **技能过期** | 技能引用的工具/技能已改名或删除 | 技能内引用的 skill name 在 skill registry 中不存在 |

### 改进流程

```
触发信号
    |
    v
分析 gap（哪条路由/规则需要改）
    |
    +-- [上游新能力] ----> 1. 读上游 SKILL.md / changelog
    |                       2. 判断是否影响 dev:* 路由
    |                       3. 更新 workflow 文档 + claude-skills/
    |
    +-- [重复发现] ------> 1. 从 learnings.jsonl 聚合模式
    |                       2. 定位缺失的路由规则或检测信号
    |                       3. writing-skills REFACTOR 更新技能
    |
    +-- [流程摩擦] ------> 1. 从 retro 提取摩擦点
    |                       2. 追溯到具体 Phase 的 Scene Detection
    |                       3. 补充信号或调整路由
    |
    +-- [技能过期] ------> 1. 扫描 SKILL.md 中的引用
                            2. 替换为当前等价技能
                            3. 验证路由仍可达
    |
    v
验证: 改进后的技能在历史场景（retro 中的案例）中路由正确
    |
    v
同步: docs/ai-coding-workflow.md + claude-skills/ 同时更新
```

### 巡检节奏

| 频率 | 动作 |
|---|---|
| **每次 retro（周）** | 扫描 `learnings.jsonl` 重复模式 + retro 摩擦点 -> 触发 Route E |
| **每次子模块更新** | 对比 delta，分析新技能是否影响 dev:* 路由 |
| **每月** | 全量扫描 claude-skills/ 引用的技能名，标记过期引用 |
| **每次 retro（周）** | **Wiki Lint**: 检查矛盾、过期引用、孤儿页、缺失概念页、断裂交叉引用 |

### 知识-技能双闭环

```
知识闭环 (已有):
Phase 4 -> 解决问题 -> Phase 7 -> docs/solutions/ -> Phase 3/5 (learnings-researcher)

技能闭环 (新增):
Phase 5 -> 重复发现 -> Phase 7 Route E -> 更新 SKILL.md -> Phase 4/5 (更好的路由)
retro   -> 摩擦点   -> 技能巡检      -> 更新 SKILL.md -> 所有 Phase (更少摩擦)
上游更新 -> delta    -> 技能同步      -> 更新 SKILL.md -> Phase 4/5 (新能力可用)
```

**知识沉淀让未来少犯错。技能演进让流程本身持续变好。两者组合 = 复利的复利。**

---

## Wiki 知识层（贯穿全流程）

> 基于 [LLM Wiki](https://gist.github.com/tobi/1cf3f88b03f6cad16c1ebd530096e649) 模式：LLM 增量构建和维护一个结构化互链的 Markdown 知识网。原始文档（docs/solutions/、learnings.jsonl、retro 报告）是不可变的源，wiki 是它们的编译产物。

### 两层架构

```
项目级: {project}/wiki/
  ├── index.md          # 内容索引（LLM 维护，Query 入口）
  ├── log.md            # 操作日志（append-only: ingest/query/lint）
  ├── entities/         # 实体页（模块、服务、API、数据模型）
  ├── concepts/         # 概念页（架构模式、设计决策、技术选型）
  ├── sources/          # 源摘要页（brainstorm/retro/外部文档摘要）
  └── synthesis/        # 综合页（跨源分析、对比、演进趋势）

全局级: ~/.claude/wiki/
  ├── index.md
  ├── log.md
  ├── frameworks/       # 框架最佳实践（Rails, React, etc.）
  ├── patterns/         # 通用工程模式（缓存策略、错误处理、测试策略）
  ├── conventions/      # 团队约定（命名、提交、审查标准）
  └── tools/            # 工具使用知识（CLI、部署平台、监控）
```

项目 wiki 记录**项目特定**知识（本项目的架构、踩坑、决策）。全局 wiki 记录**跨项目通用**知识（框架模式、工具经验、团队约定）。两层互相引用。

### 三操作

| 操作 | 描述 | 触发阶段 |
|---|---|---|
| **Ingest** | 读源 → 写/更新摘要页 → 更新 entity/concept 页（5-15 页/次）→ 更新 index.md → 追加 log.md | Phase 7 (自动) + Phase 1 (外部源) |
| **Query** | 读 index.md → 定位相关页 → 读取 → 综合回答（好的回答可反写为 synthesis 页） | Phase 1 (前置) + Phase 3 (研究) |
| **Lint** | 检查矛盾、过期引用、孤儿页、缺失概念页、断裂交叉引用 → 建议修复 + 新源待 ingest | 技能巡检（周） |

### 与现有知识层的关系

```
Raw Sources（保留，不可变）:
  docs/solutions/*.md        -- ce:compound 写入的解决方案
  learnings.jsonl            -- gstack 自动写���的一行洞察
  docs/brainstorms/          -- 需求文档
  retro reports              -- 回顾报告

Wiki（新增，LLM 维护）:
  {project}/wiki/            -- 项目知识的结构化编译
  ~/.claude/wiki/            -- 跨项目知识的结构化编译

关系: Raw Sources 是 Wiki 的输入。Wiki 是 Raw Sources 的结构化编译。
两者共存。Wiki 不替代 Raw Sources，而是在其上构建交叉引用和综合分析。
```

### Wiki 在各阶段的角色

```
Phase 1 (Discover)                    Phase 3 (Plan)
  Wiki Query ──────────────────────>    Wiki Query
  "已有 3 篇相关页，                     ce:plan 研究 Agent
   注入 brainstorm"                     搜索 wiki 获取模式和决策
         ^                                    ^
         |                                    |
         |         Wiki (持续编译)              |
         |     ┌──────────────────┐           |
         +─────│  entities/       │───────────+
               │  concepts/       │
               │  sources/        │
               │  synthesis/      │
               └──────┬───────────┘
                      ^
                      |
              Wiki Ingest (5-15 页/次)
                      |
Phase 7 (Learn)       |         外部知识
  ce:compound ────────+      用户提供文章/
  retro ──────────────+      文档/paper ──────+
```

### 跨项目知识传播

```
项目 A 的 wiki/concepts/caching-strategy.md
  |
  "这个缓存策略适用于所有 Rails 项目"
  |
  v
~/.claude/wiki/patterns/rails-caching.md (全局)
  |
  v
项目 B 的 Phase 3 (ce:plan) -- Wiki Query 搜全局 wiki
  -> "全局 wiki 有 Rails 缓存最佳实践，引用到计划中"
```

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

## 七条铁律（贯穿全流程）

| # | 铁律 | 守护技能 |
|---|---|---|
| 1 | **设计先于实现** -- 需求文档批准前不碰代码 | brainstorming, ce:brainstorm |
| 2 | **测试先于代码** -- 无失败测试不写生产代码 | test-driven-development |
| 3 | **根因先于修复** -- 不理解为什么坏就不能修 | systematic-debugging, investigate |
| 4 | **证据先于断言** -- 没跑命令不能说"通过了" | verification-before-completion |
| 5 | **验证先于采纳** -- 审查反馈先验证再实现 | receiving-code-review |
| 6 | **工作区先于工作** -- 创建任何文档或代码前必须在任务专属 worktree / feature branch 中，否则先创建工作区 | dev:flow Signal 0, compound-engineering:git-worktree, superpowers:using-git-worktrees |
| 7 | **提交由用户触发** -- AI 在 Phase 1-5 只修改文件、运行测试，不主动 `git commit` / `git push` / 创建 PR；提交仅在用户显式调用 `/dev:ship` 或说"提交/commit/push/PR"时进行 | dev:ship, ce:git-commit-push-pr, gstack-ship |

---

## 编码行为约束（贯穿 Phase 4-5）

> 七条铁律管**流程**，本节管**行为**。源自 Karpathy 对 LLM 编码常见陷阱的观察，仅提取现有流程未覆盖的增量约束（#2 Simplicity 由 `/simplify` 覆盖，#4 Goal-Driven 由 R-ID + TDD 覆盖，不重复）。

### 1. 明确假设 / 不懂就问（Think Before Coding）

- 开始实现前，**显式列出你做出的关键假设**（数据结构、调用方、错误模式、性能预期）；假设错了，代码全错。
- 需求有**多种合理解释**时，列出来让用户选，**不要静默挑一个**。
- **不确定就 STOP 问**，不要靠猜继续。标注"我不清楚 X"比写错一百行再重写便宜。
- 存在更简单的方案时**说出来**；用户让你做 A，你看出 B 更简单，先讲 B 再让用户决定。

### 1a. 澄清时必须带"推荐标识"

调用澄清工具（`AskUserQuestion` 等）向用户提问时，**必须显式标注推荐项**：

- 有明确倾向时：推荐项**排第一**，标签末尾加 `(Recommended)` 或`（推荐）`。
- 无明确倾向时：明说"无明确推荐，请你决定"，**不要伪装中立**。
- 每个选项给一句 `description` 讲清楚**选它的后果**（不是选项的重复），便于用户判断。
- 多选场景（`multiSelect: true`）：推荐组合在问题本文中先点出（"推荐勾选 A+B"），选项 label 保持描述性。

**反面示例**：四个选项看起来都一样严肃，用户无从判断；或者你心里明明有倾向却假装所有选项等权——这会把决策压力非对称地转嫁给用户，违反"显式沟通"原则。

### 2. 手术刀修改（Surgical Changes）

- **只改和任务直接相关的行**；每一行改动都应该能直接追溯到用户请求或计划 Implementation Unit。
- **不顺手"改进"相邻代码 / 注释 / 格式**——即使你确信自己的风格更好。
- **匹配现有代码风格**，即使你不认同；风格统一的价值大于个人偏好。
- 发现与任务**无关的 dead code**：**只提及，不删除**；留给独立清理任务处理。

### 3. 孤儿清理（Orphan Cleanup）

- 清理**你自己的改动**产生的未使用 import / 变量 / 函数。
- **不清理原有的** dead code / legacy 残留，除非任务明确要求。
- 区分标准：孤儿是不是**因为你这次改动**才变成孤儿的？是 → 清；否 → 留。

### 自检问题（Phase 4 收尾 + Phase 5 审查时用）

- 每一行改动能直接对应 R-ID 或 Implementation Unit 吗？
- 我是否在用户没要求的地方加了"灵活性" / "可配置性" / "防御性错误处理"？
- 我改动的相邻代码是否被我"顺手改进"了？
- 我是否删除了不是我的改动产生的 dead code？
- 我是否在不确定时静默选了一个方向而不是问用户？

任何一个"是"→ 回滚相关改动，或在 `/simplify` 时专门清扫。

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
