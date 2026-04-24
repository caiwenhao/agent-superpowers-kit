#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find "$script_dir/.agents/skills" -maxdepth 2 -name SKILL.md | sort

echo "Repo-local Codex skill surface is ready."
