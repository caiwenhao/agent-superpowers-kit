# Phase 4: 实现 — 最佳技能组合分析

## Phase 4 的技能分类

### 三个执行引擎（核心对比）

| 维度 | `ce:work` (CE) | `subagent-driven-development` (SP) | `executing-plans` (SP) |
|---|---|---|---|
| **设计哲学** | 智能调度 — 自动选最佳策略 | 严格纪律 — 每任务必经双审查 | 简单执行 — 跟着计划一步步做 |
| **策略选择** | **自动**：内联/串行 Agent/并行 Agent/Swarm | 固定：每任务一个子 Agent | 固定：单会话内联 |
| **计划解读** | 计划 = **决策文档**（自行推导实现） | 计划 = **任务脚本**（逐步执行） | 计划 = **指令手册**（完全遵循） |
| **裸提示支持** | 有（自动评估复杂度路由） | 无（必须有计划文档） | 无（必须有计划文档） |
| **每任务审查** | 无（审查在最后统一做） | **有：规格符合 -> 代码质量** 双阶段 | 无 |
| **最终审查** | `ce:review mode:autofix`（**强制**） | 全量代码审查子 Agent | `finishing-a-development-branch` |
| **测试策略** | Test Discovery + System-Wide Test Check | 子 Agent 使用 TDD skill | 跟随计划步骤 |
| **跨单元优化** | Simplify 通道（去重/提取公共） | 无（每个 Agent 上下文隔离） | 无 |
| **模型选择** | 由策略决定 | **按任务复杂度选模型**（便宜/标准/最强） |  单一模型 |
| **Swarm 支持** | 有（Agent Teams 模式） | 无（串行） | 无 |
| **适配 `ce:plan` 输出** | **完美**（读 Implementation Units, R-ID, Test Scenarios） | 需要转换（期望步骤式任务） | 需要转换 |
| **在 lfg/slfg 中** | **是默认执行器** | 不在自动流水线中 | 不在自动流水线中 |

### 辅助技能

| 技能 | 来源 | 角色 | 何时介入 |
|---|---|---|---|
| `test-driven-development` | SP | RED->GREEN->REFACTOR 强制循环 | 计划标注 `Execution note: test-first` 时 |
| `systematic-debugging` | SP | 四阶段根因分析 | 遇到 bug 时 |
| `gstack/investigate` | gstack | 四阶段调试（相同方法论） | 遇到 bug 时 |
| `ce:reproduce-bug` | CE | 从 GitHub Issue 系统化复现 | Bug 修复任务 |
| `dispatching-parallel-agents` | SP | 并行派发独立任务 | 多个互不依赖的失败/任务 |
| `using-git-worktrees` | SP | 工作区隔离 | 开始实现前 |
| `orchestrating-swarms` | CE | 多 Agent 协同模式参考 | ce:work 的 Swarm 模式 |
| `frontend-design` | CE | UI 实现时的设计指导 | 涉及前端组件时自动启用 |

### 自动化编排器

| 编排器 | 执行方式 | 流程 |
|---|---|---|
| `lfg` | 串行 | ce:plan -> **ce:work** -> ce:review(autofix) -> todo-resolve -> test-browser -> feature-video |
| `slfg` | 并行 | ce:plan -> **ce:work(swarm)** -> [ce:review(report) + test-browser] 并行 -> ce:review(autofix) -> todo-resolve |

---

## 核心洞察

### `ce:work` 为什么胜出

**1. 策略自适应 — 一个技能覆盖所有场景**

```
ce:work 接收输入
    |
    +-- 裸提示 "修个 typo"
    |     +-- 评估: Trivial (1-2 files)
    |     +-- 直接实现，无任务列表
    |
    +-- 裸提示 "加个登录功能"
    |     +-- 评估: Large (跨领域, 10+ files)
    |     +-- 建议先跑 ce:brainstorm + ce:plan
    |
    +-- 计划文档 (3 个实施单元，有依赖)
    |     +-- 评估: Serial subagents
    |     +-- 每单元一个 Agent，按依赖序执行
    |
    +-- 计划文档 (5 个实施单元，3 个独立)
    |     +-- 评估: Parallel subagents
    |     +-- 独立单元并行，依赖单元串行
    |
    +-- 计划文档 (10+ 单元，需要 Agent 间协调)
          +-- 评估: Swarm (Agent Teams)
          +-- 专门角色（实现者/测试者/审查者）持久协作
```

**`subagent-driven-development` 只能串行，`executing-plans` 只能内联。ce:work 自动选最优策略。**

**2. 与 `ce:plan` 输出完美衔接**

`ce:plan` 输出的计划包含：
- Implementation Units（不是微步骤）
- Test Scenarios（枚举场景，不是预写代码）
- Execution Notes（test-first / characterization-first 信号）
- Patterns to Follow（现有代码引用）
- Verification（完成判据）
- Deferred to Implementation（需要实现时解决的问题）

`ce:work` 逐项读取这些字段：
- 从 Implementation Units 创建任务列表
- 从 Test Scenarios 推导测试（并补充遗漏类别）
- 从 Execution Notes 决定执行姿态（TDD / 特征化优先）
- 从 Patterns to Follow 找到要模仿的现有代码
- 从 Verification 确认每单元的完成信号
- 从 Deferred to Implementation 提前了解需要解决的问题

`subagent-driven-development` 期望的是步骤式计划（`writing-plans` 的输出），与 `ce:plan` 的决策式输出不匹配。

**3. System-Wide Test Check — 子 Agent 看不到的全局视角**

```
ce:work 在每个任务完成后检查：
  "这段代码触发了什么？"     — 回调、中间件、观察者，追溯两层
  "测试是否覆盖了真实链路？" — 不是全 mock 的隔离测试
  "失败能否留下孤立状态？"   — DB 写入后外部调用失败的场景
  "其他接口也需要改吗？"     — 混入、DSL、替代入口点
  "错误策略是否跨层一致？"   — 重试+回退+框架错误处理是否冲突
```

这是 `subagent-driven-development` 的子 Agent 无法做到的 — 每个子 Agent 只看到自己的任务上下文，看不到跨任务的系统性影响。

**4. Simplify 通道 — 防止子 Agent 盲区**

子 Agent 各自实现时容易产生跨单元重复代码。`ce:work` 每 2-3 个单元后做一次 Simplify：合并重复模式、提取公共 helper、改善代码复用。

**5. 强制 ce:review 集成**

```
ce:work Phase 3:
  Tier 2 (默认): ce:review mode:autofix plan:<path>
    -> 多人格并行审查（正确性/测试/可维护性/安全/性能...）
    -> 自动修复 safe_auto 问题
    -> 残余问题写入 todo

  Tier 1 (仅限): 纯新增 + 单一关注点 + 模式跟随 + 忠于计划
    -> 内联自检
```

`subagent-driven-development` 的双阶段审查（规格->质量）虽然在每任务后执行，但审查者是新生成的子 Agent，没有 `ce:review` 的多人格专家系统（correctness-reviewer, testing-reviewer, security-reviewer 等 20+ 审查者）。

---

## `subagent-driven-development` 的一个优势

**Per-task spec compliance review** — 每任务完成后立即验证是否符合规格，在偏离早期就纠正。

`ce:work` 将审查推迟到最后（Phase 3），如果第一个单元就偏离了规格，后续单元可能在错误基础上继续建造。

**但 `ce:work` 通过其他机制缓解了这个风险：**
- 每个单元有 Verification 字段作为完成判据
- Requirements Trace 在最终验证时逐条检查
- Incremental commits 允许回滚单个单元
- 对大型计划，可以选择 Serial subagents 策略，在每个子 Agent 完成后检查结果

---

## 最佳组合

### 推荐流程

```
计划文档 (Phase 3)
    |
    v
ce:work (Phase 4 唯一执行入口)
    |
    +-- Phase 0: 输入分诊
    |     Trivial -> 直接实现
    |     Small/Medium -> 创建任务列表
    |     Large -> 建议先 ce:plan
    |
    +-- Phase 1: 快速启动
    |     读计划 -> 设置环境 (worktree/branch) -> 创建任务 -> 选策略
    |
    +-- Phase 2: 执行循环
    |     每任务: 实现 -> Test Discovery -> System-Wide Check -> 增量提交
    |     每 2-3 单元: Simplify 通道
    |
    +-- Phase 3: 质量检查
    |     测试全通过 -> Lint -> ce:review mode:autofix -> 操作验证计划
    |
    +-- Phase 4: 交付
          截图(UI) -> git-commit-push-pr -> 更新计划 status: completed
```

### 辅助技能的介入时机

```
ce:work 执行循环中:
    |
    +-- 遇到 Bug?
    |     systematic-debugging / investigate (四阶段根因)
    |
    +-- 实施单元标注 test-first?
    |     test-driven-development (RED->GREEN->REFACTOR)
    |
    +-- 多个独立���败?
    |     dispatching-parallel-agents (并行诊断)
    |
    +-- 涉及前端 UI?
    |     frontend-design (检测设计体系，指导实现)
    |
    +-- GitHub Issue 中的 Bug?
          reproduce-bug (系统化复现)
```

### 按场景选择执行策略

| 场景 | ce:work 自动选择的策略 | 理由 |
|---|---|---|
| 修个 typo | Inline (Trivial) | 1 文件，无行为变更 |
| 加个 API endpoint | Inline / Serial | 2-3 文件，有依赖 |
| 新功能 (5 单元) | Serial subagents | 有依赖链，需要按序执行 |
| 新功能 (5 单元，3 个独立) | Parallel + Serial | 独立单元并行，加速 |
| 大型重构 (10+ 单元) | Swarm (Agent Teams) | 需要 Agent 间协调 |
| 裸提示 "做个按钮" | Inline (Small) | 裸提示默认内联 |

---

## `executing-plans` (SP) 的定位

`executing-plans` 自己都说：

> "Tell your human partner that Superpowers works much better with access to subagents. If subagents are available, use superpowers:subagent-driven-development instead of this skill."

它是**没有子 Agent 能力时的降级方案**。在 Claude Code 等有子 Agent 支持的环境中，没有使用它的理由。

---

## 四阶段文档链路

```
Phase 1          Phase 2          Phase 3          Phase 4
需求文档          DESIGN.md        实施计划          ce:work 执行
R1, R2, R3  -->  Token/色值  -->  Req Trace  -->  每单元读取:
                                  Impl Units       - Goal
                                  Test Scenarios    - Files
                                  Exec Notes        - Test Scenarios
                                  Verification      - Patterns
                                                    - Verification
                                                         |
                                                         v
                                                   ce:review (Phase 5)
                                                   "R3 未被任何代码覆盖"
```

---

## 一句话结论

**Phase 4 = `ce:work` 作为唯一执行入口。它自动选择最佳策略（内联/串行/并行/Swarm），完美消费 `ce:plan` 的决策式输出，System-Wide Test Check 提供子 Agent 看不到的全局视角，强制 `ce:review` 确保质量。`subagent-driven-development` 的 per-task 双审查虽有价值，但 `ce:work` 的策略自适应 + 全局测试检查 + 多人格最终审查是更优组合。`executing-plans` 是无子 Agent 时的降级方案。**
