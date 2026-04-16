#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../../.." && pwd)"
fixtures="$repo_root/plugins/dev/tests/trigger-fixtures.tsv"
status=0

classify_prompt() {
  local prompt="$1"

  case "$prompt" in
    *"活动计划"*|*"未完成工作"*|*"继续推进"*|*"恢复中断"* )
      echo "dev-flow"
      ;;
    *"没想清楚"*|*"梳理"*|*"模糊"*|*"需求还没"*|*"新功能"* )
      echo "dev-discover"
      ;;
    *"页面"*|*"交互"*|*"视觉"*|*"设计路径"*|*"设计方向"* )
      echo "dev-design"
      ;;
    *"实施计划"*|*"先规划"*|*"不要直接写代码"*|*"需求文档已经确认"* )
      echo "dev-plan"
      ;;
    *"开始实现"*|*"开始写代码"*|*"现在开始实现"* )
      echo "dev-code"
      ;;
    *"质量验证"*|*"先做验证"*|*"交付前"*|*"代码改完了"* )
      echo "dev-verify"
      ;;
    *"发 PR"*|*"合并"*|*"部署"*|*"上线"* )
      echo "dev-ship"
      ;;
    *"可复用经验"*|*"整理经验"*|*"沉淀"*|*"复盘"* )
      echo "dev-learn"
      ;;
    * )
      echo "UNKNOWN"
      ;;
  esac
}

while IFS=$'\t' read -r expected prompt; do
  [[ -z "${expected:-}" ]] && continue
  actual="$(classify_prompt "$prompt")"

  if [[ "$actual" != "$expected" ]]; then
    echo "TRIGGER MISMATCH: expected=$expected actual=$actual prompt=$prompt"
    status=1
  fi
done < "$fixtures"

exit "$status"
