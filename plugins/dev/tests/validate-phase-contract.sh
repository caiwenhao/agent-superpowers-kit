#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../../.." && pwd)"
status=0

require_pattern() {
  local file="$1"
  local pattern="$2"
  local label="$3"

  if ! grep -Fq "$pattern" "$file"; then
    echo "MISSING $label in $file: $pattern"
    status=1
  fi
}

discover="$repo_root/plugins/dev/skills/dev-discover/SKILL.md"
plan="$repo_root/plugins/dev/skills/dev-plan/SKILL.md"
code="$repo_root/plugins/dev/skills/dev-code/SKILL.md"
verify="$repo_root/plugins/dev/skills/dev-verify/SKILL.md"
design="$repo_root/plugins/dev/skills/dev-design/SKILL.md"
ship="$repo_root/plugins/dev/skills/dev-ship/SKILL.md"
learn="$repo_root/plugins/dev/skills/dev-learn/SKILL.md"

for file in "$discover" "$plan" "$code" "$verify" "$design" "$ship" "$learn"; do
  require_pattern "$file" "user-facing status and gate reporting stays in Chinese" "Chinese reporting rule"
done

require_pattern "$discover" '`ce:brainstorm`' "dev-discover delegate"
require_pattern "$discover" '`document-review`' "dev-discover delegate"
require_pattern "$discover" '$dev-design' "dev-discover handoff"
require_pattern "$discover" '$dev-plan' "dev-discover handoff"

require_pattern "$plan" '`ce:plan`' "dev-plan delegate"
require_pattern "$plan" '`plan-eng-review`' "dev-plan required review"
require_pattern "$plan" '`autoplan`' "dev-plan large-plan review"
require_pattern "$plan" '`plan-design-review`' "dev-plan UI review"
require_pattern "$plan" '$dev-code' "dev-plan handoff"

require_pattern "$code" '`ce:work`' "dev-code delegate"
require_pattern "$code" '`test-driven-development`' "dev-code delegate"
require_pattern "$code" '`systematic-debugging`' "dev-code delegate"
require_pattern "$code" '`frontend-design`' "dev-code delegate"
require_pattern "$code" '$dev-verify' "dev-code handoff"

require_pattern "$verify" '`ce:review`' "dev-verify delegate"
require_pattern "$verify" '`test-browser`' "dev-verify additive lane"
require_pattern "$verify" '`qa`' "dev-verify additive lane"
require_pattern "$verify" '`design-review`' "dev-verify additive lane"
require_pattern "$verify" '`cso`' "dev-verify additive lane"
require_pattern "$verify" '`benchmark`' "dev-verify additive lane"
require_pattern "$verify" '$dev-ship' "dev-verify handoff"

require_pattern "$design" '`plan-design-review`' "dev-design route"
require_pattern "$design" '`design-consultation`' "dev-design route"
require_pattern "$design" '`design-shotgun`' "dev-design route"
require_pattern "$design" '$dev-plan' "dev-design handoff"

require_pattern "$ship" '`git-commit-push-pr`' "dev-ship route"
require_pattern "$ship" '`ship`' "dev-ship route"
require_pattern "$ship" '`land-and-deploy`' "dev-ship route"

require_pattern "$learn" '`ce:compound`' "dev-learn route"
require_pattern "$learn" '`retro`' "dev-learn route"
require_pattern "$learn" '`ce:compound-refresh`' "dev-learn route"
require_pattern "$learn" '`writing-skills`' "dev-learn route"

exit "$status"
