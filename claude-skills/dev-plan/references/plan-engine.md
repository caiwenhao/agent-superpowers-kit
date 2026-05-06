# Plan Engine Protocol

## 1. Core Principles

1. Use requirements as source of truth — build from origin doc, not re-invent.
2. Decisions, not code — capture approach, boundaries, files, dependencies, risks, test scenarios. No implementation code.
3. Research before structuring — explore codebase, learnings, external guidance before finalizing.
4. Right-size the artifact — small work gets compact plan, large work gets more structure.
5. Separate planning from execution discovery — resolve planning-time questions here; defer runtime unknowns.
6. Keep the plan portable — no tool-specific executor instructions.
7. Honor user-named resources — treat named CLIs, URLs, files as authoritative input.

## 2. Source Document Discovery

1. Search `docs/brainstorms/` for `*-requirements.md`.
2. Match by semantic topic, recency (30 days), and scope overlap.
3. If match found: read thoroughly, carry forward problem frame, actors (A-IDs), flows (F-IDs), acceptance examples (AE-IDs), requirements, scope boundaries, key decisions, dependencies, outstanding questions.
4. Reference carried decisions with `(see origin: <source-path>)`.
5. If no match: proceed from user request directly; run planning bootstrap to establish problem frame, intended behavior, scope boundaries, success criteria.

## 3. Scope Classification

- **Lightweight** — small, well-bounded, low ambiguity. 2-4 units. Omit optional sections.
- **Standard** — normal feature or bounded refactor. 3-6 units. Full core template.
- **Deep** — cross-cutting, strategic, high-risk, highly ambiguous. 4-8 units. Full template plus extensions.

Reclassify Lightweight to Standard if work touches: env vars consumed externally, exported public APIs/CLI flags, CI/CD config, shared types imported downstream, externally-linked docs.

## 4. Multi-Agent Research Dispatch

### 4.1 Local (always runs, parallel)

- `ce-repo-research-analyst` — technology, architecture, patterns.
- `ce-learnings-researcher` — institutional knowledge from `docs/solutions/`.

### 4.2 External (conditional, parallel)

Trigger when: high-risk topic (security, payments, privacy, migrations), fewer than 3 local pattern examples, user exploring unfamiliar territory, relevant tech layer absent/thin.

Skip when: strong local pattern exists, user knows intended shape, tech layer well-established.

- `ce-best-practices-researcher`
- `ce-framework-docs-researcher` — pass exact framework+version from repo-research output.

### 4.3 Flow Analysis (Standard/Deep only)

- `ce-spec-flow-analyzer` — identify missing edge cases, state transitions, handoff gaps.

## 5. U-ID Stability Rules

1. Assign sequentially: U1, U2, U3...
2. Never renumber existing U-IDs on reorder, split, or deletion.
3. Splitting keeps original U-ID on original concept; new unit gets next unused number.
4. Gaps from deletion are preserved — gaps are fine.
5. Format: `### U1. [Name]` (heading, not list item).

## 6. Origin Tracing

- **R-IDs** — requirements from origin or derived during planning.
- **A-IDs** — actors from origin; carry when they affect behavior, permissions, UX, orchestration.
- **F-IDs** — key flows from origin.
- **AE-IDs** — acceptance examples from origin; link in test scenarios with `Covers AE<N>.` prefix (sparse, not forced).

Every origin R/F/AE affecting implementation must appear in: Requirements, a U-ID unit, test scenarios, verification, scope boundaries, or explicit deferral.

## 7. Test Scenarios Per Unit

Each feature-bearing unit enumerates specific test cases. Consider all applicable categories:

1. **Happy path** — core functionality, expected inputs/outputs.
2. **Edge cases** — boundary values, empty inputs, nil/null, concurrent access.
3. **Error paths** — invalid input, downstream failures, timeouts, permission denials.
4. **Integration** — cross-layer behaviors mocks alone won't prove (callbacks, middleware, multi-layer interactions).

Requirements:
- Name specific input, action, and expected outcome per scenario.
- Right-size to unit complexity — simple config may need one; payment flow may need a dozen.
- Non-feature units (pure config, scaffolding, styling): use `Test expectation: none -- [reason]`.
- Blank/missing test scenarios on feature-bearing units = incomplete.

## 8. Confidence Check and Automatic Deepening

### 8.1 Gate Decision

- Lightweight: skip unless high-risk.
- Standard: deepen when important sections look thin.
- Deep/high-risk: targeted second pass.
- Thin local grounding override: always score if Phase 1 triggered external research due to <3 local examples.

### 8.2 High-Risk Signals

Auth/security, payments/billing, data migrations, external APIs, privacy/compliance, cross-interface parity, significant rollout concerns.

### 8.3 Outcome

If plan sufficiently grounded: "Confidence check passed — no sections need strengthening."
Otherwise: dispatch targeted sub-agents per weak sections, synthesize findings into plan, set `deepened: YYYY-MM-DD` in frontmatter.

## 9. Plan Template Structure

```yaml
---
title: [Plan Title]
type: feat|fix|refactor
status: active
date: YYYY-MM-DD
origin: docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md
deepened: YYYY-MM-DD  # optional
---
```

### Sections (in order)

1. **Summary** — 1-3 line prose, forward-looking.
2. **Problem Frame** — backward-looking pain/context.
3. **Assumptions** — headless mode only; unvalidated agent inferences.
4. **Requirements** — R-IDs with origin actor/flow/AE traces.
5. **Scope Boundaries** — explicit non-goals + `### Deferred to Follow-Up Work`.
6. **Context & Research** — relevant code/patterns, institutional learnings, external refs.
7. **Key Technical Decisions** — decision + rationale pairs.
8. **Open Questions** — resolved during planning / deferred to implementation.
9. **Output Structure** — (optional) file tree for greenfield plans creating 3+ new files.
10. **High-Level Technical Design** — (optional) pseudo-code, mermaid, data flow, state diagram. Framed as directional guidance.
11. **Implementation Units** — U-ID headed sections with: Goal, Requirements, Dependencies, Files, Approach, Execution note (optional), Technical design (optional), Patterns to follow, Test scenarios, Verification.
12. **System-Wide Impact** — interaction graph, error propagation, state lifecycle, API parity, integration coverage, unchanged invariants.
13. **Risks & Dependencies** — risk/mitigation table.
14. **Documentation / Operational Notes** — docs, rollout, monitoring impacts.
15. **Sources & References** — origin doc, related code, PRs, external docs.

### File Naming

```
docs/plans/YYYY-MM-DD-NNN-<type>-<descriptive-name>-plan.md
```

- Sequence NNN zero-padded starting at 001.
- Descriptive name: 3-5 words, kebab-cased.
- All file paths in plan body: repo-relative, never absolute.
