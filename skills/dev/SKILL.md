---
name: dev
description: |
  直接开发模式编排器。串联 eval→plan→review→code→qa→accept→ship 全流程。
  每个阶段自动衔接，关键节点等待确认。
  Use when: "开始开发", "dev mode", "走完整流程",
  "从头到尾做这个功能", "开发这个", "full dev flow"
argument-hint: "[功能描述]"
---

# /dev - 直接开发模式编排器

一键走完 eval → plan → review → code → qa → accept → ship 全流程。

## 输入

<feature> #$ARGUMENTS </feature>

如果上面为空，问用户："你想做什么功能？描述一下。"

## 编排流程

本 skill 依次调用 7 个独立 skill，每个阶段之间有确认卡点。
用户可以在任何卡点选择跳过或中断。

### Phase 1: 需求评估

调用 Skill tool 执行 `dev-eval`，传入功能描述。

完成后用 AskUserQuestion：
> 需求评估完成。
> - A) 继续 → 生成计划
> - B) 需求已经很明确了，跳过评估，直接生成计划
> - C) 中断，我稍后手动继续

如果 B，跳过 eval 阶段。

### Phase 2: 生成计划 + 创建工作区

调用 Skill tool 执行 `dev-plan`。

会创建 git worktree 并生成实施计划。

### Phase 3: 计划审查

用 AskUserQuestion：
> 计划已生成。要进行多轮深度审查吗？
> - A) 是，进行完整审查 (gstack autoplan: CEO→Eng→Design→DX)
> - B) 跳过审查，直接开始编码（小需求推荐）

如果 A，调用 Skill tool 执行 `dev-review-plan`。

### Phase 4: 编码 + 审查循环

用 AskUserQuestion：
> 准备开始编码。确认？
> - A) 开始
> - B) 等一下，我想先看看计划

调用 Skill tool 执行 `dev-code`。
ce-work + ce-review 循环执行直到审查通过。

### Phase 5: 全面测试

调用 Skill tool 执行 `dev-qa`。
启动服务 → 浏览器测试 + 接口验证 + 日志分析 → 自动修复 → 循环。

### Phase 6: 人工验收

调用 Skill tool 执行 `dev-accept`。
生成验收清单，等待人工确认，然后创建 issue + PR。

### Phase 7: 交付

调用 Skill tool 执行 `dev-ship`。
知识沉淀 → squash merge → 关闭 issue → 删除 worktree。

## 流程控制

- 每个 Phase 之间有确认卡点，用户可以跳过或中断
- Phase 3 (计划审查) 对小需求可跳过
- Phase 5 (QA) 对纯后端/不涉及 UI 的改动可简化
- 如果用户中断，可以在任意阶段用对应的独立 skill 恢复
  例如：已完成 plan，直接调用 `/dev-code` 从编码开始

## 独立 Skill 列表

| 阶段 | Skill | 说明 |
|------|-------|------|
| 评估 | `/dev-eval` | 分析想法，输出需求文档 |
| 计划 | `/dev-plan` | 生成计划 + 创建 worktree |
| 审查 | `/dev-review-plan` | 计划多轮审查 |
| 编码 | `/dev-code` | 写代码/审查循环 |
| 测试 | `/dev-qa` | 全面测试 + 自动修复 |
| 验收 | `/dev-accept` | 人工验收 + 创建 issue/PR |
| 交付 | `/dev-ship` | 知识沉淀 + merge + 清理 |
