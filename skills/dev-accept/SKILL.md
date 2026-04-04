---
name: dev-accept
description: |
  人工验收卡点。分析代码变更，输出验收步骤和注意点，
  等待人工确认后创建 GitHub issue 和 PR。
  Use when: "验收", "人工验收", "acceptance", "ready to review",
  "创建PR", "提交代码", "准备提交"
argument-hint: "[无参数]"
---

# /dev-accept - 人工验收卡点

分析代码变更，生成人工验收清单，用户确认后创建 GitHub issue 和 PR。

## 流程

### Step 1: 分析变更

```bash
# 获取当前分支名
BRANCH=$(git branch --show-current)

# 查看变更统计
git diff main --stat

# 查看具体改动
git diff main --name-only
```

读取计划文件（PLAN.md 或最近的需求文档），理解功能目标。

### Step 2: 生成验收清单

基于 diff 和计划文件，生成结构化验收清单：

```markdown
## 人工验收清单

### 功能验收
- [ ] {步骤 1}: {具体操作和预期结果}
- [ ] {步骤 2}: ...

### UI 验收（如有变更）
- [ ] {页面/组件}: {检查点}

### 边界情况
- [ ] {场景}: {预期行为}

### 回归风险
- ⚠️ {可能受影响的已有功能}

### 注意事项
- {需要特别关注的点}
```

### Step 3: 等待人工确认

用 AskUserQuestion 请用户验收：

> 以上是验收清单，请人工验证核心功能后确认。
>
> Options:
> - A) 验收通过，创建 issue 和 PR
> - B) 有问题，需要修复（描述问题）
> - C) 跳过验收，直接创建 PR

如果用户选 B，记录问题，提示用 `/dev-code` 修复后重新验收。

### Step 4: 创建 issue 和 PR

用户确认 OK 后：

#### 4a. 创建 GitHub issue

```bash
gh issue create \
  --title "{功能标题}" \
  --body "{基于需求文档的描述}"
```

记录 issue 编号。

#### 4b. 推送分支并创建 PR

```bash
# 推送分支
git push -u origin feat/{feature-name}

# 创建 PR，关联 issue
gh pr create \
  --title "{PR 标题}" \
  --body "## Summary
{变更摘要}

## Changes
{关键改动列表}

## Test Plan
{验收清单}

Closes #{issue_number}"
```

### Step 5: 输出与衔接

> Issue #{N} 和 PR #{M} 已创建。
>
> 下一步：
> - `/dev-ship` - 知识沉淀 + squash merge + 清理
