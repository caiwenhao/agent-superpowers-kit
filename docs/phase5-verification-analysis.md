# Phase 5: 验证 — 最佳技能组合分析

## Phase 5 的关键洞察：这些技能审查的是不同表面

Phase 5 的技能不是在同一维度上竞争，而是在**不同表面**上互补：

```
                    代码变更 (Diff)
                   /              \
            静态审查               动态验证
           /      \               /       \
     ce:review  gstack/review  test-browser  gstack/qa
     (人格驱动)  (清单+对抗)   (受影响路由)   (全站测试)
                                               |
                                          gstack/qa-only
                                           (仅报告)

              全局审计 (不限于 Diff)
              /        |         \
        gstack/health  gstack/cso  gstack/benchmark
        (代码质量)     (安全态势)    (性能基线)

              实现后视觉审查
                   |
            gstack/design-review
             (视觉QA+修复)

              贯穿原则
                   |
        verification-before-completion
          (证据先于断言)
```

---

## 技能对比

### 代码审查（三种方式）

| 维度 | `ce:review` (CE) | `gstack/review` (gstack) | `requesting-code-review` (SP) |
|---|---|---|---|
| **审查方式** | 20+ 人格 Agent 并行 | 清单 + 专家 Agent + Red Team + Codex 对抗 | 单个审查子 Agent |
| **审查者数量** | 6 始终启用 + 条件启用（自动按 diff 选择） | 固定清单 + 4-8 专家 Agent | 1 个 |
| **置信度过滤** | 有（>=0.60，P0 >=0.50） | 有（1-10 信心分） | 无 |
| **自动修复** | `safe_auto` 类自动修复 | AUTO-FIX 机械问题 | 无 |
| **模式** | interactive / autofix / report-only / headless | 仅 interactive | 仅 report |
| **需求验证** | 从计划文件读 R-ID 逐条检查 | 计划完成度审计 | 从模板中传入需求 |
| **独特能力** | 人格专业化（Rails 专家、前端竞态专家等） | Codex 对抗挑战 + Red Team | 简单直接 |
| **在 lfg/slfg 中** | **是默认审查器** | 不在自动流水线中 | 不在自动流水线中 |
| **代价** | 并行 Agent 调用（haiku 模型降低成本） | 多轮 Agent + Codex 调用 | 单次 Agent 调用 |

### 运行时验证

| 维度 | `test-browser` (CE) | `gstack/qa` | `gstack/qa-only` |
|---|---|---|---|
| **范围** | **仅 PR 受影响的路由** | 全站（5-15 页） | 全站（仅报告） |
| **修复能力** | 提供选项（修复/todo/跳过） | **自动修复 + 原子提交** | 不修复 |
| **路由映射** | 从 diff 文件自动推断路由 | 手动探索 | 手动探索 |
| **健康评分** | 无 | 加权复合评分（控制台/链接/视觉/功能/UX/性能/可访问性） | 同 qa |
| **在 lfg/slfg 中** | **是**（与 review 并行） | 手动触发 | 手动触发 |

### 全局审计

| 技能 | 审查什么 | 何时用 |
|---|---|---|
| `gstack/health` | 类型检查/Lint/测试/死代码 -> 0-10 评分 + 趋势 | 了解代码库基线质量 |
| `gstack/cso` | 密钥泄露/供应链/CI 安全/OWASP/STRIDE | 上线前安全审计 |
| `gstack/benchmark` | Core Web Vitals + 资源大小 + 回归检测 | 性能敏感变更 |
| `gstack/design-review` | 视觉一致性/间距/层级/AI Slop + 自动修复 | UI 变更后 |
| `gstack/devex-review` | 文档/上手流程/TTHW 实测 | 面向开发者的产品 |

---

## `ce:review` 为什么是核心

### 1. 人格专业化 — 不同问题由不同专家发现

```
ce:review 按 diff 内容自动组建审查团队：

始终启用（6 个）:
  correctness-reviewer     — 逻辑错误、边界条件、状态 bug
  testing-reviewer         — 覆盖缺口、弱断言、脆弱测试
  maintainability-reviewer — 耦合、复杂度、命名、死代码
  project-standards        — CLAUDE.md/AGENTS.md 合规
  agent-native-reviewer    — 新功能是否 Agent 可用
  learnings-researcher     — 搜索 docs/solutions/ 的历史经验

条件启用（按 diff 触发）:
  security-reviewer        — diff 触及 auth/公开端点/用户输入
  performance-reviewer     — diff 触及 DB 查询/缓存/异步
  api-contract-reviewer    — diff 触及路由/序列化/类型签名
  data-migrations-reviewer — diff 触及 migration/schema
  reliability-reviewer     — diff 触及错误处理/重试/超时
  adversarial-reviewer     — diff >=50 行 或 触及 auth/支付/数据
  kieran-rails-reviewer    — diff 触及 Rails 代码
  kieran-python-reviewer   — diff 触及 Python 代码
  kieran-typescript-reviewer — diff 触及 TypeScript 代码
  julik-frontend-races     — diff 触及 Stimulus/Turbo/async UI
  ...
```

**一个 config 改动 = 6 个审查者。一个 Rails 支付功能 = 12+ 个审查者。** 自动右倾。

### 2. 四种模式适配不同场景

| 模式 | 用途 | 谁调用 |
|---|---|---|
| `interactive` | 默认，人工逐项审批 | 开发者手动 |
| `autofix` | 自动修复 safe_auto，残余写入 todo | ce:work (Phase 3) |
| `report-only` | 只读，可与浏览器测试并行 | slfg (并行阶段) |
| `headless` | 程序化调用，返回结构化数据 | ce:brainstorm 的 document-review |

### 3. 需求追溯验证

```
ce:review Stage 2b:
  1. 从 plan: 参数、PR body、或自动发现找到计划文件
  2. 读取 Requirements Trace (R1, R2, R3...)
  3. 在 Stage 6 合成时检查每个 R-ID 是否被代码覆盖
  4. 输出: "R3 未被任何代码覆盖" 或 "所有需求已满足"
```

**这是从 Phase 1 需求文档 -> Phase 3 计划 -> Phase 5 审查的完整追溯闭环。**

### 4. 与 `ce:work` 的紧密集成

```
ce:work Phase 3:
  默认: ce:review mode:autofix plan:<path>
    -> safe_auto 自动修复
    -> 残余 -> todo-create -> todo-triage -> todo-resolve
    -> 然后 git-commit-push-pr

slfg 并行阶段:
  同时运行: ce:review mode:report-only + test-browser
    -> 并行读，不冲突
  然后: ce:review mode:autofix
    -> 串行写，安全修复
```

---

## `gstack/review` vs `ce:review` — 互补还是重复？

| 维度 | `ce:review` | `gstack/review` |
|---|---|---|
| 核心方法 | 人格 Agent（模拟不同类型的审查者） | 清单 + 专家 Agent + 对抗测试 |
| 安全审查 | security-reviewer (条件启用) | 专门的安全清单 + Red Team |
| 对抗测试 | adversarial-reviewer (>=50 行) | Red Team + Codex 对抗 + Claude 对抗 |
| 计划合规 | Requirements Trace 验证 | 计划完成度审计 + 范围漂移检测 |
| SQL 安全 | data-migrations-reviewer | 专门的 SQL/数据安全清单 |
| LLM 信任边界 | 无专门审查 | **有专门检查** |
| 竞态条件 | julik-frontend-races (前端) | **有专门检查（后端+前端）** |

**结论：大多数场景 `ce:review` 已足够。但 `gstack/review` 在以下场景提供额外价值：**
- LLM 输出信任边界（ce:review 没有专门审查）
- 后端竞态条件（ce:review 只有前端竞态专家）
- Codex 对抗挑战（独立 AI 模型的第二意见）

---

## `verification-before-completion` — 贯穿一切的铁律

这不是一个在特定时点运行的技能，而是一个**始终激活的纪律**：

```
铁律: 没有运行验证命令 = 不能声称通过

  "测试通过了"    -> 必须有测试输出: 0 failures
  "构建成功了"    -> 必须有构建输出: exit 0
  "Bug 修复了"    -> 必须运行原始症状测试
  "需求满足了"    -> 必须逐条对照计划清单
  "Agent 完成了"  -> 必须检查 VCS diff
```

**这条铁律应该内嵌到 `ce:work` 和 `ce:review` 的每次完成声明中，而不是作为独立技能调用。**

---

## 最佳组合

### 核心流程（每次变更必须）

```
代码变更完成
    |
    v
ce:review mode:autofix plan:<path>        <-- 必须：代码质量
    |                                          20+ 人格并行审查
    |                                          safe_auto 自动修复
    |                                          R-ID 需求追溯验证
    |
    +-- 残余问题 -> todo-create -> todo-resolve
    |
    v
verification-before-completion            <-- 贯穿：证据先于断言
    |                                          测试输出、构建输出、需求清单
    v
git-commit-push-pr                        <-- 交付
```

### 按场景叠加

| 场景 | 核心 | 叠加 |
|---|---|---|
| 普通功能 | `ce:review` | -- |
| 有 UI 的功能 | `ce:review` | + `test-browser`（受影响路由） |
| 大型 UI 功能 | `ce:review` | + `gstack/qa`（全站测试+修复）+ `design-review`（视觉QA） |
| 涉及安全/支付 | `ce:review` | + `gstack/cso`（全面安全审计） |
| 涉及 LLM/AI | `ce:review` | + `gstack/review`（LLM 信任边界检查） |
| 性能敏感 | `ce:review` | + `gstack/benchmark`（性能基线对比） |
| 上线前总检 | `ce:review` | + `gstack/health`（代码库基线）+ `gstack/cso`（安全） |
| 开发者工具 | `ce:review` | + `gstack/devex-review`（DX 实测） |

### 在 lfg/slfg 中的自动编排

```
lfg（串行）:
  ce:work -> ce:review(autofix) -> todo-resolve -> test-browser -> feature-video

slfg（并行优化）:
  ce:work(swarm) -> +-- ce:review(report-only) --+  -> ce:review(autofix) -> todo-resolve
                    +-- test-browser -------------+
                        (并行读，不冲突)               (串行写，安全修复)
```

---

## Phase 5 的输出不是文档，是裁决

Phase 1-4 每个阶段产出一个核心文档。Phase 5 不同 — 它产出的是**裁决 + 残余工作项**：

| 输出 | 位置 | 内容 |
|---|---|---|
| 审查裁决 | ce:review 合成报告 | PASS / PASS_WITH_NOTES / NEEDS_WORK |
| 自动修复 | 代码库（原地修改） | safe_auto 类问题已修复 |
| 残余工作项 | `.context/compound-engineering/todos/` | 未自动修复的 gated_auto/manual 问题 |
| 审查记录 | `.context/compound-engineering/ce-review/<run-id>/` | 完整审查过程记录 |
| QA 报告 | `.gstack/qa-reports/` | 健康评分 + 截图 + 复现步骤 |
| 安全报告 | `.gstack/security-reports/` | OWASP/STRIDE 审计结果 |

---

## 五阶段链路总结

```
Phase 1          Phase 2          Phase 3          Phase 4          Phase 5
需求文档          DESIGN.md        实施计划          ce:work          ce:review
R1,R2,R3    -->  Token/色值  -->  Req Trace  -->  实现代码    -->  审查裁决
                                  Impl Units      增量提交          |
                                  Test Scenarios                     +-- R-ID 追溯验证
                                                                    |   "R3 未被覆盖"
                                                                    |
                                                                    +-- safe_auto 修复
                                                                    |
                                                                    +-- 残余 -> todo
                                                                    |
                                                                    v
                                                              git-commit-push-pr
```

---

## 一句话结论

**Phase 5 = `ce:review`（必须）+ `verification-before-completion`（纪律）+ 按场景叠加专项审计。`ce:review` 是唯一必须的审查器：20+ 人格自动组队、R-ID 需求追溯、四种模式适配不同调用场景。`gstack/review` 在 LLM 信任边界和后端竞态有补充价值。`test-browser` 是最佳运行时验证（精准覆盖受影响路由）。`gstack/qa` 用于全站测试。全局审计（health/cso/benchmark）按需叠加，不替代 `ce:review`。**
