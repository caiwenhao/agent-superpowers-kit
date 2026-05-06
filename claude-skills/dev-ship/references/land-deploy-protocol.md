# Land and Deploy Protocol

Reference for gstack-land-and-deploy merge, deploy, and verification workflow.

## Purpose

Merge the PR, wait for CI and deploy, verify production health via canary checks.
Takes over after /ship creates the PR.

## CI Wait Logic

1. Check CI status: `gh pr checks --json name,state,status,conclusion`
2. If required checks FAILING -> STOP, list failures
3. If required checks PENDING -> wait with `gh pr checks --watch --fail-fast`
4. Timeout: 15 minutes for CI, 30 minutes for merge queue
5. Poll every 30 seconds, progress message every 2 minutes

## Merge-Readiness Report

Pre-merge gate collects evidence across four dimensions:

| Check | Source | Blocker? |
|-------|--------|----------|
| Review staleness | gstack-review-read, compare stored commit to HEAD | Red if 4+ commits since review |
| Free tests | Project test command from CLAUDE.md | Yes if failing |
| E2E tests | `~/.gstack-dev/evals/` today's results | Warning if not run |
| PR body accuracy | Compare body vs actual commits | Warning if stale |
| CHANGELOG/VERSION | Check if modified on branch | Warning if missing for new features |

Staleness rules: 0 commits = CURRENT, 1-3 = RECENT, 4+ = STALE.
Offer inline quick review if engineering review is STALE or NOT RUN.

## Deploy Platform Detection

| Signal | Platform |
|--------|----------|
| `fly.toml` | Fly.io |
| `vercel.json` or `.vercel/` | Vercel |
| `render.yaml` | Render |
| `netlify.toml` | Netlify |
| `Procfile` | Heroku |
| `railway.json` or `railway.toml` | Railway |
| `.github/workflows/*deploy*` | GitHub Actions |
| CLAUDE.md `## Deploy Configuration` | Persisted config (takes priority) |

## Merge Execution

1. Try auto-merge first: `gh pr merge --auto --delete-branch`
2. If auto-merge unavailable, merge directly: `gh pr merge --squash --delete-branch`
3. Detect merge queue: if PR state does not immediately become MERGED after auto
4. Poll merge queue every 30s, up to 30 minutes

## Canary Verification Depth by Diff Type

| Diff Scope | Canary Depth |
|------------|-------------|
| SCOPE_DOCS only | Skip verification entirely |
| SCOPE_CONFIG only | Smoke: goto + verify 200 status |
| SCOPE_BACKEND only | Console errors + perf check |
| SCOPE_FRONTEND (any) | Full: console + perf + screenshot |
| Mixed scopes | Full canary |

Full canary sequence:
1. `$B goto <url>` — verify page loads (200)
2. `$B console --errors` — check for critical errors
3. `$B perf` — page load under 10 seconds
4. `$B text` — verify real content (not blank/error)
5. `$B snapshot` — screenshot as evidence

## Rollback Options per Failure Point

| Failure Point | Rollback Action |
|---------------|----------------|
| Deploy workflow failed | Offer: investigate logs / revert merge / check anyway |
| Canary health issues | Offer: mark healthy (warming up) / revert / investigate |
| Revert execution | `git revert <merge-sha> --no-edit && git push` |
| Branch protection blocks revert | Create revert PR instead |
| Revert has conflicts | Report conflict, provide merge SHA for manual resolution |

## Health Check Endpoints

Assessment criteria (all must pass for HEALTHY):
- Page loads with 200 status
- No critical console errors (Error, Uncaught, TypeError, ReferenceError)
- Page has real content (not blank or generic error)
- Loads in under 10 seconds

## First-Run vs Subsequent Behavior

| Run Type | Behavior |
|----------|----------|
| First run | Full dry-run validation: detect infrastructure, test commands, show plan, confirm |
| Config changed | Re-trigger dry run with explanation |
| Confirmed | Skip dry run, go straight to readiness checks |

Confirmation fingerprint stored at `~/.gstack/projects/$SLUG/land-deploy-confirmed`.
