#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../../.." && pwd)"
status=0

for skill in dev-flow dev-discover dev-design dev-plan dev-code dev-verify dev-ship dev-learn; do
  file="$repo_root/.agents/skills/$skill/SKILL.md"
  expected_target="../../../plugins/dev/skills/$skill/SKILL.md"

  if [[ ! -f "$file" ]]; then
    echo "MISSING discovery path: $file"
    status=1
    continue
  fi

  if [[ ! -L "$file" ]]; then
    echo "EXPECTED symlink discovery path: $file"
    status=1
  fi

  if ! grep -qx "name: $skill" "$file"; then
    echo "INVALID frontmatter name at discovery path: $file"
    status=1
  fi

  if [[ -L "$file" ]]; then
    target="$(readlink "$file")"
    if [[ "$target" != "$expected_target" ]]; then
      echo "INVALID symlink target for $file: $target"
      status=1
    fi
  fi
done

exit "$status"
