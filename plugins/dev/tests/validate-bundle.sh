#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../../.." && pwd)"
status=0

require_symlink_target() {
  local path="$1"
  local target="$2"

  if [[ ! -L "$path" ]]; then
    echo "EXPECTED symlink: $path"
    status=1
    return
  fi

  local actual
  actual="$(readlink "$path")"
  if [[ "$actual" != "$target" ]]; then
    echo "INVALID symlink target for $path: $actual"
    status=1
  fi
}

test -f "$repo_root/codex-skills/README.md" || {
  echo "MISSING bundle README: $repo_root/codex-skills/README.md"
  status=1
}

require_symlink_target \
  "$repo_root/codex-skills/alias-contract.md" \
  "../docs/codex-skills/alias-contract.md"

require_symlink_target \
  "$repo_root/codex-skills/testing-matrix.md" \
  "../docs/codex-skills/testing-matrix.md"

for skill in dev-flow dev-discover dev-design dev-plan dev-code dev-verify dev-ship dev-learn; do
  require_symlink_target \
    "$repo_root/codex-skills/$skill/SKILL.md" \
    "../../plugins/dev/skills/$skill/SKILL.md"
done

exit "$status"
