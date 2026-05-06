# Review Autofix Protocol (mode:autofix)

Invoke ce-code-review with `mode:autofix`. No user interaction. Apply safe fixes, report residuals, exit.

## Persona Selection

Always-on (every review):

| Persona | Focus |
|---------|-------|
| correctness | Logic errors, edge cases, state bugs, error propagation |
| testing | Coverage gaps, weak assertions, brittle tests |
| maintainability | Coupling, complexity, naming, dead code |
| project-standards | CLAUDE.md/AGENTS.md compliance, naming, portability |
| agent-native | Verify new features are agent-accessible |
| learnings | Search docs/solutions/ for past issues related to this diff |

Conditional (triggered by diff content -- agent judgment, not keyword matching):

| Persona | Trigger |
|---------|---------|
| security | Auth, public endpoints, user input, permissions |
| performance | DB queries, data transforms, caching, async |
| api-contract | Routes, serializers, type signatures, versioning |
| data-migrations | Migrations, schema changes, backfills |
| reliability | Error handling, retries, timeouts, background jobs |
| adversarial | >=50 changed non-test/non-generated lines, or auth/payments/data mutations/external APIs |
| language-specific | Stack-specific reviewers (Rails, Python, TypeScript, Swift, frontend races) when diff warrants |

## Severity Scale

| Level | Meaning | Gate |
|-------|---------|------|
| P0 | Critical breakage, exploitable vuln, data loss | Must fix before merge |
| P1 | High-impact defect in normal usage | Should fix |
| P2 | Moderate issue, meaningful downside | Fix if straightforward |
| P3 | Low-impact, minor improvement | Discretion |

## Autofix Classification

| Class | Owner | Meaning |
|-------|-------|---------|
| safe_auto | review-fixer | Deterministic local fix; applied automatically |
| gated_auto | downstream-resolver | Concrete fix exists but changes behavior/contracts; left unresolved |
| manual | downstream-resolver | Actionable but needs handoff; left unresolved |
| advisory | human/release | Report-only (learnings, rollout notes, residual risk) |

## Execution

1. **Determine scope.** Compute diff via `base:` arg or branch detection. Include staged + unstaged.
2. **Discover intent.** Infer from branch name, commits, PR metadata. Note uncertainty in Coverage.
3. **Select reviewers.** Always-on + applicable conditionals per diff content.
4. **Spawn sub-agents.** Parallel dispatch with bounded concurrency. Each returns structured JSON findings.
5. **Synthesize findings (merge pipeline):**
   a. Validate -- drop malformed returns/findings.
   b. Anchor -- confidence uses discrete anchors: 0, 25, 50, 75, 100.
   c. Deduplicate -- fingerprint: normalize(file) + line_bucket(+/-3) + normalize(title). Merge: keep highest severity/anchor.
   d. Promote -- 2+ reviewers flag same issue: promote one anchor step (50->75, 75->100).
   e. Route -- normalize autofix_class/owner; conservative on disagreement. Never widen safe_auto->gated without evidence.
   f. Confidence gate -- suppress findings below anchor 75. Exception: P0 at anchor 50+ survives.
   g. Partition: safe_auto->review-fixer queue | residual actionable | report-only.
   h. Sort by severity->anchor->file->line; assign stable monotonic `#` across full set.
6. **Validate (Stage 5b).** Spawn one validator per surviving finding. Validator re-checks against diff/code independently. Drop rejected findings.
7. **Apply safe_auto fixes only.** Spawn one fixer subagent. If `requires_verification: true`, run targeted tests before declaring applied.
8. **Bounded re-review.** Re-review changed scope after fixes. Max 2 rounds. Residuals after round 2 become handoff.
9. **Write run artifact** to `/tmp/compound-engineering/ce-code-review/<run-id>/` with findings, applied fixes, residuals, advisory.
10. **Emit compact residual summary** in return: applied safe_auto fixes first, then residual non-auto findings preserving stable `#`. Include artifact path.

## Plan Discovery for R-ID Verification

Locate plan via: (1) `plan:` argument, (2) PR body path match, (3) auto-discover from branch keywords.
Tag confidence: `explicit` (caller-provided or unambiguous PR body) vs `inferred` (auto-discovered).
Extract R-IDs and implementation units. Flag unaddressed requirements per confidence level.

## Protected Artifacts

Never flag for deletion: `docs/brainstorms/*`, `docs/plans/*.md`, `docs/solutions/*.md`.

## Constraints

- Never commit, push, or create a PR.
- Never ask user questions.
- Leave gated_auto, manual, advisory unresolved.
- Parent workflow owns all downstream decisions.
