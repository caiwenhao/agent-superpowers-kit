---
name: dev:verify
description: "Use after implementation to run multi-layer quality verification. Detects diff content to auto-select which review personas and additive layers to activate. ce:review is always the core gate."
---

# Phase 5: Verify -- "质量关"

## Overview

Phase 5 is the quality gate. `ce:review` **detects** diff content and **auto-selects** 6-20+ persona reviewers. Additional verification layers are **auto-stacked** based on what changed.

Position in workflow: Phase 4 (code) -> **Phase 5** -> Phase 6 (delivery)

## When to Use

- Code changes are complete and committed
- Ready to validate before creating a PR or shipping

**Never skip Phase 5.**

## Scene Detection

### Core Review (always, auto-detected by `ce:review`)

`ce:review` reads the diff and auto-selects reviewers:

**Always-on (every review, no detection needed):**
- correctness, testing, maintainability, project-standards, agent-native, learnings

**Auto-detected by diff content:**

| Detected Signal in Diff | Auto-activated Persona |
|---|---|
| Files in `auth/`, `login`, `session`, `permission` | `security-reviewer` |
| Files with DB queries, `cache`, `async`, `worker` | `performance-reviewer` |
| Files in `routes`, `serializer`, `*.proto`, `openapi` | `api-contract-reviewer` |
| Files in `db/migrate/`, `schema`, backfill scripts | `data-migrations-reviewer` + `schema-drift-detector` |
| Files with `rescue`, `retry`, `timeout`, `circuit` | `reliability-reviewer` |
| Diff >= 50 changed lines OR touches auth/payments | `adversarial-reviewer` |
| Files in Rails `app/controllers/`, `app/models/` | `kieran-rails-reviewer` + `dhh-rails-reviewer` |
| Files `*.py` | `kieran-python-reviewer` |
| Files `*.ts`, `*.tsx` | `kieran-typescript-reviewer` |
| Files with Stimulus/Turbo controllers, DOM events | `julik-frontend-races-reviewer` |
| PR has existing review comments | `previous-comments-reviewer` |

### Additive Layers (auto-detected by diff file paths)

| Detected Signal | Auto-stacked Layer |
|---|---|
| Diff touches `views/`, `components/`, `*.tsx`, `*.css`, `*.html` | `test-browser` (affected routes) |
| 5+ UI files changed across multiple pages | `gstack/qa` (full site) + `design-review` |
| Diff touches `auth`, `payment`, `secret`, `token`, `*.pem` | `gstack/cso` (OWASP + STRIDE) |
| Diff touches `prompt`, `llm`, `ai`, `openai`, `anthropic` | `gstack/review` (LLM trust boundary) |
| Diff touches hot API paths, rendering loops, `*.sql` | `gstack/benchmark` (Core Web Vitals) |
| Diff touches `README`, `docs/`, `CONTRIBUTING`, CLI help text | `gstack/devex-review` |

## Workflow

1. **`ce:review` auto-detects and announces team:**
   ```
   Review team:
   - correctness (always)
   - testing (always)
   - maintainability (always)
   - security -- new endpoint in routes.rb accepts user input
   - kieran-rails -- controller changed in app/controllers/
   - adversarial -- diff is 120 lines touching auth
   ```

2. **REVIEW (Core): `ce:review mode:autofix plan:<plan-path>`**
   - Confidence filter: >= 0.60 (P0 >= 0.50)
   - safe_auto fixes applied automatically
   - R-ID requirements trace verification
   - Residual issues -> todo system

   **GATE: PASS verdict required.**

3. **If NEEDS_WORK**: address findings (verify before adopting), re-run until PASS

4. **Auto-stack additive layers** based on detected signals. Announce:
   - "Diff touches auth + frontend -- stacking CSO audit and browser tests."
   - "No additional layers needed for this diff."

5. **Run `todo-resolve`** to batch-process remaining todos

6. **Next**: `/dev:ship` (Phase 6)

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | Code diff, plan file path (for R-ID verification) |
| **Output** | PASS verdict, safe_auto fixes applied, todos resolved |
| **Next** | `/dev:ship` (Phase 6) |

## Iron Laws

- **Evidence before assertions** -- never claim "tests pass" without running the command and reading output
- **Verify before adopting** -- review feedback must be verified against codebase before implementing
