# Phase 2: 设计 — 最佳技能组合分析

## Phase 2 六个技能的本质差异

| 维度 | `design-consultation` | `design-shotgun` | `plan-design-review` | `design-html` | `design-review` | `frontend-design` (CE) |
|---|---|---|---|---|---|---|
| **解决的问题** | 没有设计体系 | 不知道长什么样 | 计划里缺���计决策 | 设计稿变成代码 | 实现后的视觉质量 | 做功能时顺便做好设计 |
| **阶段** | 设计体系创建 | 视觉探索 | 计划评审(设计视角) | 设计->代码 | 实现后审查 | 实现中的设计指导 |
| **输入** | 代码库 + 产品上下文 | DESIGN.md + 功能描述 | 计划文件 + DESIGN.md | approved.json + 设计稿 | 线上 URL + DESIGN.md | 代码库信号 + 任务描述 |
| **核心输出** | **`DESIGN.md`** | `approved.json` + 变体图片 | 修订后的计划文件 | `finalized.html` | 审计报告 + 原子提交修复 | 实现的前端代码 |
| **产出位置** | 仓库根目录 | `~/.gstack/projects/*/designs/` | 计划文件(就地修改) | `~/.gstack/projects/*/designs/` | `~/.gstack/projects/*/designs/` | 项目代码库内 |
| **是否修改代码** | 否(仅写 DESIGN.md) | 否 | 否(修改计划文档) | 否(生成独立 HTML) | **是(原子提交修复)** | **是(写前端代码)** |
| **独特能力** | 竞品研究 + 完整设计系统 | AI 多变体生成 + 对比面板 | 7 维度逐项评审 | Pretext 精确文本布局 | 截图证据 + 逐项修复 | 零依赖、内置于 ce:work |

---

## 核心洞察：这是一条流水线，不是可替换选项

```
design-consultation -----> design-shotgun -----> plan-design-review -----> design-html -----> design-review
  "建立设计语言"            "探索视觉方案"        "计划里补设计决策"        "设计变代码"         "实现后视觉QA"
       |                        |                       |                      |                    |
       v                        v                       v                      v                    v
   DESIGN.md              approved.json           修订后的计划           finalized.html          审计报告
  (设计体系)              (选定的变体)           (含设计决策)           (生产级HTML)         + 原子修复提交
```

**每个技能有明确的前置条件和输出物，上游的输出是下游的输入。**

`frontend-design` (CE) 是这条流水线的**轻量替代品** -- 它在一个技能内完成"检测->计划->实现->验证"，适合在 `ce:work` 执行期间的组件级工作。

---

## 关键发现：`DESIGN.md` 是全流程的锚点

与 Phase 1 的 `R-ID` 需求追溯类似，Phase 2 的锚点是 **`DESIGN.md`**：

```
                         DESIGN.md (设计体系源文件)
                              |
          +-------------------+-------------------+
          |                   |                   |
    design-shotgun      plan-design-review    design-html
    (约束变体生成)       (校验设计一致性)     (提取 token)
          |                   |                   |
          v                   v                   v
    approved.json         修订后计划          finalized.html
          |                                       |
          +------------------+--------------------+
                             |
                       design-review
                    (偏离 DESIGN.md = 高严重度)
```

**所有技能要么创建 DESIGN.md，要么消费 DESIGN.md，要么根据偏离 DESIGN.md 的程度来判定问题严重性。**

---

## 最佳组合：按项目阶段选择

### 场景 A：新项目，从零开始

```
design-consultation -> design-shotgun -> plan-design-review -> design-html
     (建体系)           (探索方案)          (补设计决策)         (生成HTML)
```

**完整路径。** 先建设计体系，再探索具体页面方案，然后确保计划包含设计决策，最后生成高保真 HTML。

### 场景 B：已有项目，加新功能

```
plan-design-review -> frontend-design (在 ce:work 中自动启用)
   (计划里补设计)       (实现时遵循设计体系)
```

**轻量路径。** 已有 DESIGN.md，不需要重建体系。`frontend-design` 自动检测已有设计系统并遵循。

### 场景 C：实现后发现视觉问题

```
design-review (审查 + 修复)
```

**修复路径。** 直接审查线上站点，逐项修复并原子提交。

### 场景 D：不确定设计方向

```
design-shotgun (独立探索)
```

**探索路径。** 不需要先建完整体系，直接生成多变体对比，收集反馈。

---

## Phase 2 应该输出什么文档？

**两层输出，不是一个文档：**

### 第一层：`DESIGN.md`（设计体系 -- 一次创建，长期维护）

```markdown
# Design System

## Aesthetic Direction
[视觉论点：情绪、材质、能量]

## Typography
- Headlines: [字体名称], [权重], [大小层级]
- Body: [字体名称], [权重], [行高]

## Color Palette
- Primary: [色值] -- [使用场景]
- Accent: [色值] -- [使用场景]
- Surface: [色值层级]
- Semantic: success/warning/error/info

## Spacing Scale
[4px/8px/16px/24px/32px/48px/64px...]

## Layout Patterns
[栅格系统、容器宽度、响应式断点]

## Motion
[入场动画、滚动动画、悬停过渡 -- 具体参数]

## Component Conventions
[圆角、阴影、边框、卡片使用规则]

## Anti-Patterns (AI Slop 黑名单)
- 禁止：紫色渐变、三列图标网格、居中一切、装饰性气泡...

## Decisions Log
| 日期 | 决策 | 理由 | 替代方案 |
|------|------|------|----------|
```

**作用**：所有下游设计工作的约束文件。`design-review` 根据偏离程度判定严重性。`frontend-design` 检测并遵循。`ce:work` 中的 Agent 在写前端代码前必须读取。

### 第二层：`approved.json` + 变体截图（具体页面/屏幕的视觉方案）

```json
{
  "approved_variant": "B",
  "feedback": "更喜欢 B 的留白和排版层次",
  "date": "2026-04-04T10:30:00Z",
  "screen": "dashboard-main",
  "branch": "feat/dashboard"
}
```

**作用**：`design-html` 读取此文件，按选定变体生成生产级 HTML。每个页面/屏幕一个 `approved.json`。

---

## 与 Phase 1 / Phase 3 的衔接

### 上游衔接（来自 Phase 1）

```
Phase 1 需求文档 (docs/brainstorms/*-requirements.md)
    |
    |-- 需求中涉及 UI? --> design-consultation (建体系) 或 design-shotgun (探索方案)
    |
    |-- 纯后端需求? --> 跳过 Phase 2，直接进 Phase 3
```

### 下游衔接（进入 Phase 3）

```
DESIGN.md + approved.json
    |
    +---> ce:plan (实施计划引用 DESIGN.md 中的 token)
    |        |
    |        +---> plan-design-review (7 维度检查计划中的设计决策)
    |
    +---> ce:work 中的 frontend-design (实现时自动检测并遵循)
```

---

## `frontend-design` vs gstack 设计流水线的定位

| 维度 | gstack 设计流水线 | `frontend-design` (CE) |
|---|---|---|
| **覆盖范围** | 从设计体系到视觉 QA 的完整流水线 | 单个组件/功能的设计+实现 |
| **外部依赖** | `$D` 设计二进制、`$B` 浏览器二进制 | 零依赖 |
| **产出** | 独立设计工件（mockup、HTML、审计报告） | 直接写入项目代码 |
| **适用场景** | 新项目设计、大型 UI 重构、设计系统建立 | 功能开发中的日常前端工作 |
| **在 lfg/slfg 中的角色** | 不在自动流水线中（需手动触发） | 被 `ce:work` 自动调用 |

**结论**：两者互补，不冲突。gstack 设计流水线用于**重大设计决策**（建体系、探索方案、审计质量），`frontend-design` 用于**日常实现**（按已有体系写代码）。

---

## 对比总结

| 场景 | 推荐组合 | 输出 |
|---|---|---|
| 新项目，无设计体系 | `design-consultation` -> `design-shotgun` | DESIGN.md + approved.json |
| 有体系，规划新功能 | `plan-design-review` | 修订后的计划(含设计决策) |
| 实现功能中 | `frontend-design`(自动) | 遵循体系的前端代码 |
| 实现后质量检查 | `design-review` | 审计报告 + 原子修复 |
| 探索设计方向 | `design-shotgun` | 对比面板 + approved.json |
| 设计稿转代码 | `design-html` | 生产级 HTML |

---

## 一句话结论

**Phase 2 的核心产出是 `DESIGN.md`（设计体系）+ `approved.json`（视觉方案选择）。`DESIGN.md` 是贯穿设计->规划->实现->审查全流程的设计锚点，地位等同于 Phase 1 的需求文档中的 R-ID。**

```
Phase 1 输出: 需求文档 (WHAT)
                |
Phase 2 输出: DESIGN.md (LOOK) + approved.json (WHICH)
                |
Phase 3 输入: ce:plan 引用 R-ID + DESIGN.md token
```
