---
name: dev-pixel
description: |
  像素级还原模式。分析 HTML 高保真原型，提取组件结构和样式规范，
  生成计划并执行开发，使用设计审查 Superpower 验证像素级匹配。
  Use when: "像素级还原", "按原型开发", "还原设计稿", "pixel perfect",
  "照着原型做", "HTML 原型", "高保真原型"
argument-hint: "[HTML 原型文件路径或 URL]"
---

# /dev-pixel - 像素级还原

分析 HTML 高保真原型 + 需求文档，像素级还原为产品代码。

## 输入

<prototype> #$ARGUMENTS </prototype>

如果上面为空，问用户：
"请提供 HTML 原型的文件路径或 URL，以及需求文档（如有）。"

## 流程

### Step 1: 分析 HTML 原型

读取或浏览 HTML 原型，全面分析：

**如果是文件路径：**
- 使用 Read 工具读取 HTML 文件
- 提取所有组件结构、CSS 样式、交互逻辑

**如果是 URL：**
- 使用浏览器工具导航到原型页面
- 截图保存，分析页面结构

分析输出：
```markdown
## 原型分析报告

### 页面结构
- {组件层级}

### 样式规范
- 颜色: {色值列表}
- 字体: {字号/字重}
- 间距: {关键间距}
- 圆角/阴影: {样式细节}

### 交互逻辑
- {交互 1}: {触发条件} → {行为}
- {交互 2}: ...

### 响应式要求
- {断点和适配策略}
```

使用 Agent tool 启动 `compound-engineering:design:design-implementation-reviewer` (Superpower)
分析原型的设计细节，确保没有遗漏。

### Step 2: 生成计划

调用 Skill tool 执行 `dev-plan`，传入原型分析报告作为需求。

dev-plan 会：
- 创建 git worktree 隔离工作区
- 调用 ce-plan 生成实施计划，基于原型分析拆分实现单元

用 AskUserQuestion：
> 计划已生成。要进行深度审查吗？
> - A) 审查计划 (gstack-autoplan)
> - B) 跳过，直接编码

如果 A，调用 Skill tool 执行 `dev-review-plan`。

### Step 3: 编码 + 像素级审查循环

调用 Skill tool 执行 `dev-code`（ce-work + ce-review 循环）。

**在每轮 code 完成后，额外执行像素级对比：**

使用 Agent tool 启动 `compound-engineering:design:design-implementation-reviewer` (Superpower)：
- 对比原型截图 vs 实现截图
- 检测像素级差异（间距、颜色、字号、对齐）
- 输出差异报告

如果有像素级差异：
1. 将差异作为修复任务
2. 再次调用 ce-work 修复
3. 再次对比
4. 循环直到像素级匹配（最多 5 轮，超过后用 AskUserQuestion 展示剩余差异让用户决定）

### Step 4: 输出与衔接

像素级还原和编码完成后，告诉用户：

> 像素级还原完成。下一步：
> - `/dev-qa` - 浏览器交互测试 + 接口验证
> - `/dev-accept` - 人工验收
> - `/dev-ship` - 知识沉淀 + merge + 清理
> - 或通过 `/dev` 编排器自动执行后续流程
