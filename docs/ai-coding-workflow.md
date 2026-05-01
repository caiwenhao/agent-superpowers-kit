# AI Coding 研发流程全景图

四套技能库（Agent Skills / Superpowers / Compound Engineering / gstack）+ `dev:` 编排层，组合形成 **7 阶段研发流程**。

每个阶段标注了**智能路由逻辑**、**最佳技能组合**和**核心产出文档**，基于对 120+ 个技能源码的深度分析。

```
┌──────────────────────────────────────────────────────────────────────┐
│                      AI Coding 研发全流程                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              dev:flow -- 智能编排器（单一入口）                  │    │
│  │  自动检测当前阶段并推进；只在重大疑问/冲突/风险取舍时 GATE        │    │
│  └──────────────────────────────────────────────────────────────┘    │
│      |                                                               │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │ 发现  │->│ 设计  │->│ 规划  │->│ 实现  │->│ 验证  │->│ 预交付│       │
│  │Phase1│  │Phase2│  │Phase3│  │Phase4│  │Phase5│  │Phase5│       │
│  │dev:  │  │dev:  │  │dev:  │  │dev:  │  │dev:  │  │.5     │       │
│  │disco-│  │design│  │plan  │  │code  │  │verify│  │learn/│       │
│  │ver   │  │      │  │      │  │      │  │      │  │super │       │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  └───┬──┘       │
│                                                        v           │
│                                                    ┌──────┐       │
│                                                    │ 交付  │       │
│                                                    │Phase6│       │
│                                                    │dev:  │       │
│                                                    │ship  │       │
│                                                    └──────┘       │
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

> **用户不需要手动选择技能组合。** `dev:flow` 是唯一入口，自动检测当前状态并路由到正确阶段。默认 guided auto-advance：阶段通过且下一步唯一明确时自动继续；只有重大疑问、冲突、风险取舍、破坏性动作或用户明确要求逐步确认时才 GATE。

### 场景检测（按优先级）

| 信号 | 检测方式 | 路由结果 |
|---|---|---|
| Signal 0: 是否在任务专属工作区 | `git rev-parse --abbrev-ref HEAD` + `git worktree list` | 在 main/master 或未进入任务专属 worktree -> 调用 `compound-engineering:ce-worktree`（或 `superpowers:using-git-worktrees`）先创建工作区，再进入任何 Phase |
| Signal 1: 有无未完成工作 | plan status + git status + PR | 恢复到中断的阶段 |
| Signal 2a: 是否为 Bug 修复意图 | 关键词（bug / fix / 修复 / 报错 / crash / regression）+ 引用 Issue / 错误日志 / stack trace | **Bug Fix 快速路径**（见下方专节） |
| Signal 2b: 用户输入了什么 | 意图分类 | 路由到匹配阶段 |
| Signal 3: 存在哪些产物 | 扫描 docs/ + DESIGN.md + .context/ | 跳到最近的未完成阶段 |

### GATE 机制

`dev:flow` 区分 status checkpoint 和 decision GATE：

| 出口 | 是否问用户 | 用法 |
|---|---|---|
| Status checkpoint | 不问；报告证据后继续 | 当前 phase 已通过，下一步唯一明确 |
| Decision GATE | 问；必须有明确选项 | 存在阻塞、重大疑问、风险取舍、破坏性动作、多个合理路线、或用户明确要求逐步确认 |

确认必须有决策价值。如果推荐项永远是"继续下一阶段"，那就不是 GATE。编号选项只用于用户必须做选择的情况。

默认 guided 行为：
- 当前阶段通过且下一步唯一明确 -> 自动继续
- 提醒级信息（如主干偏离 6-15 commits）-> 打印后继续
- 遇到 hard blocker（未满足工作区前置、测试失败、强制 review gate 未清零 P0/P1、merge conflict、deploy 失败、缺少关键工具等）-> 立即 STOP，转回人工处理
- 进入 Phase 6 但没有显式 ship 授权 -> STOP，请求交付授权

`mode:manual` 只有用户明确要求"每步确认/逐步确认"时启用。
`mode:auto` 表示用户授权自动推进非阻塞步骤，并授权在无 blocker 时进入 `/dev:ship`。

### 主干同步（Trunk Sync）

> 工作区离 main 越远，最终合并越痛苦。每个 GATE 自动检测偏离度。

| 偏离度 | 表现 | 动作 |
|---|---|---|
| 0-5 commits | ✅ 显示偏离数 | 无 |
| 6-15 commits | ⚠️ 黄色提醒 | 打印提醒后继续；只有用户要求逐步确认时才停下 |
| 16+ commits | 🔴 红色警告 | STOP，要求先同步主干，再继续流程 |

Phase 4 长实现阶段：每 3 个 Implementation Unit 完成后额外检查一次。
Phase 5 通过后、Phase 6 前：先执行 **Phase 5.5 交付前沉淀/自省判断**，按需运行 `dev-learn` / `dev-supervise`。随后 Phase 6 前仍 **强制同步**（不可跳过），rebase 后有冲突则协助解决。

### 阶段跳过规则

| 条件 | 跳过 |
|---|---|
| 纯后端，需求无 UI | Phase 2 (design) |
| Bug 修复（含微小修复、紧急热修复） | **走 Bug Fix 快速路径**（Signal 2a），不走标准 Phase 链 |
| 需求文档已存在且已批准 | Phase 1 |
| DESIGN.md 已存在且无新 UI 模式 | Phase 2 |
| 计划已存在且已审查 | Phase 3 |
| 无新知识且无 skill 自省信号 | Phase 5.5 的 `dev-learn` / `dev-supervise` |
| 仅文档变更 | Phase 1, 2, 3 -> Phase 4 内联 |
| 依赖升级 | Phase 2 |

### 恢复智能

再次调用 `/dev:flow` 时，自动扫描产物（plan status、git branch、PR state），宣告恢复位置并继续。

### Bug Fix 快速路径

> 当 Signal 2a 检测到 bug 修复意图时，跳过标准 Phase 1-3 链，进入专用修复流程。
>
> 核心原则：**根因先于修复**（铁律 #3）。不理解为什么坏就不能修。

```
用户报告 bug / 引用 Issue / 粘贴错误日志
    |
    v
Signal 0: 工作区检查（同标准流程）
    |
    v
┌─────────────────────────────────────────────┐
│  Step 1: 复现                                │
│  reproduce-bug                               │
│  (涉及 UI 时叠加 dev-browser)                │
│  产出：可稳定触发的复现步骤 + 失败断言        │
│  ⛔ 无法复现 -> 停下，向用户要更多上下文       │
└─────────────────────────────────────────────┘
    |
    v
┌─────────────────────────────────────────────┐
│  Step 2: 根因定位                            │
│  ce-debug（因果链门控 4 阶段）/ investigate   │
│  产出：定位到具体代码行 + 因果链解释          │
│  ⛔ 3 轮定位失败 -> 停下质疑架构              │
└─────────────────────────────────────────────┘
    |
    v
┌─────────────────────────────────────────────┐
│  Step 3: 修复实现（= Phase 4 子集）          │
│  TDD: 先将复现步骤固化为回归测试（RED）       │
│       再写最小修复代码（GREEN）               │
│  ⛔ 不扩大修复范围——只修根因，不顺手重构      │
└─────────────────────────────────────────────┘
    |
    v
┌─────────────────────────────────────────────┐
│  Step 4: 回归验证（= Phase 5 子集）          │
│  - 回归测试通过                               │
│  - 全量测试套件无新失败                       │
│  - 涉及 UI 时 dev-browser 验证修复效果        │
└─────────────────────────────────────────────┘
    |
    v
GATE: 报告修复结果，先进入 Phase 5.5 判断是否需要沉淀/自省，再决定是否进入 Phase 6 交付
```

#### 路由细节

| 信号 | 路由 |
|---|---|
| 用户描述 bug + 提供复现步骤 | Step 1 快速确认 -> Step 2 |
| 用户粘贴 stack trace / 错误日志 | Step 2 直接开始（日志即复现证据） |
| 引用 GitHub Issue | `reproduce-bug` 从 Issue 提取复现步骤 -> Step 1 |
| 用户说"紧急"/"hotfix"/"线上" | 同上流程，但 GATE 提示优先交付，跳过非必要审查 |

#### 与标准流程的关系

- Bug Fix 路径**不产出需求文档**（Phase 1 产物），因为 bug 本身就是需求："恢复预期行为"。
- Bug Fix 路径**不产出设计文档**（Phase 2 产物），除非修复涉及 UI 变更且需要新的交互模式。
- 修复完成后汇入标准 Phase 6（交付），遵守铁律 #7（提交由用户触发）。
- 如果根因分析发现问题不是 bug 而是缺失功能，**退出 Bug Fix 路径，回到标准 Phase 1**。

#### 铁律（Bug Fix 专属补充）

- **无复现，不定位** —— 不能稳定复现的 bug 不进入 Step 2
- **无根因，不修复** —— 铁律 #3 的强化：禁止"试试看"式修复
- **不扩大范围** —— 只修根因，不顺手清理周边代码；清理另开任务
- **回归测试必须先于修复代码** —— 铁律 #2 在 bug 场景的具体化

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
                                  ce:doc-review
                                  (Route C/高风险强制；小范围低风险 opt-in)
```

`dev:discover` 自动检测用户输入的意图清晰度（无方向 / 有方向但不确定价值 / 多面向 / 清晰小范围），路由到正确的入口技能。**所有路径最终汇聚到 `ce:brainstorm`。**

| 技能 | 角色 | 何时触发 |
|---|---|---|
| `ce:ideate` | 创意发散 | 无方向时，生成 20-30 候选，筛选到 Top 5-7 |
| `office-hours` | 需求验证 | 有想法但不确定值不值得做 |
| **`ce:brainstorm`** | **需求定义（唯一出口）** | **所有场景最终汇聚于此** |
| `ce:doc-review` | 多人格审查 | Route C/Deep 或高风险需求强制；Route D 小范围低风险 opt-in |

### 为什么是 `ce:brainstorm` 的需求文档

- **R-ID 追溯**（R1, R2, R3...）-- 贯穿规划、实现、审查全流程的锚点
- **阻塞问题分级** -- Resolve Before Planning / Deferred to Planning
- **无实现泄漏** -- 只定义 WHAT，不泄漏 HOW
- **ce:doc-review（条件强制）** -- coherence / feasibility / product-lens / design-lens / security-lens / scope-guardian / adversarial 并行审查；Route C/Deep、高风险、或用户要求 review 时必须通过多轮门禁

### Phase 1 Review Gate

`dev:discover` 在 `ce:brainstorm` 写出需求文档后，先判断 review gate:

| 信号 | 动作 |
|---|---|
| Route C / Deep brainstorm | 强制 `ce-doc-review <requirements-path>` |
| R-ID 数量 >8 | 强制 `ce-doc-review` |
| 外部上游/API/SDK、public endpoint、model alias、协议契约 | 强制 `ce-doc-review` |
| auth/token/凭证、私域素材、用户数据、计费/pricing/quota、审计日志 | 强制 `ce-doc-review` |
| 用户明确说 review / 审查 | 强制 `ce-doc-review` |
| Route D 且无以上信号 | opt-in，brainstorm handoff 菜单提供 review |

多轮语义:
- 使用 Compound Engineering 的 `ce-doc-review` / `compound-engineering:ce-doc-review`，不要用 standalone `document-review` 替代。
- Codex 下若 reviewer-agent / task spawning 可用，优先做多 agent reviewer fanout；只有拿不到 reviewer agents 时，才允许降级为串行角色审查，并要明确报告降级。
- 循环: 审查 -> 修复/用户裁决 -> 再审查，直到零未处理 P0/P1、达到 3 轮上限、或连续两轮发现相同 P0/P1。
- 达到上限或收敛仍有 P0/P1 时，STOP；只有用户显式接受风险并把理由写入需求文档 Deferred/Open Questions，才允许进入 `/dev:plan`。
- Codex 没有阻塞提问工具时，用编号选项停下等待用户；不得把单轮主线程综合报告当作通过。

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
ce-doc-review (Layer 1, 多轮门禁)
    |  coherence / feasibility / scope-guardian
    |  零未处理 P0/P1 或记录化 override
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

### Phase 3 Review Gates

`dev:plan` 在进入 `/dev:code` 前有两层强制审查门禁:

| 层级 | 门禁 |
|---|---|
| Layer 1 | `ce-doc-review <plan-path>` 必须通过；不要用 standalone `document-review` 替代 |
| Layer 2 | 选中的 `plan-eng-review` / `autoplan` / `plan-design-review` / `plan-devex-review` 必须写入 REVIEW REPORT 并 cleared |

多轮语义:
- Codex 下若 reviewer-agent / task spawning 可用，优先做多 agent reviewer fanout；只有拿不到 reviewer agents 时，才允许降级为串行角色审查，并要明确报告降级。
- `ce:plan` 写出 plan 文件后不算完成；`dev:plan` 外层必须立刻进入 Layer 1 review gate，不能停在 `ce:plan` 的 handoff 菜单或“下一步建议”。
- 循环: 审查 -> 修复/用户裁决 -> 再审查，直到零未处理 P0/P1、达到 3 轮上限、或连续两轮发现相同 P0/P1。
- 达到上限或收敛仍有 P0/P1 时，STOP；只有用户显式接受风险并把理由写入计划 Deferred/Open Questions 或 Review Notes，才允许进入 `/dev:code`。
- Codex 没有阻塞提问工具时，用编号选项停下等待用户；不得把单轮主线程综合报告当作通过。
- gstack 审查技能在 Codex 环境不可用时，STOP 并要求用户选择手动执行、使用可用 fallback、或记录 override。

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
dev-code 外层编排
    |
    +-- 按 2-3 个 Implementation Units 切批
    +-- 每批调用 ce:work 只执行当前 batch
    +-- 禁止 ce:work 进入 shipping workflow / residual gate
    |
    v
每个 batch:
    ce:work 实现 -> Test Discovery -> System-Wide Test Check -> 暂存变更（git add，不 commit）
    -> ce:code-review mode:autofix (safe_auto only)
    |
    v
所有 Unit 完成:
    /simplify
    -> final ce:code-review mode:autofix
    -> gated_auto/manual 留给 Phase 5
```

### Phase 4 自动修复回路

`dev:code` 的 review 目标是**实现阶段自动修复**，不是最终质量裁决。

| 时机 | 动作 |
|---|---|
| 每个 2-3 Unit batch 完成后 | 运行 `ce:code-review mode:autofix plan:<path>` |
| 单批次/小改动完成后 | 至少运行一次 `mode:autofix` |
| 所有 Unit 完成后 | 先运行 `/simplify` |
| `/simplify` 之后 | 再运行一次 final `mode:autofix` |

规则:
- `dev-code` 是外层编排器；`ce:work` 只执行当前 batch，不进入自己的 shipping workflow / residual-review gate。
- 只自动应用 `safe_auto -> review-fixer`。
- 不处理 `gated_auto` / `manual` / `human` / `release` 决策；残余作为 downstream work/todo 交给 Phase 5。
- 不得因为后面还有 `dev:verify` 就跳过 Phase 4 autofix loop；Phase 5 是独立总体审查，不是自动修复替代品。

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

### Phase 4 → Phase 5 过渡关：`/simplify` + final autofix

所有 Unit 完成、准备进入 Phase 5 前，默认手动调用一次 `/simplify`，然后再运行 final `ce:code-review mode:autofix`。`/simplify` 并行派三个 agent（复用 / 质量 / 效率）扫整个累积 diff 并直接修复：

| Agent | 抓什么 |
|---|---|
| **Agent 1: 复用** | 新写的代码是否有现成 util / helper 可替换；内联手写的字符串/路径处理/类型守卫是否有已有函数 |
| **Agent 2: 质量** | 冗余 state、参数堆砌、复制粘贴微变、泄漏抽象、stringly-typed、无用 JSX 嵌套、无用注释（解释 WHAT 而非 WHY） |
| **Agent 3: 效率** | 重复计算、可并行化的串行 I/O、热路径臃肿、轮询里无变更检测的 no-op 更新、TOCTOU 前置 exists 检查、无界内存、过度读取 |

**调用时机**：

- ✅ 所有 Unit 完成、Phase 4 收尾时（**默认**）
- ✅ 中途某个 Unit 改动量大 / 重构密集 / 引入新抽象时可选插一次
- ❌ 每个 Unit 都跑（太频繁，`ce:work` 已自动每 2-3 Unit 做内置 simplify pass）
- ❌ Phase 5 的 `ce:code-review interactive` 完成后再回头跑（那是总体审查之后，不应回到实现期清理）

**与 `ce:work` 内置 simplify pass 的区别**：

| | ce:work 内置 | 手动 `/simplify` |
|---|---|---|
| 频率 | 每 2-3 Unit 自动 | Phase 4 收尾一次 |
| 扫描范围 | 跨单元去重 | 完整累积 diff 三维（复用/质量/效率） |
| 执行方式 | 单 agent 串行 | 三 agent 并行 |
| 修复策略 | 保守去重 | 直接修 + 跳过 false positive |

`/simplify` 会修改代码，所以其后必须再跑一次 final `ce:code-review mode:autofix`，确保 simplification edits 也经过 Phase 4 自动修复。

### 铁律

- **无失败测试，不写生产代码**
- **无根因分析，不尝试修复**
- **3 次修复失败，停下质疑架构**
- **不主动提交** —— Phase 4 结束时变更可能 staged 或 unstaged，但绝不自动创建 commit；提交在 Phase 6 由用户触发

---

## Phase 5: 验证 -- "质量关"

> 目标：总体审查当前产物，处理需要裁决的问题，并确保代码质量
>
> 路由器：`dev:verify`
>
> 核心产出：总体审查裁决（PASS / NEEDS_WORK）+ gated/manual 裁决 + 残余 todo

### 智能路由：`ce:code-review` 自动组队 + `dev:verify` 自动叠加

```
代码变更
    |
    v
ce:code-review interactive plan:<path> (核心, 多轮循环最多 3 轮)
    |
    |-- 跨模型对抗审查: Claude + Codex 始终并行派发
    |   大 diff (200+ 行) 额外加 Codex 结构化 P1 门控
    |-- Codex 路径下，reviewer-agent / task spawning 可用时
    |   角色审查也应走多 agent fanout；否则才降级为串行 persona passes
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
    +-- diff 涉及 views/components/css   -> ce:test-browser (受影响路由) | `dev-browser`（轻量 stdin 脚本，跨 harness 通用）
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

### Phase 4 vs Phase 5 的 ce:code-review 区别

| | Phase 4 (内嵌) | Phase 5 (完整) |
|---|---|---|
| 模式 | `mode:autofix` | `interactive` |
| 目的 | 实现阶段自动修复 `safe_auto` | 总体审查当前产物，处理 `gated_auto` / `manual` 裁决 |
| 触发 | 每个 batch 后 + `/simplify` 后 final pass | Phase 4 完成后，或用户手动要求审查当前产物 |
| 轮次 | 每次 `mode:autofix` 内部 bounded re-review；可随实现批次多次运行 | 最多 3 轮 interactive 审查/修复/再审 |
| 决策 | 不问用户，不处理 gated/manual | 需要时向用户展示裁决项 |
| 叠加层 | 无 | 按 diff 自动叠加 + 跨模型对抗 + slop-scan |

### 铁律

- **证据先于断言** -- 没跑命令不能说"通过了"
- **验证先于采纳** -- 审查反馈先验证再实现，技术正确性优先于社交礼貌

---

## Phase 5.5: 交付前沉淀 / 自省判断

> 目标：在 commit / PR / merge 之前，判断本次交付是否必须先运行 `dev-learn` 或 `dev-supervise`，让知识与自省证据随同一批代码交付。
>
> 路由器：`dev:flow` 内置判断（按需委托 `dev-learn` / `dev-supervise`）
>
> 核心产出：可能新增 `docs/solutions/`、`docs/supervise/`、wiki ingest 产物，或明确跳过记录

### 为什么在 Phase 6 前

`dev-learn` 和 `dev-supervise` 可能写入仓库内文档。如果先 ship 再沉淀，就会留下未交付的知识 diff，或者迫使用户为了文档再跑一次交付。Phase 5.5 把这个判断前置：需要沉淀/自省就先做，确认无必要就直接进入 Phase 6。

### 智能判定

| 信号 | 动作 |
|---|---|
| 非平凡 bug 已解决、根因明确、有新预防经验 | 运行 `dev-learn` Route A，把问题/根因/修复/预防写入 `docs/solutions/` |
| 交付包含新的架构、调试、部署、AI 工作流模式 | 运行 `dev-learn` Route A/C，把可复用经验写入知识库或 skill |
| 用户明确要求"记下来 / 沉淀 / 写成 skill / 以后都这么做" | 运行 `dev-learn`，按 Route A/C/E/F 分流 |
| diff 修改 `claude-skills/`、`.agents/skills/`、`docs/ai-coding-workflow.md`、`scripts/supervise/`、`docs/supervise/` | 运行 `dev-supervise --scope project --since 7d`；若报告暴露 skill gap，再运行 `dev-learn` Route E |
| session 出现用户打断、回滚、重复返工、L1 iron law 事件，或同类 review 发现反复出现 | 先运行 `dev-supervise` 收集证据，再判断是否需要 `dev-learn` Route E |
| 机械 typo、格式调整、无新决策的锁文件/文档微调，且无自省信号 | 跳过两者，进入 Phase 6 |

当两者都需要时，顺序固定为 **`dev-supervise` -> `dev-learn`**。`dev-supervise` 的报告是 evidence；`dev-learn` 负责把可复用结论转成知识或 skill 改进。

### 验证与回流

- guided / `mode:auto`：信号唯一明确时自动执行；信号明确为无必要时自动跳过；存在取舍时 STOP。
- `mode:manual`：用户明确要求逐步确认时，展示判定结果并等待。
- 任一子步骤产生文件后，至少运行针对性验证（`git status --short`、链接/grep 检查、必要时 docs-only `/dev:verify`），再进入 Phase 6。
- 如果 `dev-supervise` 报告要求修改 `SKILL.md`，回到 Phase 4/5 完成修改和验证；不得带着未处理的 P0/P1 流程问题进入 Phase 6。

## Phase 6: 交付 -- "上线"

> 目标：从代码到生产环境
>
> 路由器：`dev:ship`
>
> 核心产出：PR + 部署 + 合并后自动删除当前工作区

### 智能路由：按项目类型和用户意图自动选路径

```
验证通过且完成 Phase 5.5 交付前判断的代码
  |
  [强制前置: 主干同步]
  git fetch origin main && git rebase origin/main
  |
  +-- [默认] -----------------------------------------> Path A: Squash 合并
  |   squash merge + 中文 commit，保持主干线性干净 -> 自动删除当前 worktree
  |
  +-- [用户显式要求 PR] ------------------------------> Path B: PR 路径
  |   ce:commit-push-pr -> land-and-deploy -> 自动删除当前 worktree
  |
  +-- [用户显式要求 release / bump / deploy] ---------> Path C: gstack 完整
      ship -> document-release -> land-and-deploy -> 自动删除当前 worktree
```

### 自动检测的前置和叠加操作

| 检测到的信号 | 自动动作 |
|---|---|
| 主干落后 >0 commits | **强制 rebase**（不可跳过） |
| PR 有未解决的审查线程 | 先 `resolve-pr-feedback` |
| Diff 涉及 UI 文件 | 并行 `feature-video` (PR 嵌入录屏) |
| 无部署配置文件 (greenfield) | 先 `setup-deploy` 配置部署 |
| 无 Phase 5 review 证据 | STOP，回 `/dev:verify` |

### Phase 6 确认收敛规则

- 用户显式进入 `/dev:ship`，或明确说"提交/commit/push/PR/合并到 main/上线"，就视为**对当前交付路径的整体授权**。
- 不要把授权拆成 commit / push / merge / deploy 多次重复确认；那会把 Phase 6 退化成人工脚本播放器。
- 只有以下情况才再次 GATE：路径存在多个有效选择且无法安全自动判定；merge-readiness / deploy 报告出现 blocker 或风险取舍；用户明确要求逐步确认。
- `dev:flow mode:auto` 进入 Phase 6 时，沿用同一规则：路径唯一且无 blocker 就自动继续；遇到 blocker 再停。

### Path A: Squash 合并回 main（默认路径）

```
主干同步 (git rebase origin/main)
  -> 记录当前 task_worktree / feature_branch / main_worktree
  -> cd main_worktree && git merge --squash <branch>
  -> 若用户已明确要求合并到 main 且无歧义，直接提交
  -> 仅在 commit message / 目标路径 / 风险不明确时 GATE: 展示 diff 摘要 + 拟定中文 commit message
  -> git commit -m "简洁中文描述"
  -> git push origin main
  -> 自动删除当前 task worktree + 本地 feature branch
  [+ feature-video in parallel if UI detected]
```

**为什么默认不创建 PR**：个人项目或小团队场景下，PR 是不必要的仪式。squash 合并保持 main 线性，每个 commit 对应一个完整功能，`git log --oneline` 即是项目演进史。

### Path B: PR 路径（仅在用户显式要求时）

```
/ce:ce:commit-push-pr (ce-pr-description 生成描述 -> 自适应 PR)
  -> land-and-deploy (CI -> merge-readiness 报告 -> 合并 -> 部署 -> 金丝雀)
  -> 自动删除当前 task worktree + 本地 feature branch
```

### Path C: gstack 完整发布路径（仅在用户显式要求 release / bump / deploy 时）

```
ship (合并基准分支 -> 测试 -> 覆盖率审计 60%/80% -> 计划完成度审计
      -> pre-landing review 多轮 -> adversarial review 多轮
      -> VERSION bump -> CHANGELOG 生成 -> 可二分提交)
  -> document-release (交叉引用 diff 同步所有文档)
  -> land-and-deploy (同上)
  -> 自动删除当前 task worktree + 本地 feature branch
```

### `land-and-deploy` 关键设计

- 自动检测部署平台（Fly.io / Vercel / Render / Netlify / Heroku / GitHub Actions）
- 合并前就绪报告（默认保留的单一交付关卡；无 blocker 时不再拆成多次确认）
- 金丝雀验证按 diff 范围分级：docs 跳过、config smoke、backend 控制台、frontend 全量（frontend 优先用 `dev-browser --headless` + Playwright API 脚本验证关键路由 / 表单 / 控制台无 error）
- 每个失败点提供回滚选项

### 合并后工作区自动清理（强制）

代码确认已合入 main 后，`dev-ship` 自动删除当前任务 worktree，不让 `.worktrees/` 下的临时工作区长期滞留。Merge-readiness GATE 必须提前展示将删除的 worktree 路径；合并成功后不再二次确认。

安全顺序:
1. 离开当前 worktree 前先记录:
   ```bash
   feature_branch=$(git branch --show-current)
   task_worktree=$(git rev-parse --show-toplevel)
   main_worktree=$(git worktree list --porcelain | sed -n 's/^worktree //p' | head -n 1)
   ```
2. Path A 在 `git push origin main` 成功后，从 `main_worktree` 执行 `git worktree remove "$task_worktree"`。
3. Path B/C 在 `land-and-deploy` 明确确认 PR 已 merge 到 main 后，从 `main_worktree` 执行同样清理。
4. 清理本地 feature branch。Squash merge 不会让 Git 认为分支已合并，所以只有在 main push/PR merge 成功后才允许 `git branch -D "$feature_branch"`。
5. 若 `task_worktree` 等于 `main_worktree`，或路径不在 `<repo>/.worktrees/` 下，STOP 并报告；禁止删除主 checkout。
6. 删除前运行 `git -C "$task_worktree" status --porcelain`;若过程文件归档产生未提交改动，暂停并报告，不使用 `--force` 删除。

### 过程文件收尾(默认不阻塞)

`land-and-deploy` 完成后、自动删除当前 worktree 前，`dev-ship` 扫描本任务相关的**过程文件**并在状态报告中列出候选。默认不发起额外确认；只有用户明确要求处理过程文件时，才进入归档 / wiki-ingest / 保留分支:

| 目录 | 性质 | 默认动作 |
|---|---|---|
| `docs/brainstorms/` | 过程(R-ID 需求) | 可归档到 `docs/archive/<year>/` |
| `docs/plans/` | 过程(实现 checklist) | 可归档 |
| `docs/superpowers/{specs,plans}/` | 过程(同上) | 可归档 |
| `docs/ideation/` | 过程(点子排序表) | 可归档或直接 `git rm` |
| **`docs/solutions/`** | **沉淀(institutional memory)** | **永远不动** |

四选一:
1. **归档到 `docs/archive/<year>/`(推荐)** —— `git mv` 保留 history,主目录只留在飞文档
2. **走 `/dev:wiki-ingest` 编译进 wiki 后 `git rm` 原文** —— 适合长期项目,信息结构化沉淀
3. **保持原位** —— 文档本身仍有长期参考价值
4. **跳过** —— 用户自行处理

归档/删除的 `git mv` / `git rm` 不由 skill 自动 commit(铁律 7);作为下次 commit 的一部分,仍由用户显式触发。

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
| 受影响路由的回归用例（Phase 5 自动叠加） | `ce:test-browser`（gstack） | 与 ce:code-review 联动产生结构化报告 |
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

**何时不用 dev-browser**：需要与 ce:code-review / gstack 报告管线集成时优先 `ce:test-browser` / `gstack/qa`；纯 MCP 工作流可继续用 Playwright MCP。dev-browser 的优势是**轻量 + 跨 harness + 沙箱安全**，适合作为 Phase 4-6 的默认 UI 验证刀。

---

## Phase 7: 沉淀 -- "学到什么"

> 目标：将经验转化为可复用的组织知识。可在 Phase 5.5 交付前运行（让知识文档随代码一起交付），也可在 Phase 6 后做部署/迭代收尾。
>
> 路由器：`dev:learn`
>
> 核心产出：`docs/solutions/*.md` + `learnings.jsonl` + 可选 `SKILL.md`

### 智能路由：按触发类型分流

```
已验证或已完成的工作
  |
  +-- [问题被解决] ("fixed", "root cause") -> Route A: ce:compound
  |   默认 Full + session history；无歧义时不额外确认
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

### Phase 7 默认决策

`dev:learn` 默认减少交互确认，尤其是 Route A:

- Route A (`ce-compound`)：默认 **Full + session history**，直接执行
- 只有用户明确说"轻量"/"不要查会话历史"，或会话历史检索存在 blocker 时，才改变默认或发起确认
- 不把 token 成本当作默认决策面；用户没要求时，不问"为了省 token 要不要轻量模式"
- 若 Phase 5.5 已完成同一知识沉淀，Phase 6 后的 Phase 7 只处理部署后新增事实、retro、或用户明确要求的补充；不要重复写同一份 solution。

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
Phase 5 (ce:code-review) <-- learnings-researcher 始终启用 -------------------+
所有 gstack 技能 <-- preamble 自动搜索 learnings.jsonl ------------------+
```

**知识不只是被记录 -- 它被编译成结构化知识网，自动注入到未来的发现、规划和审查中。**

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
  learnings.jsonl            -- gstack 自动写下的一行洞察
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
  dev:discover -> status/decision gate -> dev:design -> status/decision gate
      -> dev:plan -> status/decision gate -> dev:code -> status/decision gate
      -> dev:verify -> status/decision gate
      -> pre-ship dev-learn/dev-supervise 判断 -> dev:ship -> GATE
      -> post-ship dev:learn -> 闭环
```

- **智能路由**: 每个阶段内部自动检测场景，选最优技能组合
- **默认模式**: guided auto-advance，阶段通过且下一步唯一明确时自动继续
- **手动模式**: `mode:manual`，只有用户明确要求逐步确认时使用
- **全自动交付模式**: `mode:auto`，阶段通过且无阻塞时自动继续，并授权后续进入 `/dev:ship`
- **主干同步**: 每个 GATE 检测与 main 的偏离度，及时提醒 rebase
- **恢复智能**: 跨会话自动检测中断位置
- **阶段跳过**: 自动检测哪些阶段可跳过

### `dev:flow mode:auto` -- 带场景检测的全自动模式

```
dev:flow mode:auto
  |
  自动检测阶段 -> 自动进入下一阶段
  |
  只有遇到 hard blocker 才 STOP
```

- 保留 `dev:flow` 的场景检测、阶段跳过、恢复智能
- 不在每个 phase GATE 等用户逐步确认
- 仍不绕过硬门禁：工作区前置、测试失败、强制 review gate、merge/deploy 失败等

### `lfg` -- 全自动编排

```
ce:plan -> GATE -> ce:work -> GATE -> ce:code-review(autofix) -> todo-resolve -> ce:test-browser -> feature-video -> DONE
```

- 串行执行，适合明确知道从 Phase 3 开始的场景
- 无场景检测，无阶段跳过

### 何时用哪个

| 场景 | 推荐 |
|---|---|
| 不确定从哪开始 | `dev:flow` |
| 从零开始新功能 | `dev:flow` |
| 跨会话恢复工作 | `dev:flow` |
| 想减少普通阶段确认、只在 blocker/重大取舍时停下 | `dev:flow`（默认） |
| 想授权一路推进到交付 | `dev:flow mode:auto` |
| 有明确计划，一键执行 | `lfg` |
| 已有需求，快速走完 plan->ship | `lfg` |

---

## 七条铁律（贯穿全流程）

| # | 铁律 | 守护技能 |
|---|---|---|
| 1 | **设计先于实现** -- 需求文档批准前不碰代码 | brainstorming, ce:brainstorm |
| 2 | **测试先于代码** -- 无失败测试不写生产代码 | test-driven-development |
| 3 | **根因先于修复** -- 不理解为什么坏就不能修 | systematic-debugging, investigate, **Bug Fix 快速路径 Step 2** |
| 4 | **证据先于断言** -- 没跑命令不能说"通过了" | verification-before-completion |
| 5 | **验证先于采纳** -- 审查反馈先验证再实现 | receiving-code-review |
| 6 | **工作区先于工作** -- 创建任何文档或代码前必须在任务专属 worktree / feature branch 中，否则先创建工作区 | dev:flow Signal 0, compound-engineering:ce-worktree, superpowers:using-git-worktrees |
| 7 | **提交由用户触发** -- AI 在 Phase 1-5 只修改文件、运行测试，不主动 `git commit` / `git push` / 创建 PR；提交仅在用户显式调用 `/dev:ship` 或说"提交/commit/push/PR"时进行 | dev:ship, ce:ce:commit-push-pr, gstack-ship |

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

Phase 1 特例：Route C/Deep 或高风险需求的 `ce-doc-review` 是进入 Phase 3 前的强制门禁；若仍有未处理 P0/P1，只能阻塞或记录用户 override，不能直接宣布 requirements 批准。

Phase 3 特例：`ce-doc-review` 和选中的计划审查层是进入 Phase 4 前的强制门禁；若仍有未处理 P0/P1，只能阻塞或记录用户 override，不能直接宣布计划已审查通过。

---

## 文档追溯链（贯穿全流程）

```
Phase 1            Phase 2            Phase 3            Phase 4         Phase 5         Phase 5.5       Phase 6
需求文档            DESIGN.md          实施计划            ce:work         ce:code-review  pre-ship learn   交付
R1,R2,R3 -------> Token/色值 -------> Req Trace -------> 实现代码 -----> R-ID 验证 ----> docs/solutions -> PR
                                       Impl Units         增量提交        safe_auto       docs/supervise    部署
                                       Test Scenarios                     修复           skill evidence
                                                                                                           |
                                                                                                      Phase 7
                                                                                                      post-ship closeout
                                                                                                           |
Phase 3 (ce:plan) <-- learnings-researcher 自动搜索 ------------------------------------------------------+

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
