<!-- Canonical source: dev-discover/references/doc-review-protocol.md. Keep in sync. -->
# Document Review Protocol

Condensed from ce-doc-review. Invoke via `Skill("ce-doc-review", "[mode:headless] <path>")`.

## 1. Personas

### Always-on

| Persona | Focus |
|---------|-------|
| coherence | Internal consistency, cross-reference accuracy, terminology drift |
| feasibility | Technical viability, codebase alignment, implementation risk |

### Conditional (activate by content signal)

| Persona | Activation signal |
|---------|-------------------|
| product-lens | Challengeable premise claims OR strategic weight (path dependencies, opportunity cost) |
| design-lens | UI/UX refs, user flows, interaction descriptions, accessibility |
| security-lens | Auth, API endpoints, PII/payments, trust boundaries |
| scope-guardian | Multiple priority tiers, >8 requirements/units, stretch goals, misaligned boundaries |
| adversarial | Requirements with 2+ challengeable claims; high-stakes domain; new abstraction/framework; plan without origin doc; plan extending scope beyond origin; explicit unresolved tradeoffs |

Do NOT activate adversarial on routine plans derived from validated requirements that stay in scope.

## 2. Doc-Shape Scoping

Classify by content shape (path is tie-breaker only):

- **requirements**: frontmatter with actors/flows/acceptance_examples; R-IDs (R1, A1, F1, AE1); user/business problem framing; no implementation units
- **plan**: frontmatter with type/origin; U-IDs (U1, U2); per-unit Goal/Files/Approach/Test; repo-relative paths; technical decision framing

Classification determines persona behavior and terminal routing (requirements -> ce-plan, plan -> ce-work).

## 3. Decision Primer (Round-to-Round Suppression)

Round 1: empty `<prior-decisions>` block.
Round 2+: accumulate applied/rejected entries with evidence snippets (~120 chars, first quote).

Rejected = Skip | Defer | Acknowledge. All suppress re-raised findings via:
- Fingerprint match: `normalize(section) + normalize(title)`
- Evidence-substring overlap >50%

Exception: if document text changed around the section, treat as new finding.

## 4. Synthesis Pipeline

Execute in order:

1. **Validate** — drop findings missing required fields or with invalid enums
2. **Confidence gate** — drop anchors 0/25 silently; anchor 50 -> FYI; anchors 75/100 -> actionable
3. **Deduplicate** — fingerprint on normalized section+title; merge or preserve contradictions
4. **Same-persona redundancy collapse** — cluster 3+ findings from one persona sharing root premise; keep strongest, demote rest to FYI
5. **Cross-persona promotion** — 2+ independent personas on same finding: promote anchor one step (50->75, 75->100)
6. **Resolve contradictions** — combined finding, set manual, frame as tradeoff
7. **Deterministic tie-break** — recommended_action: Skip > Defer > Apply (most conservative wins)
8. **Premise-dependency chains** — link dependents to root premise challenges (max 6 per root); cascade on root rejection
9. **Promote auto-eligible** — manual findings with codebase-pattern evidence or mechanical completions -> gated_auto/safe_auto
10. **Route by three tiers:**

| Anchor | Class | Route |
|--------|-------|-------|
| 100 | safe_auto | Apply silently |
| 100 | gated_auto | Walk-through, Apply recommended |
| 100 | manual | Walk-through, user judgment |
| 75 | safe_auto | Demote to gated_auto, walk-through |
| 75 | gated_auto | Walk-through, Apply recommended |
| 75 | manual | Walk-through, user judgment |
| 50 | any | FYI subsection only |

11. **Sort** — P0>P1>P2>P3, errors before omissions, confidence desc, document order
12. **Suppress restated residuals** — drop residual_risks/deferred_questions that restate actionable findings

## 5. Multi-Round Loop

- Max 3 rounds recommended (allow more if user insists)
- Convergence detection: fixed findings self-suppress (evidence gone); rejected findings suppressed by R29; applied fixes verified by R30
- If findings repeat after suppression mechanisms run, recommend completion
- Cross-session persistence: none. New invocation = fresh round 1.

## 6. Headless Mode

Set via `mode:headless` in arguments. Changes:
- safe_auto fixes: applied silently (same as interactive)
- All other findings: returned as structured text envelope, no blocking prompts
- Phase 5: returns "Review complete" immediately
- Caller receives findings with original classifications intact

Envelope format: Applied fixes, Proposed fixes (gated_auto), Decisions (manual), FYI observations (anchor 50), Residual concerns, Deferred questions, Coverage footnotes.
