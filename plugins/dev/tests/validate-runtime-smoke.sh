#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../../.." && pwd)"
fixtures="$repo_root/plugins/dev/tests/runtime-smoke-fixtures.tsv"
tmp_dir="$(mktemp -d)"
status=0

cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

if ! command -v codex >/dev/null 2>&1; then
  echo "SKIP runtime smoke: codex CLI not found"
  exit 0
fi

if ! codex login status >/dev/null 2>&1; then
  echo "SKIP runtime smoke: codex is not logged in"
  exit 0
fi

run_case() {
  local _expected="$1"
  local prompt="$2"
  local output_file="$3"

  codex exec \
    -C "$repo_root" \
    -s read-only \
    -m gpt-5.4-mini \
    --color never \
    --ephemeral \
    -o "$output_file" \
    "Inspect only the frontmatter and top routing lines of repo-local dev-* skills under .codex/skills/ or plugins/dev/skills/ if needed. Answer with exactly one skill name from this set: dev-flow, dev-discover, dev-design, dev-plan, dev-code, dev-verify, dev-ship, dev-learn. User request: $prompt" \
    </dev/null
}

case_index=0
while IFS=$'\t' read -r expected prompt; do
  [[ -z "${expected:-}" ]] && continue
  output_file="$tmp_dir/case-$case_index.txt"

  if ! run_case "$expected" "$prompt" "$output_file"; then
    echo "RUNTIME SMOKE FAILED TO EXECUTE: expected=$expected prompt=$prompt"
    status=1
    case_index=$((case_index + 1))
    continue
  fi

  actual="$(tr -d '\r' < "$output_file" | tail -n 1 | tr -d '[:space:]')"
  if [[ "$actual" != "$expected" ]]; then
    echo "RUNTIME SMOKE MISMATCH: expected=$expected actual=$actual prompt=$prompt"
    status=1
  fi

  case_index=$((case_index + 1))
done < "$fixtures"

exit "$status"
