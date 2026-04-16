#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find "$script_dir/.codex/skills" -maxdepth 2 -name SKILL.md | sort

if [[ -d "$script_dir/.agents/skills" ]]; then
  echo "Legacy mirror:"
  find "$script_dir/.agents/skills" -maxdepth 2 -name SKILL.md | sort
fi

echo "Repo-local Codex skill surface is ready."
echo "Activate project scope with: omx setup --scope project"
