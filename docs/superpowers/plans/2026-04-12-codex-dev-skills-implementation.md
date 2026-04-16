# Codex-Native `dev:*` Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the first Codex-native `dev:*` skill suite so the repo exposes a valid, testable, thin-orchestration phase workflow for Codex CLI without relying on Claude-only naming or discovery assumptions, and without implying a literal `dev:*` invocation bridge already exists.

**Architecture:** Keep `plugins/dev/skills/` as the authored source of truth for the eight phase skills, and expose them to Codex CLI through repo-local `.agents/skills/<skill>/SKILL.md` symlinks inside real runtime directories. For the current stage, the supported literal Codex CLI invocation remains `$dev-flow`, `$dev-plan`, and the other `$dev-*` `$name` forms; `dev:*` remains phase vocabulary only. Add a small repo-local validation harness that enforces `writing-skills` frontmatter and discovery rules, then rewrite each `dev-*` skill so it is thin, Codex-native, and aligned with the approved design spec.

**Tech Stack:** Markdown skills, bash validation scripts, repo-local `.agents/skills/` symlinks, existing Codex skill discovery contract, git

---

## File Structure

### Canonical skill source

- `plugins/dev/skills/dev-flow/SKILL.md`
- `plugins/dev/skills/dev-discover/SKILL.md`
- `plugins/dev/skills/dev-design/SKILL.md`
- `plugins/dev/skills/dev-plan/SKILL.md`
- `plugins/dev/skills/dev-code/SKILL.md`
- `plugins/dev/skills/dev-verify/SKILL.md`
- `plugins/dev/skills/dev-ship/SKILL.md`
- `plugins/dev/skills/dev-learn/SKILL.md`

These remain the authored copies. They are edited directly.

### Codex runtime surface

- `.agents/skills/dev-flow/SKILL.md` -> symlink to `../../../plugins/dev/skills/dev-flow/SKILL.md`
- `.agents/skills/dev-discover/SKILL.md` -> symlink to `../../../plugins/dev/skills/dev-discover/SKILL.md`
- `.agents/skills/dev-design/SKILL.md` -> symlink to `../../../plugins/dev/skills/dev-design/SKILL.md`
- `.agents/skills/dev-plan/SKILL.md` -> symlink to `../../../plugins/dev/skills/dev-plan/SKILL.md`
- `.agents/skills/dev-code/SKILL.md` -> symlink to `../../../plugins/dev/skills/dev-code/SKILL.md`
- `.agents/skills/dev-verify/SKILL.md` -> symlink to `../../../plugins/dev/skills/dev-verify/SKILL.md`
- `.agents/skills/dev-ship/SKILL.md` -> symlink to `../../../plugins/dev/skills/dev-ship/SKILL.md`
- `.agents/skills/dev-learn/SKILL.md` -> symlink to `../../../plugins/dev/skills/dev-learn/SKILL.md`

This keeps Codex-native discovery working without creating a second authored copy, while ensuring plain `find` can see concrete `SKILL.md` paths.

### Validation and support files

- Create: `plugins/dev/tests/validate-frontmatter.sh`
- Create: `plugins/dev/tests/validate-discovery.sh`
- Create: `plugins/dev/tests/red-baselines.md`
- Create: `docs/codex-skills/alias-contract.md`
- Create: `docs/codex-skills/testing-matrix.md`
- Modify: `plugins/dev/.claude-plugin/plugin.json`
- Modify: `install-skills.sh`

## Task 1: Establish The Codex Runtime Contract

**Files:**
- Create: `.agents/skills/`
- Create: `.agents/skills/dev-flow/SKILL.md` (symlink)
- Create: `.agents/skills/dev-discover/SKILL.md` (symlink)
- Create: `.agents/skills/dev-design/SKILL.md` (symlink)
- Create: `.agents/skills/dev-plan/SKILL.md` (symlink)
- Create: `.agents/skills/dev-code/SKILL.md` (symlink)
- Create: `.agents/skills/dev-verify/SKILL.md` (symlink)
- Create: `.agents/skills/dev-ship/SKILL.md` (symlink)
- Create: `.agents/skills/dev-learn/SKILL.md` (symlink)
- Create: `docs/codex-skills/alias-contract.md`

- [ ] **Step 1: Write the failing contract check**

Create `docs/codex-skills/alias-contract.md` with the exact contract:

```md
# `dev:*` Alias Contract

- Public phase vocabulary uses `dev:*`.
- Current literal Codex CLI invocation uses `$dev-flow`, `$dev-plan`, and the other `$dev-*` `$name` forms.
- Repo-local Codex discovery uses `.agents/skills/<hyphenated-name>/SKILL.md`.
- Frontmatter `name:` values use hyphenated names such as `dev-flow`.
- No `SKILL.md` in this suite may use a colon in `name:`.
- `.agents/skills/<hyphenated-name>/SKILL.md` entries are symlinks to canonical `plugins/dev/skills/<hyphenated-name>/SKILL.md` source files.
```

- [ ] **Step 2: Run a repo-state check to verify the runtime surface does not exist yet**

Run:

```bash
find .agents/skills -maxdepth 2 -name SKILL.md 2>/dev/null | sort
```

Expected: no `dev-*` skill entries are listed.

- [ ] **Step 3: Create the Codex runtime symlinks**

Run:

```bash
mkdir -p .agents/skills
mkdir -p .agents/skills/dev-flow .agents/skills/dev-discover .agents/skills/dev-design .agents/skills/dev-plan .agents/skills/dev-code .agents/skills/dev-verify .agents/skills/dev-ship .agents/skills/dev-learn
ln -snf ../../../plugins/dev/skills/dev-flow/SKILL.md .agents/skills/dev-flow/SKILL.md
ln -snf ../../../plugins/dev/skills/dev-discover/SKILL.md .agents/skills/dev-discover/SKILL.md
ln -snf ../../../plugins/dev/skills/dev-design/SKILL.md .agents/skills/dev-design/SKILL.md
ln -snf ../../../plugins/dev/skills/dev-plan/SKILL.md .agents/skills/dev-plan/SKILL.md
ln -snf ../../../plugins/dev/skills/dev-code/SKILL.md .agents/skills/dev-code/SKILL.md
ln -snf ../../../plugins/dev/skills/dev-verify/SKILL.md .agents/skills/dev-verify/SKILL.md
ln -snf ../../../plugins/dev/skills/dev-ship/SKILL.md .agents/skills/dev-ship/SKILL.md
ln -snf ../../../plugins/dev/skills/dev-learn/SKILL.md .agents/skills/dev-learn/SKILL.md
```

- [ ] **Step 4: Verify Codex-visible skill paths resolve**

Run:

```bash
find .agents/skills -maxdepth 2 -name SKILL.md -print | sort
```

Expected:

```text
.agents/skills/dev-code/SKILL.md
.agents/skills/dev-design/SKILL.md
.agents/skills/dev-discover/SKILL.md
.agents/skills/dev-flow/SKILL.md
.agents/skills/dev-learn/SKILL.md
.agents/skills/dev-plan/SKILL.md
.agents/skills/dev-ship/SKILL.md
.agents/skills/dev-verify/SKILL.md
```

- [ ] **Step 5: Commit the runtime contract**

```bash
git add .agents/skills docs/codex-skills/alias-contract.md
git commit -m "Expose dev skills through Codex-native runtime paths"
```

## Task 2: Add The Validation Harness And RED Baselines

**Files:**
- Create: `plugins/dev/tests/validate-frontmatter.sh`
- Create: `plugins/dev/tests/validate-discovery.sh`
- Create: `plugins/dev/tests/red-baselines.md`
- Create: `docs/codex-skills/testing-matrix.md`

- [ ] **Step 1: Write the failing frontmatter validator**

Create `plugins/dev/tests/validate-frontmatter.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
status=0

while IFS= read -r file; do
  name="$(sed -n 's/^name: *//p' "$file" | head -1 | tr -d '"' | tr -d "'")"
  description="$(sed -n 's/^description: *//p' "$file" | head -1 | tr -d '"' | tr -d "'")"

  if [[ ! "$name" =~ ^[a-z0-9-]+$ ]]; then
    echo "INVALID name in $file: $name"
    status=1
  fi

  if [[ "$description" != Use\ when* && "$description" != 用于* && "$description" != 适用于* ]]; then
    echo "INVALID description prefix in $file"
    status=1
  fi
done < <(find "$root/skills" -name SKILL.md | sort)

exit "$status"
```

- [ ] **Step 2: Run the validator and verify it fails on the current suite**

Run:

```bash
bash plugins/dev/tests/validate-frontmatter.sh
```

Expected: failure because current files still include `name: dev:...` and workflow-heavy descriptions.

- [ ] **Step 3: Add the discovery-boundary validator**

Create `plugins/dev/tests/validate-discovery.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

for skill in dev-flow dev-discover dev-design dev-plan dev-code dev-verify dev-ship dev-learn; do
  file=".agents/skills/$skill/SKILL.md"
  test -f "$file"
  grep -q "^name: $skill$" "$file"
done
```

- [ ] **Step 4: Add the RED baseline scenario doc**

Create `plugins/dev/tests/red-baselines.md` with one section per skill:

```md
# RED Baseline Scenarios For `dev-*`

## `dev-flow`
- Scenario: repo has active plan plus dirty branch
- Failure to observe before rewrite: restarts from discovery instead of resume

## `dev-discover`
- Scenario: user gives a vague feature request
- Failure to observe before rewrite: jumps straight to plan or code
```

Include all eight skills using the scenarios approved in the design spec.

- [ ] **Step 5: Mirror the same matrix in a user-facing support doc**

Create `docs/codex-skills/testing-matrix.md`:

```md
# Codex `dev-*` Testing Matrix

| Skill | RED baseline | Green proof |
|---|---|---|
| `dev-flow` | Active plan + dirty branch resumes incorrectly | Enters resume lane |
| `dev-discover` | Vague idea jumps ahead | Produces requirements lane |
```

Populate the full 8-row matrix.

- [ ] **Step 6: Re-run both validators**

Run:

```bash
bash plugins/dev/tests/validate-frontmatter.sh || true
bash plugins/dev/tests/validate-discovery.sh
```

Expected: discovery check passes once symlinks exist; frontmatter check still fails until the skill rewrites are complete.

- [ ] **Step 7: Commit the validation harness**

```bash
git add plugins/dev/tests docs/codex-skills/testing-matrix.md
git commit -m "Add validation and RED baselines for dev skills"
```

## Task 3: Rewrite `dev-flow` As A Thin Orchestrator

**Files:**
- Modify: `plugins/dev/skills/dev-flow/SKILL.md`
- Test: `plugins/dev/tests/validate-frontmatter.sh`

- [ ] **Step 1: Replace the invalid frontmatter and workflow-heavy description**

Set the frontmatter to:

```yaml
---
name: dev-flow
description: Use when starting a development task, resuming interrupted work, or when the correct workflow phase is unclear in a Codex CLI session
---
```

- [ ] **Step 2: Replace the body with a thin-orchestration structure**

Rewrite the section outline to:

```md
# dev-flow

## Overview
`$dev-flow` is the top-level phase router for Codex CLI work.

## When to Use
- starting new work
- resuming interrupted work
- phase unclear

## Entry Signals
- active plan artifacts
- dirty branch
- user asks to ship
- user provides plan path

## Decision Rules
- inspect artifacts first
- resume before restarting
- skip only when explicit phase-skip conditions apply

## REQUIRED SUB-SKILLS
- `dev-discover`
- `dev-design`
- `dev-plan`
- `dev-code`
- `dev-verify`
- `dev-ship`
- `dev-learn`

## Gate / Stop Conditions
- stop at each phase gate and report in Chinese

## Common Mistakes
- restarting discovery when an active plan already exists
- treating `dev:*` as literal invocation syntax or actual frontmatter names
```

- [ ] **Step 3: Run the frontmatter validator**

Run:

```bash
bash plugins/dev/tests/validate-frontmatter.sh
```

Expected: `dev-flow` no longer fails name or description checks.

- [ ] **Step 4: Commit the `dev-flow` rewrite**

```bash
git add plugins/dev/skills/dev-flow/SKILL.md
git commit -m "Make dev-flow a Codex-native thin router"
```

## Task 4: Rewrite `dev-discover` And `dev-plan`

**Files:**
- Modify: `plugins/dev/skills/dev-discover/SKILL.md`
- Modify: `plugins/dev/skills/dev-plan/SKILL.md`
- Test: `plugins/dev/tests/validate-frontmatter.sh`

- [ ] **Step 1: Fix `dev-discover` frontmatter**

Use:

```yaml
---
name: dev-discover
description: Use when new work is still vague, value is uncertain, or a Codex CLI session needs a requirements artifact before planning
---
```

- [ ] **Step 2: Rewrite `dev-discover` to route instead of narrate**

Keep only these core sections:

```md
## Decision Rules
- no approved requirements -> stay in discovery
- value unclear -> route to `office-hours`
- idea space unclear -> route to `ce:ideate`
- otherwise -> route to `ce:brainstorm`
```

- [ ] **Step 3: Fix `dev-plan` frontmatter**

Use:

```yaml
---
name: dev-plan
description: Use when approved requirements exist and a Codex CLI session needs a reviewed implementation plan before code changes begin
---
```

- [ ] **Step 4: Rewrite `dev-plan` as a planning gate**

Keep only these core rules:

```md
## Decision Rules
- `ce:plan` is the only plan creator
- choose review depth from implementation-unit count
- route UI-sensitive plans through `plan-design-review`
- do not include implementation code in the plan skill body
```

- [ ] **Step 5: Run the frontmatter validator**

Run:

```bash
bash plugins/dev/tests/validate-frontmatter.sh
```

Expected: `dev-discover` and `dev-plan` pass name and description checks.

- [ ] **Step 6: Commit both rewrites**

```bash
git add plugins/dev/skills/dev-discover/SKILL.md plugins/dev/skills/dev-plan/SKILL.md
git commit -m "Thin out discovery and planning phase skills"
```

## Task 5: Rewrite `dev-code` And `dev-verify`

**Files:**
- Modify: `plugins/dev/skills/dev-code/SKILL.md`
- Modify: `plugins/dev/skills/dev-verify/SKILL.md`
- Test: `plugins/dev/tests/validate-frontmatter.sh`

- [ ] **Step 1: Fix `dev-code` frontmatter**

Use:

```yaml
---
name: dev-code
description: Use when an approved plan exists or a very small bare prompt is ready for implementation in a Codex CLI session
---
```

- [ ] **Step 2: Rewrite `dev-code` to focus on execution posture only**

Keep these rules:

```md
## Decision Rules
- approved plan -> route to `ce:work`
- very small bare prompt -> allow inline execution
- bug work -> require `systematic-debugging` before fix
- implementation notes may trigger `test-driven-development`
```

- [ ] **Step 3: Fix `dev-verify` frontmatter**

Use:

```yaml
---
name: dev-verify
description: Use when implementation is complete and a Codex CLI session needs evidence-based quality verification before delivery
---
```

- [ ] **Step 4: Rewrite `dev-verify` as the full quality gate**

Keep these rules:

```md
## Decision Rules
- `ce:review` is always the core gate
- additive review layers depend on diff scope and risk
- no pass claim without executed evidence
```

- [ ] **Step 5: Run the frontmatter validator**

Run:

```bash
bash plugins/dev/tests/validate-frontmatter.sh
```

Expected: `dev-code` and `dev-verify` pass.

- [ ] **Step 6: Commit both rewrites**

```bash
git add plugins/dev/skills/dev-code/SKILL.md plugins/dev/skills/dev-verify/SKILL.md
git commit -m "Refocus code and verify skills on Codex phase gates"
```

## Task 6: Rewrite `dev-ship`, `dev-learn`, And `dev-design`

**Files:**
- Modify: `plugins/dev/skills/dev-ship/SKILL.md`
- Modify: `plugins/dev/skills/dev-learn/SKILL.md`
- Modify: `plugins/dev/skills/dev-design/SKILL.md`
- Modify: `plugins/dev/.claude-plugin/plugin.json`
- Modify: `install-skills.sh`
- Test: `plugins/dev/tests/validate-frontmatter.sh`

- [ ] **Step 1: Fix frontmatter for the remaining three skills**

Use:

```yaml
---
name: dev-ship
description: Use when verified work is ready for PR, merge, deployment, or post-deploy checks in a Codex CLI session
---
```

```yaml
---
name: dev-learn
description: Use when meaningful work is complete and a Codex CLI session should capture reusable knowledge or refresh an existing pattern
---
```

```yaml
---
name: dev-design
description: Use when approved requirements involve UI, visual behavior, or interaction changes and a Codex CLI session must decide the correct design lane
---
```

- [ ] **Step 2: Rewrite `dev-ship`, `dev-learn`, and `dev-design` as thin routes**

Keep these cores:

```md
## `dev-ship` Decision Rules
- verified code only
- choose lightweight or full ship path from project state
- unresolved review feedback blocks delivery
```

```md
## `dev-learn` Decision Rules
- solved problem -> `ce:compound`
- stale knowledge -> `ce:compound-refresh`
- reusable method -> `writing-skills`
```

```md
## `dev-design` Decision Rules
- pure backend -> skip design
- existing design system + no new visual language -> route lightly
- new or unclear visual direction -> route to design exploration
```

- [ ] **Step 3: Update the plugin metadata**

Change `plugins/dev/.claude-plugin/plugin.json` description to:

```json
{
  "description": "Thin orchestration layer for the 7-phase AI coding workflow, authored once and exposed through Codex-native dev-* skills."
}
```

- [ ] **Step 4: Replace the old Claude installer with a runtime note or Codex-aware helper**

Rewrite `install-skills.sh` so it no longer claims Claude-only installation and instead verifies repo-local `.agents/skills/` entries:

```bash
#!/usr/bin/env bash
set -euo pipefail

find .agents/skills -maxdepth 2 -name SKILL.md | sort
echo "Repo-local Codex skill surface is ready."
```

- [ ] **Step 5: Run the full frontmatter validator**

Run:

```bash
bash plugins/dev/tests/validate-frontmatter.sh
```

Expected: all eight skills pass.

- [ ] **Step 6: Commit the final phase rewrites**

```bash
git add plugins/dev/skills/dev-ship/SKILL.md plugins/dev/skills/dev-learn/SKILL.md plugins/dev/skills/dev-design/SKILL.md plugins/dev/.claude-plugin/plugin.json install-skills.sh
git commit -m "Complete the Codex-native dev skill suite"
```

## Task 7: Final Verification And Handoff

**Files:**
- Test: `plugins/dev/tests/validate-frontmatter.sh`
- Test: `plugins/dev/tests/validate-discovery.sh`
- Test: `plugins/dev/tests/red-baselines.md`

- [ ] **Step 1: Run the validation scripts**

Run:

```bash
bash plugins/dev/tests/validate-frontmatter.sh
bash plugins/dev/tests/validate-discovery.sh
```

Expected: both commands exit successfully with no invalid-skill output.

- [ ] **Step 2: Review the runtime-visible frontmatter**

Run:

```bash
for f in .agents/skills/*/SKILL.md; do
  echo "--- $f"
  sed -n '1,4p' "$f"
done
```

Expected: all `name:` values are hyphenated and all `description:` values start with `Use when` or the repo-approved Chinese trigger prefixes.

- [ ] **Step 3: Verify the design spec is still matched**

Run:

```bash
rg -n "dev-flow|dev-discover|dev-plan|dev-code|dev-verify|dev-ship|dev-learn|dev-design" docs/superpowers/specs/2026-04-12-codex-skills-design.md
```

Expected: every planned skill still matches the approved design scope.

- [ ] **Step 4: Commit the verification pass**

```bash
git add .agents/skills plugins/dev/tests docs/codex-skills install-skills.sh
git commit -m "Verify Codex dev skill discovery and frontmatter contracts"
```

## Spec Coverage

- Public `dev:*` vocabulary remains intact while the current literal invocation surface stays `$dev-*`: covered by Tasks 1, 3, 4, 5, and 6.
- Hyphenated frontmatter names: covered by Tasks 3, 4, 5, and 6.
- Thin orchestration model: covered by Tasks 3 through 6.
- First batch limited to eight skills: covered by Tasks 1 through 6.
- RED baseline before skill rewrite: covered by Task 2.
- Codex-native runtime surface via `.agents/skills/`: covered by Task 1.

## Self-Review

- Placeholder scan complete: no `TBD`, `TODO`, or deferred code markers remain in the implementation steps.
- Scope check complete: this plan stays within one subsystem, the Codex-native `dev-*` skill suite.
- Consistency check complete: source-of-truth skills remain in `plugins/dev/skills/`; runtime exposure occurs through `.agents/skills/`.
