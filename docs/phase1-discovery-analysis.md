# Phase 1: 发现 — 最佳技能组合分析

## Phase 1 四个技能的本质差异

| 维度 | `ce:ideate` | `office-hours` | `ce:brainstorm` | `SP/brainstorming` |
|---|---|---|---|---|
| **解决的问题** | 不知道做什么 | 这个想法值得做吗 | 到底做成什么样 | 技术上怎么设计 |
| **方法论** | 发散->对抗性过滤->排名 | YC 六问诊断 / Builder 头脑风暴 | 协作对话->需求文档 | 对话->设计文档 |
| **输出物** | `docs/ideation/*.md` (排名创意) | `~/.gstack/projects/*/design-*.md` (设计文档) | `docs/brainstorms/*-requirements.md` (需求文档) | `docs/superpowers/specs/*-design.md` (设计规格) |
| **输出包含实现细节?** | 不包含 | 包含方案选择 | **明确排除** | 包含架构/组件/数据流 |
| **需求 ID** | 无 | 无 | **有 (R1, R2, R3...)** | 无 |
| **下游衔接** | -> `ce:brainstorm` | -> `plan-ceo/eng/design-review` | -> **`ce:plan`** | -> `writing-plans` |
| **范围评估** | 通过 focus hint | 通过产品阶段路由 | **Lightweight/Standard/Deep 三级** | 通过对话自适应 |
| **文档审查** | 无 | Spec Review Loop (子 Agent 对抗审查) | **document-review (多人格)** | Spec Self-Review (内联检查) |
| **独特价值** | 并行多视角发散 + Issue 分析 | 需求验证 + 竞品调研 + 跨模型二审 | 阻塞问题分级 + 需求可追溯性 | Visual Companion + HARD-GATE |

---

## 核心洞察：它们是四个不同阶段，不是四个可替换选项

```
"不知道做什么"          "值不值得做"           "到底做成什么"          "怎么做"
     |                     |                     |                   |
  ce:ideate          office-hours          ce:brainstorm         ce:plan
  (创意发散)           (需求验证)             (需求定义)           (实施规划)
     |                     |                     |                   |
     v                     v                     v                   v
  排名创意 ----------> 验证后的方向 ----------> 需求文档 (R1,R2...) --> 实施计划
```

**`SP/brainstorming` 的问题**：它在发现阶段就引入了架构/组件/数据流等实现细节，违反了 `ce:brainstorm` 的核心原则 -- "WHAT 和 WHY 在这里解决，HOW 留给规划"。混合导致：

- 需求变更时设计也要重写
- 规划阶段不能自由选择实现方案
- 文档职责不清

---

## 最佳组合：按场景路由

```
用户输入
  |
  |-- "不知道做什么" / "给我些想法"
  |     +-- ce:ideate -> ce:brainstorm -> ce:plan
  |
  |-- "我有个产品想法" / "这值得做吗"
  |     +-- office-hours -> ce:brainstorm -> ce:plan
  |
  |-- "我要给现有产品加功能"（模糊）
  |     +-- ce:brainstorm (Standard/Deep) -> ce:plan
  |
  +-- "帮我做这个具体的事"（清晰）
        +-- ce:brainstorm (Lightweight，可能跳过文档) -> ce:plan 或 ce:work
```

**`SP/brainstorming` 不在推荐链中**，但它的两个独特能力应该被吸收：

- **Visual Companion**（UI 相关需求时浏览器可视化）-> 应集成到 `ce:brainstorm`
- **HARD-GATE 机制**（强制禁止提前实现）-> `ce:brainstorm` 已有此原则但没有 HARD-GATE 标签

---

## 统一输出文档：`ce:brainstorm` 的需求文档

**推荐使用 `ce:brainstorm` 的输出格式作为 Phase 1 的标准产出**，理由：

### 1. 需求可追溯性

```markdown
## Requirements

**用户管理**
- R1. 新用户可通过邮箱注册
- R2. 已注册用户可通过邮箱+密码登录

**权限控制**
- R3. 管理员可以禁用任何普通用户账号
```

下游 `ce:plan` 的每个实施单元直接引用 R1、R2、R3；`ce:review` 校验每个需求是否被覆盖。**这是贯穿全流程的追溯锚点**。

### 2. 阻塞问题分级（独有且关键）

```markdown
## Outstanding Questions

### Resolve Before Planning
- [Affects R1][User decision] 是否支持第三方 OAuth 登录？

### Deferred to Planning
- [Affects R2][Technical] 密码哈希算法选择（bcrypt vs argon2）
- [Affects R3][Needs research] 现有 RBAC 库的适用性
```

**不是所有问题都需要在发现阶段解决。** 技术问题归规划、产品问题归需求 -- 这个分级防止了两种常见浪费：

- 在需求阶段纠结技术细节
- 把未决的产品问题带入规划阶段

### 3. 完整的文档模板

```markdown
---
date: 2026-04-04
topic: user-authentication
---

# User Authentication

## Problem Frame
[谁受影响、什么在变、为什么重要]

## Requirements
[带稳定 ID 的分组需求，R1/R2/R3...]

## Success Criteria
[如何判断问题被正确解决]

## Scope Boundaries
[明确排除项]

## Key Decisions
[决策 + 理由]

## Dependencies / Assumptions

## Outstanding Questions
### Resolve Before Planning
### Deferred to Planning

## Next Steps
-> /ce:plan
```

### 4. 与下游的衔接最紧密

| 下游技能 | 如何使用需求文档 |
|---|---|
| `ce:plan` | 每个实施单元标注对应的 R-ID |
| `ce:review` | 检查需求完整性（"R3 未被任何代码覆盖"）|
| `ce:work` | 作为验收标准 |
| `document-review` | 多人格审查文档质量 |

---

## 对比：如果用其他格式作为输出

| 输出格式 | 优势 | 劣势 |
|---|---|---|
| `ce:brainstorm` 需求文档 | R-ID 追溯、阻塞分级、无实现泄漏、document-review | 不含架构设计 |
| `SP/brainstorming` 设计文档 | 含架构/组件/数据流、Visual Companion | 实现泄漏、无 R-ID、无阻塞分级、下游 `writing-plans` 而非 `ce:plan` |
| `office-hours` 设计文档 | 需求验证、竞品分析、创始人信号 | 产品验证文档不等于需求文档、无 R-ID |
| `ce:ideate` 创意排名 | 多视角发散 | 太粗粒度，不是需求 |

---

## 结论

**最佳 Phase 1 组合 = 按场景路由入口 + 统一汇聚到 `ce:brainstorm` 输出需求文��**

```
                ce:ideate ----------+
                                   |
         office-hours -------------+---> ce:brainstorm ---> docs/brainstorms/*-requirements.md
                                   |         |
         用户直接描述需求 ----------+    document-review
                                        (多人格审查)
```

- **`ce:ideate`** 提供"做什么"的候选集
- **`office-hours`** 验证"值不值得做"
- **`ce:brainstorm`** 是**唯一的需求定义出口**，输出带 R-ID 的需求文档
- **`SP/brainstorming`** 的 Visual Companion 和 HARD-GATE 应被纳入 `ce:brainstorm`，但其"设计文档"格式不应作为 Phase 1 产出

**一句话：Phase 1 的产出是需求文档（WHAT），不是设计文档（HOW）。实现细节属于 Phase 3。**
