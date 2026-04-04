# Phase 3: 规划 — 最佳技能组合分析

## Phase 3 的技能分类

Phase 3 包含两类技能：**计划创建**和**计划评审**。

### 计划创建（二选一）

| 维度 | `ce:plan` (CE) | `writing-plans` (SP) |
|---|---|---|
| **设计哲学** | 计划 = **决策**，实现者自行编写代码 | 计划 = **代码**，实现者机械跟随步骤 |
| **假设实现者** | 有能力的 AI Agent (ce:work) | 零上下文的工程师 |
| **步骤粒度** | 实施单元（一个原子提交的工作量） | 微步骤（2-5 分钟：写测试->运行->实现->运行->提交） |
| **代码内容** | 不含代码，含方向性伪代码/图表 | **每步含完整代码**，无占位符 |
| **研究能力** | 并行子 Agent（repo-research, learnings, best-practices, framework-docs） | 无 |
| **需求追溯** | **Requirements Trace (R1, R2...)** 回链到需求文档 | 无 |
| **测试设计** | 枚举测试场景（输入->预期结果），不预写代码 | 预写完整测试代码 |
| **范围分级** | Lightweight / Standard / Deep | 无 |
| **问题管理** | Resolved During Planning / Deferred to Implementation | 无 |
| **深化机制** | Confidence Check + 子 Agent gap 分析 | Self-Review 清单 |
| **文档审查** | document-review（多人格） | 内联自检 |
| **输出位置** | `docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md` | `docs/superpowers/plans/YYYY-MM-DD-<name>.md` |
| **下游消费者** | `ce:work` (自动选策略执行) | `subagent-driven-development` 或 `executing-plans` |

### 计划评审（四种视角 + 一个编排器）

| 技能 | 视角 | 是否必需 | 核心价值 |
|---|---|---|---|
| `plan-ceo-review` | CEO/创始人 | 推荐 | 质疑前提、Dream State、10 维度审查（架构->安全->性能->部署） |
| `plan-design-review` | 设计师 | 条件(有 UI) | 7 维度评审（信息架构->交互状态->AI Slop->响应式） |
| `plan-eng-review` | 工程经理 | **必需（gate /ship）** | 架构/测试覆盖/性能/故障模式，输出测试计划供 /qa 消费 |
| `plan-devex-review` | DX 专家 | 条件(面向开发者) | 8 维度 DX 评分卡 + TTHW 评估 |
| `autoplan` | 编排器 | 替代手动 | 串联 CEO->Design->Eng->DX，6 原则自动决策 |

---

## 核心洞察：`ce:plan` vs `writing-plans` 是两种范式

```
ce:plan 范式：                           writing-plans 范式：
  计划 = 做什么决策 + 为什么              计划 = 写什么代码 + 怎么运行
  实施单元 -> Agent 自行实现              微步骤 -> 人/Agent 机械执行

  优势：灵活、可维护、有研究支撑            优势：无歧义、可复制、对新手友好
  劣势：依赖实现者的能力                   劣势：需求变更时大量代码重写
```

### 为什么 `ce:plan` 更适合 AI Coding 流程

1. **实现者是 AI Agent（ce:work）**，不需要预写代码 -- 它能从决策+模式+测试场景自行推导实现
2. **需求追溯（R-ID）** 连接 Phase 1 的需求文档，贯穿到 Phase 5 的 ce:review
3. **研究子 Agent** 提供代码库模式分析、历史经验、外部最佳实践 -- writing-plans 完全缺失
4. **深化机制** 允许在信心不足时自动发现 gap 并加强计划
5. **范围分级** 避免小任务过度规划、大任务规划不足
6. **计划可维护** -- 决策不容易过时，预写代码容易过时

### `writing-plans` 的合理场景

当实现者是**人类新手开发者**（非 AI Agent）时，预写完整代码的计划更有价值。但在 AI Coding 流程中，这种详细程度是浪费 -- `ce:work` 不需要被手把手教写代码。

---

## 最佳组合

### 完整路径（推荐）

```
需求文档 (Phase 1)
    |
    v
ce:plan (创建计划)
    |
    +--- 并行研究 Agent (repo-research + learnings + best-practices + framework-docs)
    |
    +--- 需求追溯 (R1, R2... 回链需求文档)
    |
    +--- 实施单元 (每个是一个原子提交)
    |
    v
autoplan (一键四视角评审)
    |
    +--- Phase 1: plan-ceo-review (质疑前提、扩展/收缩范围)
    |
    +--- Phase 2: plan-design-review (条件：有 UI，7 维度)
    |
    +--- Phase 3: plan-eng-review (必需：架构/测试/性能/故障)
    |
    +--- Phase 3.5: plan-devex-review (条件：面向开发者，8 维度)
    |
    v
修订后的计划 + GSTACK REVIEW REPORT
```

### 轻量路径（小任务）

```
需求文档 (Phase 1)
    |
    v
ce:plan (Lightweight 模式, 2-4 实施单元)
    |
    v
plan-eng-review (单独跑工程评审，确保可 ship)
    |
    v
修订后的计划
```

### 按场景选择评审深度

| 场景 | 推荐评审 |
|---|---|
| 新产品/大型功能 | `autoplan`（全部四种） |
| 普通功能开发 | `plan-eng-review`（必需）+ `plan-design-review`（有 UI 时） |
| 小修复/重构 | `plan-eng-review`（必需） |
| 开发者工具/SDK | `plan-eng-review` + `plan-devex-review` |
| 战略性架构变更 | `plan-ceo-review` + `plan-eng-review` |

---

## Phase 3 应该输出什么文档？

### 核心输出：`ce:plan` 的计划文档

**`docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`**

```markdown
---
title: feat: Add user authentication
type: feat
status: active
date: 2026-04-04
origin: docs/brainstorms/2026-04-03-user-auth-requirements.md
deepened: 2026-04-04
---

# feat: Add user authentication

## Overview
[变什么、为什么]

## Problem Frame
[用户/业务问题，引用 origin doc]

## Requirements Trace              <-- 回链 Phase 1 的 R-ID
- R1. 新用户可通过邮箱注册
- R2. 已注册用户可通过邮箱+密码登录
- R3. 管理员可以禁用任何普通用户账号

## Scope Boundaries
[明确排除项]

## Context & Research
### Relevant Code and Patterns     <-- 研究 Agent 产出
### Institutional Learnings         <-- docs/solutions/ 中的经验
### External References             <-- 外部最佳实践

## Key Technical Decisions          <-- 决策 + 理由
- 密码哈希使用 argon2: [理由]
- Session 存储使用 Redis: [理由]

## Open Questions
### Resolved During Planning
### Deferred to Implementation

## High-Level Technical Design      <-- 可选：伪代码/图表
> 方向性指导，非实现规格

## Implementation Units             <-- 每个 = 一个原子提交

- [ ] **Unit 1: User model and migration**
  **Goal:** 创建用户表和 model
  **Requirements:** R1, R2
  **Files:** Create: src/models/user.rb, Modify: db/schema.rb
  **Test scenarios:**
  - Happy path: 有效邮箱+密码创建用户 -> 返回用户对象
  - Edge case: 重复邮箱 -> 抛出 UniqueViolation
  - Error path: 空密码 -> 验证失败

- [ ] **Unit 2: Registration endpoint**
  **Goal:** POST /api/register
  **Requirements:** R1
  **Dependencies:** Unit 1
  ...

## System-Wide Impact
## Risks & Dependencies

## GSTACK REVIEW REPORT             <-- 评审技能写入此处
| Review | Runs | Status | Findings |
|--------|------|--------|----------|
| CEO    | 1    | DONE   | 3 fixed  |
| Eng    | 1    | CLEARED| 0 open   |
| Design | 0    | --     | --       |
```

### 为什么是这个格式

| 设计决策 | 理由 |
|---|---|
| **Requirements Trace** | R-ID 从 Phase 1 需求文档流入，贯穿到 Phase 5 的 ce:review |
| **Implementation Units（非微步骤）** | Agent 需要决策和边界，不需要预写代码 |
| **Test scenarios（非预写测试代码）** | 枚举"测什么"，Agent 决定"怎么测" |
| **Open Questions 分级** | 区分规划时可解决 vs 实现时才知道的问题 |
| **GSTACK REVIEW REPORT 就地写入** | 评审结果和计划在同一文件，/ship 读取判断是否可发布 |
| **origin 字段** | 明确链接到 Phase 1 需求文档，可追溯 |
| **status 字段** | `active` -> `completed` 生命周期管理 |

---

## 三阶段文档链路总结

```
Phase 1                    Phase 2                    Phase 3
需求文档                    设计体系                    实施计划
docs/brainstorms/          DESIGN.md                  docs/plans/
*-requirements.md          + approved.json            *-plan.md

  R1, R2, R3...     -->    Token/色值/字体     -->    Requirements Trace: R1, R2
  (追溯锚点)               (设计锚点)                  Implementation Units
  Success Criteria          approved variant            Test Scenarios
  Scope Boundaries                                     GSTACK REVIEW REPORT

      |                        |                        |
      v                        v                        v
  "做什么"                  "长什么样"                "怎么做"
      |                        |                        |
      +------------------------+------------------------+
                               |
                               v
                     Phase 4: ce:work (执行)
```

---

## 一句话结论

**Phase 3 = `ce:plan`（创建决策级计划）+ `autoplan`/`plan-eng-review`（多视角评审）。输出是 `docs/plans/*-plan.md`，包含 Requirements Trace 回链需求、Implementation Units 映射原子提交、Test Scenarios 枚举验证点。`writing-plans` 的"代码级计划"在 AI Coding 流程中不如"决策级计划"有效 -- Agent 需要方向，不需要抄写。**
