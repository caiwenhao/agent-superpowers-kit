---
name: dev-fix
description: |
  排查修复模式。系统化复现 Bug，进行根因分析，修复并验证。
  组合 CE reproduce-bug + Superpower bug-reproduction-validator
  + gstack investigate 进行全链路排查。
  Use when: "修复 bug", "排查问题", "报错了", "fix this bug",
  "出了个 bug", "异常", "崩溃了", "500 错误", "页面白屏"
argument-hint: "[Bug 描述、报错信息或 issue 链接]"
---

# /dev-fix - 排查修复

系统化复现 Bug → 根因分析 → 修复 → 验证的完整修复链路。

## 输入

<bug_report> #$ARGUMENTS </bug_report>

如果上面为空，问用户：
"请描述 Bug 现象：什么操作触发的？报错信息是什么？预期行为是什么？"

## 流程

### Step 1: Bug 复现

#### 1a. 系统化复现 (CE reproduce-bug)

使用 Skill tool 调用 `compound-engineering:reproduce-bug`，传入 Bug 描述。

reproduce-bug 会：
- 分析 Bug 描述，提取复现步骤
- 在代码中定位相关文件
- 尝试通过测试或手动步骤复现 Bug

#### 1b. 复现验证 (Superpower)

使用 Agent tool 启动 `compound-engineering:workflow:bug-reproduction-validator` (Superpower)：
- 独立验证 Bug 是否可复现
- 确认复现步骤的准确性
- 记录复现环境和条件

如果无法复现，用 AskUserQuestion：
> Bug 无法复现。
> - A) 提供更多信息（环境、步骤、截图）
> - B) 标记为无法复现，关闭
> - C) 继续分析代码，尝试找到潜在问题

### Step 2: 根因分析

使用 Skill tool 调用 `gstack-investigate`。

gstack-investigate 使用四阶段方法论：
1. **调查** - 收集证据（日志、代码、数据）
2. **分析** - 分析证据链，缩小范围
3. **假设** - 提出根因假设并验证
4. **实施** - 确认根因，制定修复方案

Iron Law: 不确认根因不动手修复。

输出根因分析报告：
```markdown
## 根因分析

### 根因
{具体原因，精确到文件和行号}

### 影响范围
{哪些功能受影响}

### 修复方案
{具体修复策略}

### 回归风险
{修复可能引入的风险}
```

### Step 3: 创建工作区 + 修复

```bash
# 基于 bug 描述创建分支
REPO_ROOT=$(git rev-parse --show-toplevel)
FIX_NAME="{bug-short-name}"
WORKTREE_PATH="$REPO_ROOT/.worktrees/$FIX_NAME"
git worktree add "$WORKTREE_PATH" -b "fix/$FIX_NAME"
```

切换到 worktree 后，调用 Skill tool 执行 `dev-code`：
- ce-work 执行修复（基于根因分析报告）
- ce-review 审查修复代码
- 循环直到审查通过

### Step 4: 后续流程（复用）

修复完成后，依次调用：
- `/dev-qa` - 验证修复 + 回归测试
- `/dev-accept` - 人工验收（重点验证 Bug 已修复且无回归）
- `/dev-ship` - 知识沉淀 + merge + 清理
