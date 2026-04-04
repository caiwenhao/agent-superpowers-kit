---
name: dev-ship
description: |
  完成交付：知识沉淀 + squash merge 到 main + 关闭 issue + 删除 worktree。
  Use when: "合并", "ship it", "merge", "发布", "完成",
  "知识沉淀", "收尾", "merge to main"
argument-hint: "[无参数]"
---

# /dev-ship - 知识沉淀 + merge + 清理

完成开发的最后一步：沉淀知识、合并代码、清理工作区。

## 流程

### Step 1: 知识沉淀 (ce-compound)

使用 Skill tool 调用 `compound-engineering:ce-compound`。

ce-compound 会记录这次开发过程中学到的经验：
- 解决了什么问题
- 用了什么方案
- 踩了什么坑
- 有什么可复用的模式

### Step 2: 确认合并

用 AskUserQuestion 确认：

> 即将执行以下不可逆操作：
> 1. squash merge 当前 PR 到 main
> 2. 删除远程分支
> 3. 删除本地 worktree
>
> - A) 确认，执行合并和清理
> - B) 取消，我还没准备好

如果 B，停止并告诉用户稍后用 `/dev-ship` 继续。

### Step 3: squash merge + 关闭 issue + 清理

将 merge、issue 关闭、worktree 清理合并在一个连续流程中执行，
避免变量跨 bash 调用丢失。

```bash
# Step 3a: 获取当前状态（merge 前，变量还可用）
CURRENT_BRANCH=$(git branch --show-current)
PR_NUM=$(gh pr view --json number -q .number 2>/dev/null)
MAIN_WORKTREE=$(git worktree list | head -1 | awk '{print $1}')
CURRENT_DIR=$(pwd)

echo "分支: $CURRENT_BRANCH"
echo "PR: #$PR_NUM"
echo "主工作区: $MAIN_WORKTREE"
echo "当前目录: $CURRENT_DIR"

# Step 3b: 提取 issue 编号（merge 前提取，因为 merge 后 PR body 不变但分支会被删）
ISSUE_NUM=""
if [ -n "$PR_NUM" ]; then
  ISSUE_NUM=$(gh pr view "$PR_NUM" --json body -q '.body' | grep -oE 'Closes #[0-9]+' | grep -oE '[0-9]+' | head -1)
fi
echo "关联 Issue: ${ISSUE_NUM:-无}"

# Step 3c: squash merge
if [ -n "$PR_NUM" ]; then
  gh pr merge "$PR_NUM" --squash --delete-branch
  echo "PR #$PR_NUM 已合并"
else
  echo "未找到 PR，跳过 merge"
fi

# Step 3d: 关闭 issue（如果未被自动关闭）
if [ -n "$ISSUE_NUM" ]; then
  ISSUE_STATE=$(gh issue view "$ISSUE_NUM" --json state -q .state 2>/dev/null)
  if [ "$ISSUE_STATE" != "CLOSED" ]; then
    gh issue close "$ISSUE_NUM"
    echo "Issue #$ISSUE_NUM 已关闭"
  else
    echo "Issue #$ISSUE_NUM 已自动关闭"
  fi
fi

# Step 3e: 切回主工作区
cd "$MAIN_WORKTREE"
git checkout main
git pull origin main

# Step 3f: 删除 worktree（只在当前目录不是主工作区时）
if [ "$CURRENT_DIR" != "$MAIN_WORKTREE" ] && [ -d "$CURRENT_DIR" ]; then
  git worktree remove "$CURRENT_DIR" --force 2>/dev/null && \
    echo "工作区 $CURRENT_DIR 已删除" || \
    echo "工作区清理失败，请手动执行: git worktree remove $CURRENT_DIR --force"
fi

echo "完成"
```

### Step 4: 完成总结

输出完成总结：

> ## 开发完成
>
> - **功能**: {功能名称}
> - **分支**: {branch} -> main (squash merged)
> - **Issue**: #{N} (closed)
> - **PR**: #{M} (merged)
> - **知识沉淀**: 已记录
> - **工作区**: 已清理
>
> 整个开发流程结束。
