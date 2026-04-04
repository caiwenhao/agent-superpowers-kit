---
name: dev:ship
description: "Use when Phase 5 has passed and code is ready to deliver. Detects project type and upstream quality to auto-select lightweight (CE) or full (gstack) delivery path. Both end with land-and-deploy."
---

# Phase 6: Ship -- "上线"

## Overview

Phase 6 delivers verified code to production. It **detects** project type and upstream quality context to **auto-select** the right delivery path. Two paths share a single endpoint (`land-and-deploy`).

Position in workflow: Phase 5 (verify) -> **Phase 6** -> Phase 7 (knowledge)

## When to Use

- Phase 5 verification passed
- Code is ready to ship

**Never skip Phase 6.**

## Scene Detection

**Signal 1: Does the project use versioning?**
- `VERSION` file exists OR `package.json` has `version` field -> versioned project
- No version file -> unversioned project

**Signal 2: What upstream quality was already applied?**
- `ce:review` ran in Phase 4/5 (check `.context/compound-engineering/ce-review/` for recent run) -> upstream quality confirmed
- No ce:review evidence -> needs ship's built-in review

**Signal 3: PR feedback pending?**
- Run `gh pr view --json reviewDecision,comments` on current branch
- Unresolved review threads exist -> prepend `resolve-pr-feedback`

**Signal 4: UI changes in diff?**
- Scan diff for `views/`, `components/`, `*.tsx`, `*.css`, `*.html` -> add `feature-video`

## Routing

```
Verified code (from Phase 5)
  |
  +-- [Unversioned + upstream quality confirmed] -> Path A: CE Lightweight
  |   Daily feature, already passed ce:review
  |
  +-- [Versioned project] -----------------------> Path B: gstack Full
  |   Needs VERSION bump + CHANGELOG
  |
  +-- [No upstream review evidence] --------------> Path B: gstack Full
  |   Needs ship's built-in review gates
  |
  +-- [Emergency hotfix] -------------------------> Path A: CE Lightweight
      (user explicitly says "hotfix" or "urgent")
```

### Pre-delivery (auto-detected)

```
  +-- [PR has unresolved threads] -> resolve-pr-feedback first
  +-- [Diff has UI files] ---------> feature-video in parallel
```

## Workflow

1. **Detect scene** and announce:
   - "Versioned project with VERSION file -- using full ship workflow with CHANGELOG."
   - "Upstream ce:review confirmed -- using lightweight commit+PR path."
   - "PR has 3 unresolved review threads -- resolving first."

2. **Pre-delivery** (if detected):
   - Run `/ce:resolve-pr-feedback` for pending PR comments

3. **Execute detected path**

   **Path A: CE Lightweight**
   ```
   /ce:git-commit-push-pr
     - Auto-detects conventions from repo history
     - Logical commit splitting (file-level)
     - Adaptive PR description
     [+ feature-video in parallel if UI detected]
   /gstack-land-and-deploy
     - CI wait -> merge-readiness report -> merge -> deploy -> canary
   ```

   **Path B: gstack Full Release**
   ```
   /gstack-ship
     - Merge base branch -> parallel tests -> coverage audit (60%/80%)
     - Plan completion audit + scope drift detection
     - REVIEW: pre-landing code review (auto, Step 3.5)
     - REVIEW: adversarial review -- Claude + Codex (auto, Step 3.8)
     - Version bump + CHANGELOG generation
     - Bisectable commits (dependency-ordered)
     [+ feature-video in parallel if UI detected]
   /gstack-document-release
     - Cross-references all docs against diff
     - Auto-updates factual changes, asks on narrative changes
   /gstack-land-and-deploy
     - CI wait -> merge-readiness report -> merge -> deploy -> canary
   ```

4. **`land-and-deploy` auto-detects** deployment platform and canary depth:
   - Platform: from `fly.toml` / `vercel.json` / `render.yaml` / `Procfile` / GitHub Actions
   - Canary depth by diff type: docs->skip, config->smoke, backend->console, frontend->full

   **GATE: Merge-readiness report shown to user. User confirms before merge.**

5. **Next**: `/dev:learn` (Phase 7)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Verified code diff (Phase 5 PASS) |
| **Output** | Merged PR, deployed to production, canary verified |
| **Next** | `/dev:learn` (Phase 7) |
