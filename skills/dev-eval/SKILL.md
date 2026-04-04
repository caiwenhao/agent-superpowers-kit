---
name: dev-eval
description: |
  评估一个功能想法或改进需求。通过结构化对话分析问题、判断价值、明确范围，
  输出需求文档。内部使用 ce-brainstorm 进行探索。
  Use when: "评估这个想法", "这个值不值得做", "分析一下这个需求",
  "evaluate this idea", "is this worth building"
argument-hint: "[想法或需求描述]"
---

# /dev-eval - 评估想法

评估一个功能改进想法或新功能需求。通过结构化对话，从模糊想法到清晰需求。

## 输入

<feature_idea> #$ARGUMENTS </feature_idea>

如果上面为空，问用户："你想做什么？描述一下你的想法或收到的反馈。"

## 流程

### Step 1: 调用 ce-brainstorm

使用 Skill tool 调用 `compound-engineering:ce-brainstorm`，传入用户的想法描述。

ce-brainstorm 会通过多轮对话帮助用户：
- 明确问题定义
- 挑战假设
- 探索替代方案
- 确定范围边界
- 输出结构化需求文档

### Step 2: 输出与衔接

ce-brainstorm 完成后，告诉用户：

> 需求已明确，输出了需求文档。下一步：
> - `/dev-plan` - 基于需求生成实施计划并创建工作区
> - `/dev` - 走完整开发流程

记住需求文档的路径，后续 skill 会用到。
