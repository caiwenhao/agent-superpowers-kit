#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
status=0

workflow_summary_patterns=(
  "detects"
  "routes through"
  "routes to"
  "orchestrates"
  "auto-selects"
  "always uses"
  "auto-triggered"
  "auto-stacked"
  "single entry point"
  "检测"
  "路由到"
  "路由至"
  "统一编排"
  "自动选择"
  "自动触发"
  "自动叠加"
  "唯一入口"
)

while IFS= read -r file; do
  name="$(sed -n 's/^name:[[:space:]]*//p' "$file" | head -1 | tr -d '"' | tr -d "'" | tr -d '\r')"
  description="$(sed -n 's/^description:[[:space:]]*//p' "$file" | head -1 | tr -d '"' | tr -d "'" | tr -d '\r')"
  description_lc="$(printf '%s' "$description" | tr '[:upper:]' '[:lower:]')"

  if [[ -z "$name" ]]; then
    echo "MISSING name in $file"
    status=1
  elif [[ ! "$name" =~ ^[a-z0-9-]+$ ]]; then
    echo "INVALID name in $file: $name"
    status=1
  fi

  if [[ -z "$description" ]]; then
    echo "MISSING description in $file"
    status=1
    continue
  fi

  if [[ "$description" != Use\ when* && "$description" != 用于* && "$description" != 适用于* ]]; then
    echo "INVALID description prefix in $file: $description"
    status=1
  fi

  for pattern in "${workflow_summary_patterns[@]}"; do
    if [[ "$description_lc" == *"$pattern"* ]]; then
      echo "WORKFLOW-SUMMARY description in $file: found '$pattern'"
      status=1
      break
    fi
  done
done < <(find "$root/skills" -name SKILL.md | sort)

exit "$status"
