#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../../.." && pwd)"
status=0

for skill in dev-flow dev-discover dev-design dev-plan dev-code dev-verify dev-ship dev-learn; do
  file="$repo_root/.codex/skills/$skill/SKILL.md"
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

  legacy_file="$repo_root/.agents/skills/$skill/SKILL.md"
  if [[ -e "$legacy_file" ]]; then
    if [[ ! -L "$legacy_file" ]]; then
      echo "EXPECTED legacy symlink mirror: $legacy_file"
      status=1
    fi

    if [[ -L "$legacy_file" ]]; then
      legacy_target="$(readlink "$legacy_file")"
      if [[ "$legacy_target" != "$expected_target" ]]; then
        echo "INVALID legacy symlink target for $legacy_file: $legacy_target"
        status=1
      fi
    fi
  fi
done

exit "$status"
