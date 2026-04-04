---
name: dev-code
description: |
  按计划执行编码，并进行代码审查循环。使用 ce-work 执行开发，
  ce-review 审查代码，循环直到所有问题解决。
  Use when: "开始写代码", "start coding", "执行计划",
  "implement this", "动手开发", "开始实现"
argument-hint: "[计划文件路径，默认自动检测]"
---

# /dev-code - 写代码 + 审查循环

按计划执行编码，编码完成后自动进行代码审查，发现问题则修复并重新审查，循环直到通过。

## 输入

<plan_path> #$ARGUMENTS </plan_path>

如果上面为空，自动查找当前目录下的计划文件。

## 流程

### Step 1: 执行编码 (ce-work)

使用 Skill tool 调用 `compound-engineering:ce-work`，传入计划文件路径。

ce-work 会：
- 读取计划文件，理解任务列表
- 按实现单元逐个执行
- 遵循现有代码模式
- 确保测试覆盖

### Step 2: 代码审查 (ce-review)

编码完成后，使用 Skill tool 调用 `compound-engineering:ce-review`。

ce-review 会：
- 启动多个 reviewer persona (根据 diff 内容动态选择)
- 并行审查代码变更
- 合并去重审查结果
- 输出结构化审查报告

### Step 3: 审查循环

如果 ce-review 输出的发现中有 severity >= warning 的问题，进入修复循环。
info 级别的发现记录但不阻塞。

1. 列出所有需要修复的问题和建议
2. 再次调用 `compound-engineering:ce-work`，传入修复任务
3. 修复后再次调用 `compound-engineering:ce-review`
4. 重复直到审查通过

**最多循环 5 轮**。5 轮后如果仍有问题，用 AskUserQuestion：

> 已完成 5 轮代码审查循环，仍有 {N} 个未解决的问题：
> {问题列表}
>
> - A) 继续修复（再开 5 轮）
> - B) 忽略剩余问题，继续下一步
> - C) 中断，稍后手动处理

### Step 4: 输出与衔接

所有审查通过后，告诉用户：

> 代码审查通过。共经过 {N} 轮 code-review 循环。
>
> 下一步：
> - `/dev-qa` - 启动服务进行全面测试
> - `/dev-accept` - 跳过自动测试，直接进入人工验收（小改动可选）
