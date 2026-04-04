---
name: dev-plan
description: |
  为明确的需求生成实施计划，并创建 git worktree 隔离工作区。
  内部使用 ce-plan 生成计划。
  Use when: "做个计划", "plan this",
  "create a plan", "制定方案", "规划一下"
argument-hint: "[需求描述或需求文档路径]"
---

# /dev-plan - 生成计划 + 创建工作区

基于明确需求生成实施计划，并创建隔离的 git worktree 工作区。

## 输入

<requirement> #$ARGUMENTS </requirement>

如果上面为空，检查当前对话中是否有 dev-eval 产出的需求文档。如果没有，
问用户："请描述要做的功能，或提供需求文档路径。"

## 流程

### Step 1: 确定 feature 名称

从需求中提取一个简短的 feature 名称（英文，kebab-case），用于分支名和目录名。
例如："给列表页加搜索" → `list-search`

用 AskUserQuestion 确认：
> Feature 名称: `{name}`，分支: `feat/{name}`，确认？

### Step 2: 创建 git worktree

```bash
# 获取项目根目录
REPO_ROOT=$(git rev-parse --show-toplevel)
FEATURE_NAME="{name}"
WORKTREE_PATH="$REPO_ROOT/.worktrees/$FEATURE_NAME"

# 创建 worktree + feature 分支
git worktree add "$WORKTREE_PATH" -b "feat/$FEATURE_NAME"
echo "工作区已创建: $WORKTREE_PATH"
echo "分支: feat/$FEATURE_NAME"
```

切换工作目录到新的 worktree。

### Step 3: 调用 ce-plan

使用 Skill tool 调用 `compound-engineering:ce-plan`，传入需求描述。

ce-plan 会：
- 探索代码库，理解现有模式
- 生成结构化实施计划
- 拆分实现单元
- 识别风险和依赖

计划文档会保存在工作区中。

### Step 4: 输出与衔接

计划生成完毕后，告诉用户：

> 计划已生成，工作区: `{worktree_path}`
> 分支: `feat/{name}`
>
> 下一步：
> - `/dev-review-plan` - 对计划进行多轮深度审查
> - `/dev-code` - 跳过审查，直接开始编码（小需求可选）
