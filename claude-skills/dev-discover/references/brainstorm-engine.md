# Brainstorm Engine Protocol

## 1. Interaction Discipline

1. Ask ONE question per turn. Never stack sub-questions.
2. Default to the platform's blocking question tool (AskUserQuestion / request_user_input / ask_user). Fall back to numbered options only when no tool exists or the call errors.
3. Use prose only when the question is genuinely open — narrative answers, diagnostic probes where options would leak priors, or when 3-4 distinct plausible options cannot be written without padding.

## 2. Scope Classification

Classify work into one tier before proceeding:

- **Lightweight** — small, well-bounded, low ambiguity. Minimal ceremony.
- **Standard** — normal feature or bounded refactor with decisions to make.
- **Deep** — cross-cutting, strategic, or highly ambiguous.
- **Deep-product** — Deep where product shape (primary actors, core outcome, positioning, primary flows) is materially unresolved.

If scope is unclear, ask one targeted question to disambiguate.

## 3. Gap Lenses (Phase 1.2 Pressure Test)

Scan the user's opening for these gaps. Probe only those actually present, as separate prose questions, before exploring approaches.

| Lens | Fires when | Probe shape |
|------|-----------|-------------|
| **Evidence** | Asserts want/need without observable user behavior (time spent, money paid, workarounds built) | "What's the most concrete thing someone's already done about this?" |
| **Specificity** | Beneficiary too abstract to design for | "Name a specific person or segment — what changes for them when this ships?" |
| **Counterfactual** | No visibility into current workaround or cost of inaction | "What do users do today when this problem arises? What does it cost them?" |
| **Attachment** | Solution shape treated as the goal rather than the value it delivers | "What's the smallest version that still delivers real value?" |
| **Durability** | (Deep-product only) Value proposition rests on a current state that may shift | "Under the most plausible near-term shifts, how does this bet hold?" |

Scope mapping: Lightweight uses none. Standard uses Evidence/Specificity/Counterfactual/Attachment. Deep adds systemic lens. Deep-product adds Durability.

## 4. Collaborative Dialogue

1. Ask what the user is already thinking before offering ideas.
2. Start broad (problem, users, value) then narrow (constraints, exclusions, edge cases).
3. Fire all scope-appropriate gap probes before entering approach exploration.
4. Resolve product decisions here; leave implementation choices for planning.
5. Make requirements concrete enough that planning will not invent behavior.
6. Exit when the idea is clear OR user explicitly wants to proceed.

## 5. Approach Exploration

1. Propose 2-3 concrete approaches when multiple plausible directions remain.
2. Include at least one non-obvious angle: inversion, constraint removal, or cross-domain analogy.
3. Present ALL approaches first, THEN state recommendation. Do not anchor prematurely.
4. For each approach: brief description (2-3 sentences), pros/cons, key risks, best-suited context.
5. Keep at mechanism/product-shape level — no architecture, schemas, endpoints, file paths.
6. At product tier, alternatives differ on WHAT is built, not HOW.

## 6. Synthesis Summary

Three buckets presented to user before writing the requirements doc:

| Bucket | Content |
|--------|---------|
| **Stated** | Decisions the user explicitly made |
| **Inferred** | Bets the agent made from context (user can correct) |
| **Out** | Explicitly excluded scope |

Emit synthesis, then STOP. Wait for user response. If correction: revise and re-emit. If acknowledgment: proceed to requirements capture.

## 7. Requirements Document Template

Write to `docs/brainstorms/<topic>-requirements.md`. Use repo-relative paths only.

```
# <Title> Requirements
Date: YYYY-MM-DD | Tier: <tier>

## Problem Statement
## Success Criteria
## Scope Boundaries
  - Included
  - Deferred for later
  - Outside this product's identity (Deep-product only)

## Requirements
  R-ID: R-001, R-002... (functional requirements)

## Assumptions
  A-ID: A-001, A-002... (unvalidated bets from Inferred bucket)

## Flows
  F-ID: F-001, F-002... (user-facing flows, one per primary path)

## Acceptance Evidence
  AE-ID: AE-001, AE-002... (observable proof each R-ID is met)

## Dependencies / Risks
## Key Decisions (from Stated bucket)
```

Lightweight: use only Problem Statement, Requirements (R-IDs), and Acceptance Evidence (AE-IDs). Skip other sections.

## 8. Handoff Menu

After writing the doc, present options:

1. Proceed to planning (route to plan phase)
2. Iterate on requirements (continue brainstorm)
3. Park for later (end session, doc persists)
4. Discard and start fresh
