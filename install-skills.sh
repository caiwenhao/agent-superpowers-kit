#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find "$script_dir/.agents/skills" -maxdepth 2 -name SKILL.md | sort

missing=0

while IFS= read -r skill; do
  if [ ! -f "$skill" ]; then
    echo "Broken skill link: $skill" >&2
    missing=1
    continue
  fi
  if ! sed -n '1,8p' "$skill" | grep -q '^name:'; then
    echo "Missing frontmatter name: $skill" >&2
    missing=1
  fi
  if ! sed -n '1,8p' "$skill" | grep -q '^description:'; then
    echo "Missing frontmatter description: $skill" >&2
    missing=1
  fi
done < <(find "$script_dir/.agents/skills" -maxdepth 2 -name SKILL.md | sort)

for required in dev-flow dev-discover dev-design dev-plan dev-code dev-verify dev-ship dev-learn dev-doctor dev-init dev-supervise dev-wiki-search dev-wiki-ingest dev-wiki-init; do
  if [ ! -f "$script_dir/.agents/skills/$required/SKILL.md" ]; then
    echo "Missing repo-local Codex skill: $required" >&2
    missing=1
  fi
done

if rg -n 'ce:doc-review|ce-doc-review|ce:code-review|ce:test-browser|/ce:ce|ce:ideate|ce:brainstorm|ce:compound|ce:compound-refresh|gstack/qa|gstack/cso|gstack/review|gstack/retro|gstack/learn|resolve-pr-feedback|日志即复现|增量提交|ce-code-review|/tmp/compound-engineering/ce-code-review' "$script_dir/docs/ai-coding-workflow.md" "$script_dir/claude-skills" --glob '!claude-skills/README.md' >/dev/null; then
  echo "Non-canonical or blocked workflow text remains. Run rg for details." >&2
  missing=1
fi

if [ "$missing" -ne 0 ]; then
  exit 1
fi

echo "Repo-local Codex skill surface is ready."
