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

### Step 2: squash merge

```bash
# 获取当前 PR 编号
PR_NUM=$(gh pr view --json number -q .number)

# squash merge 到 main（单 commit）
gh pr merge $PR_NUM --squash --delete-branch
```

如果 merge 失败（冲突等），提示用户手动处理。

### Step 3: 关闭关联 issue

```bash
# 从 PR body 中提取关联的 issue 编号
# gh pr merge --squash 通常会自动关闭 "Closes #N" 引用的 issue
# 检查 issue 是否已关闭
ISSUE_NUM=$(gh pr view $PR_NUM --json body -q '.body' | grep -oP 'Closes #\K\d+')
if [ -n "$ISSUE_NUM" ]; then
  ISSUE_STATE=$(gh issue view $ISSUE_NUM --json state -q .state)
  if [ "$ISSUE_STATE" != "CLOSED" ]; then
    gh issue close $ISSUE_NUM
    echo "Issue #$ISSUE_NUM 已关闭"
  else
    echo "Issue #$ISSUE_NUM 已自动关闭"
  fi
fi
```

### Step 4: 清理 worktree

```bash
# 获取项目根目录和 worktree 信息
REPO_ROOT=$(git rev-parse --show-toplevel)
CURRENT_DIR=$(pwd)
FEATURE_NAME=$(git branch --show-current | sed 's|feat/||')

# 切回主工作区
cd "$REPO_ROOT"
# 如果当前在 worktree 中，先切出去
if git worktree list | grep -q "$CURRENT_DIR"; then
  cd "$(git worktree list | head -1 | awk '{print $1}')"
fi

# 拉取最新 main
git checkout main
git pull origin main

# 删除 worktree
WORKTREE_PATH="$REPO_ROOT/.worktrees/$FEATURE_NAME"
if [ -d "$WORKTREE_PATH" ]; then
  git worktree remove "$WORKTREE_PATH" --force
  echo "工作区 $WORKTREE_PATH 已删除"
fi

# 清理远程分支（如果还存在）
git push origin --delete "feat/$FEATURE_NAME" 2>/dev/null || true
```

### Step 5: 完成总结

输出完成总结：

> ## 开发完成 ✓
>
> - **功能**: {功能名称}
> - **分支**: feat/{name} → main (squash merged)
> - **Issue**: #{N} (closed)
> - **PR**: #{M} (merged)
> - **知识沉淀**: 已记录
> - **工作区**: 已清理
>
> 整个开发流程结束。
