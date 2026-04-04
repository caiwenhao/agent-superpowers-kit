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

如果 ce-review 发现需要修复的问题：

1. 列出所有发现的问题和修复建议
2. 再次调用 `compound-engineering:ce-work`，传入修复任务
3. 修复后再次调用 `compound-engineering:ce-review`
4. 重复直到审查通过

**最多循环 5 轮**。如果 5 轮后仍有问题，列出未解决的问题，
让用户决定是否继续或手动处理。

### Step 4: 输出与衔接

所有审查通过后，告诉用户：

> 代码审查通过。共经过 {N} 轮 code-review 循环。
>
> 下一步：
> - `/dev-qa` - 启动服务进行全面测试
> - `/dev-accept` - 跳过自动测试，直接进入人工验收（小改动可选）
