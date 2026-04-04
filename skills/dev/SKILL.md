---
name: dev
description: |
  智能开发编排器。自动识别四种开发模式并路由到对应流程：
  - 直接开发: 功能改进或新功能
  - 像素级还原: 按 HTML 原型开发
  - 自主设计开发: 从反馈到设计到开发 (0→1)
  - 排查修复: Bug 复现→根因分析→修复
  每个阶段自动衔接，关键节点等待确认。
  Use when: "开始开发", "dev mode", "走完整流程", "开发这个",
  "做这个功能", "修这个 bug", "按原型开发", "设计一下"
argument-hint: "[功能描述、Bug 描述、原型路径或反馈内容]"
---

# /dev - 智能开发编排器

一个入口，四种模式。自动识别输入类型，路由到对应开发流程。

## 输入

<input> #$ARGUMENTS </input>

如果上面为空，问用户："你想做什么？描述一下（功能需求/Bug 报告/原型路径/反馈内容）。"

## Step 0: 模式识别

分析用户输入，自动识别开发模式：

**像素级还原模式** (pixel) - 匹配关键词：
- 原型、HTML、设计稿、像素、高保真、按照设计、还原、mockup、prototype
- 或输入是 .html 文件路径 / URL

**自主设计模式** (design) - 匹配关键词：
- 客户反馈、运营反馈、用户反馈、从零开始、0到1、需要设计、新页面
- 出原型、做个设计、design from scratch

**排查修复模式** (fix) - 匹配关键词：
- bug、报错、异常、崩溃、500、404、白屏、修复、fix、error、panic
- 出问题了、不正常、regression

**直接开发模式** (direct) - 默认：
- 功能改进、新功能、优化、重构、添加、修改
- 或不匹配以上任何模式

识别后用 AskUserQuestion 确认：
> 识别到 **{模式名}** 模式。
> - A) 正确，继续
> - B) 不对，我选择模式：
>   - 直接开发（功能改进/新功能）
>   - 像素级还原（按原型开发）
>   - 自主设计（从反馈到设计到开发）
>   - 排查修复（Bug 修复）

---

## 模式 1: 直接开发 (direct)

最高频模式。已有功能改进或新功能添加。

### Phase 1: 需求评估

调用 Skill tool 执行 `dev-eval`，传入功能描述。

完成后用 AskUserQuestion：
> 需求评估完成。
> - A) 继续 → 生成计划
> - B) 需求已经很明确了，跳过评估，直接生成计划（用户原始输入作为需求）
> - C) 中断，稍后手动继续

如果 B，将用户的原始功能描述直接作为 dev-plan 的需求输入。

### Phase 2: 生成计划 + 创建工作区

调用 Skill tool 执行 `dev-plan`。

### Phase 3: 计划审查（可选）

用 AskUserQuestion：
> 计划已生成。要进行多轮深度审查吗？
> - A) 完整审查 (gstack autoplan: CEO→Eng→Design→DX)
> - B) 跳过审查，直接编码（小需求推荐）

如果 A，调用 Skill tool 执行 `dev-review-plan`。

### Phase 4: 编码 + 审查循环

调用 Skill tool 执行 `dev-code`。
ce-work + ce-review 循环，直到代码审查通过。

### Phase 5-7: 共享后半段 (qa → accept → ship)

→ 跳到下方「共享后半段」

---

## 模式 2: 像素级还原 (pixel)

按 HTML 高保真原型像素级还原为产品代码。

### Phase 1: 分析原型 + 计划 + 编码

调用 Skill tool 执行 `dev-pixel`。

dev-pixel 会完成：
- 分析 HTML 原型（组件结构、样式规范、交互逻辑）
- 调用 dev-plan 生成计划 + 创建 worktree
- 调用 dev-code 编码 + 像素级审查循环

### Phase 2-4: 共享后半段 (qa → accept → ship)

→ 跳到下方「共享后半段」

---

## 模式 3: 自主设计开发 (design)

从客户/运营反馈出发，0 到 1 完成设计和开发。

### Phase 1: 问题分析 + 设计 + 原型

调用 Skill tool 执行 `dev-design`。

dev-design 会完成：
- 问题识别 + 痛点分析
- 调用 dev-eval 做价值判断 + 需求设计
- 原型设计（design-shotgun + design-html）

### Phase 2: 计划

调用 Skill tool 执行 `dev-plan`（基于需求文档 + 原型）。

用 AskUserQuestion 决定是否审查计划（调用 `dev-review-plan`）。

### Phase 3: 编码 + 审查循环

调用 Skill tool 执行 `dev-code`。

### Phase 4-6: 共享后半段 (qa → accept → ship)

→ 跳到下方「共享后半段」

---

## 模式 4: 排查修复 (fix)

系统化复现 Bug → 根因分析 → 修复 → 验证。

### Phase 1: 复现 + 根因分析 + 修复

调用 Skill tool 执行 `dev-fix`。

dev-fix 会完成：
- Bug 复现（CE reproduce-bug + Superpower validator）
- 根因分析（gstack-investigate）
- 创建 worktree + 修复代码（dev-code）

### Phase 2-4: 共享后半段 (qa → accept → ship)

→ 跳到下方「共享后半段」

---

## 共享后半段

所有模式在专属环节完成后，统一进入以下流程：

### 全面测试

调用 Skill tool 执行 `dev-qa`。
启动服务 → 浏览器测试 + 接口验证 + 日志分析 → 自动修复 → 循环。

### 人工验收

调用 Skill tool 执行 `dev-accept`。
生成验收清单，等待人工确认，然后创建 issue + PR。

### 交付

调用 Skill tool 执行 `dev-ship`。
知识沉淀 → squash merge → 关闭 issue → 删除 worktree。

---

## 流程控制

- 模式识别后有确认卡点，用户可以切换模式
- 每个 Phase 之间有确认卡点，可以跳过或中断
- 中断后可以用对应的独立 skill 恢复（如 `/dev-code` 从编码开始）

## 全部 Skill 列表

| Skill | 模式 | 说明 |
|-------|------|------|
| `/dev` | 全部 | 智能编排器，自动识别模式 |
| `/dev-eval` | 直接/设计 | 评估想法，输出需求文档 |
| `/dev-plan` | 全部 | 生成计划 + 创建 worktree |
| `/dev-review-plan` | 全部 | 计划多轮深度审查 |
| `/dev-code` | 全部 | 写代码/审查循环 |
| `/dev-qa` | 全部 | 全面测试 + 自动修复 |
| `/dev-accept` | 全部 | 人工验收 + 创建 issue/PR |
| `/dev-ship` | 全部 | 知识沉淀 + merge + 清理 |
| `/dev-pixel` | 像素级 | 分析 HTML 原型 + 像素级审查 |
| `/dev-design` | 自主设计 | 问题分析 + 需求设计 + 原型生成 |
| `/dev-fix` | 排查修复 | Bug 复现 + 根因分析 |
