#!/usr/bin/env bash
set -euo pipefail

find .agents/skills -maxdepth 2 -name SKILL.md | sort
echo "Repo-local Codex skill surface is ready."
