# ce-review Interactive Mode Protocol

Phase 5 full review with user decisions. Applies when no `mode:` token is present.

---

## Persona Selection

Always-on (every review):

| Agent | Focus |
|-------|-------|
| `ce-correctness-reviewer` | Logic errors, edge cases, state bugs, error propagation |
| `ce-testing-reviewer` | Coverage gaps, weak assertions, brittle tests |
| `ce-maintainability-reviewer` | Coupling, complexity, naming, dead code |
| `ce-project-standards-reviewer` | CLAUDE.md/AGENTS.md compliance |
| `ce-agent-native-reviewer` | Agent-accessibility of new features |
| `ce-learnings-researcher` | Past solutions in docs/solutions/ |

Cross-cutting conditional (select per diff content):

| Agent | Trigger |
|-------|---------|
| `ce-security-reviewer` | Auth, public endpoints, user input, permissions |
| `ce-performance-reviewer` | DB queries, data transforms, caching, async |
| `ce-api-contract-reviewer` | Routes, serializers, type signatures, versioning |
| `ce-data-migrations-reviewer` | Migrations, schema changes, backfills |
| `ce-reliability-reviewer` | Error handling, retries, timeouts, background jobs |
| `ce-adversarial-reviewer` | Diff >=50 changed executable lines, or auth/payments/data mutations/external APIs |
| `ce-previous-comments-reviewer` | PR with existing review comments |

---

## Severity Scale

| Level | Meaning | Action |
|-------|---------|--------|
| P0 | Critical breakage, exploitable vuln, data loss | Must fix before merge |
| P1 | High-impact defect in normal usage | Should fix |
| P2 | Moderate issue with meaningful downside | Fix if straightforward |
| P3 | Low-impact, narrow scope | User's discretion |

---

## Autofix Classification

| `autofix_class` | Owner | Behavior |
|-----------------|-------|----------|
| `safe_auto` | `review-fixer` | Applied automatically, no user prompt |
| `gated_auto` | `downstream-resolver` | Concrete fix exists but changes behavior/contracts; presented to user |
| `manual` | `downstream-resolver` | Actionable but needs handoff or cross-team context |
| `advisory` | `human` / `release` | Report-only: learnings, rollout notes, residual risk |

---

## Synthesis Pipeline

1. Validate compact JSON returns from sub-agents (drop malformed).
2. Deduplicate via fingerprint: `normalize(file) + line_bucket(line, +/-3) + normalize(title)`.
3. Cross-reviewer agreement: 2+ reviewers on same fingerprint promotes anchor one step (50->75, 75->100).
4. Separate `pre_existing: true` findings.
5. Resolve severity/routing disagreements (keep most conservative).
6. Normalize final `autofix_class`, `owner`, `requires_verification`.
7. Confidence gate: suppress findings below anchor 75 (P0 at anchor 50+ survives).
8. Partition: fixer queue (`safe_auto`), residual actionable (`gated_auto`/`manual`), report-only (`advisory`).
9. Sort by severity -> anchor desc -> file -> line. Assign stable monotonic `#` across full set.

---

## Plan Discovery (R-ID Verification)

Check in priority order, stop at first hit:
1. `plan:` argument passed by caller.
2. PR body scan for `docs/plans/*.md` paths.
3. Auto-discover from branch-name keywords against `docs/plans/*`.

Tag confidence: `explicit` (caller/PR body single match) or `inferred` (auto-discover).
Extract R-IDs (R1, R2...) and Implementation Units. Stage 6 reports met/not addressed/partial per requirement.
- `explicit` plan: unaddressed R-IDs become P1 `manual` findings.
- `inferred` plan: unaddressed R-IDs become P3 `advisory` findings.

---

## Cross-Model Adversarial Review

`ce-correctness-reviewer`, `ce-security-reviewer`, and `ce-adversarial-reviewer` inherit the session model (no override). All other persona sub-agents use the mid-tier model (sonnet). Dispatch all reviewers in bounded parallel respecting harness concurrency limits.

---

## Multi-Round Loop (max 3 rounds)

1. Apply `safe_auto` fixes automatically (no user prompt).
2. Re-review only changed scope after fixes land.
3. Bound loop at max 2 re-review rounds for autofix/walk-through Apply paths. If issues remain after second round, hand off as residual work.

Best-judgment path (option B) is single-pass with no re-review loop.

---

## Residual Work Gate (4 options)

After `safe_auto` applied, present remaining `gated_auto`/`manual` findings via blocking question tool. Stem: `What should the agent do with the remaining N findings?`

Options:
- **(A)** Review each finding one by one -- per-finding walk-through with Apply/Defer/Skip/Auto-resolve menu
- **(B)** Auto-resolve with best judgment -- fixer applies what it can defend, surfaces the rest
- **(C)** File a [TRACKER] ticket per finding without applying fixes (omit when no sink available)
- **(D)** Report only -- take no further action

Option C label adapts: named tracker when `confidence=high` AND `named_sink_available=true`; generic "File an issue" otherwise. Omit entirely when `any_sink_available=false`.

---

## Todo-Resolve Batch Processing

Walk-through (option A) accumulates Apply decisions in memory. At end-of-loop, dispatch one fixer subagent for the full Apply set in a single pass against a consistent tree. Defer actions execute inline via tracker-defer. Skip/Acknowledge are no-ops.

Best-judgment (option B) dispatches fixer immediately on full pending set. Fixer returns `{applied, failed, advisory}`. If `failed` is non-empty, fire post-run question: File tickets / Walk through failed set / Ignore.

After all actions complete, emit unified completion report: per-finding entries with action taken, summary counts by bucket, failures called out, end-of-review verdict.
