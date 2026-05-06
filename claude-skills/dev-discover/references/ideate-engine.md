# Ideate Engine Protocol

Reference for ce-ideate divergent idea generation and adversarial filtering.

## Purpose

Generate and critically evaluate grounded improvement ideas. Precedes brainstorm
(ce-brainstorm defines the chosen idea; ce-plan builds it). Output: ranked ideation
artifact in `docs/ideation/`.

## Three Modes

| Mode | Subject | Grounding Source |
|------|---------|-----------------|
| repo-grounded | Feature, module, subsystem in current codebase | Codebase scan + learnings + web research |
| elsewhere-software | Product/app/SaaS outside this repo | User-context synthesis + learnings + web research |
| elsewhere-non-software | Naming, narrative, personal, non-digital | User-context synthesis + web research (no learnings) |

## Phase 0: Scope and Resume

1. Check `docs/ideation/` for recent (30-day) docs matching the focus
2. Subject-identification gate: confirm the subject is identifiable, not vague
3. Classify mode via two binary decisions (repo vs elsewhere; software vs non-software)
4. Context-substance gate (elsewhere modes): collect URL, description, or paste
5. Interpret focus hint and volume override (default: 6-8 ideas per agent, top 5-7 survivors)
6. Cost transparency: state agent count before dispatch

## Phase 1: Parallel Grounding Agents

Dispatch in foreground (results needed before Phase 2):

| Agent | Repo Mode | Elsewhere Mode |
|-------|-----------|----------------|
| Codebase scan (cheapest model) | Top-level layout, patterns, pain points, leverage | Skipped |
| User-context synthesis (cheapest model) | Skipped | Themes, tensions, omissions from user material |
| Learnings researcher | Search `docs/solutions/` | Software only; skip non-software |
| Web researcher | Prior art, adjacent solutions, market signals | Same |
| Issue intelligence (conditional) | Only if issue-tracker intent detected | N/A |

Consolidated grounding summary feeds Phase 2.

## Phase 2: Divergent Generation (6 Parallel Sub-Agents)

Dispatch on inherited model (no tier-down). Each targets ~6-8 ideas.

### Six Ideation Frames

1. Pain and friction — user/operator pain points
2. Inversion, removal, or automation — eliminate or automate painful steps
3. Assumption-breaking and reframing — challenge what is treated as fixed
4. Leverage and compounding — choices that make future moves cheaper
5. Cross-domain analogy — how unrelated fields solve analogous problems
6. Constraint-flipping — invert obvious constraints to extremes

Issue-tracker mode: cluster-derived frames replace defaults, capped at 4 agents.

### Per-Idea Output Contract

| Field | Required |
|-------|----------|
| title | Yes |
| summary | 2-4 sentences |
| warrant | Tagged: `direct:` / `external:` / `reasoned:` |
| why_it_matters | Connects warrant to significance |
| meeting_test | One line (waived for tactical scope) |

### Warrant Types

- `direct:` — quoted line, specific file, named issue, explicit user context
- `external:` — named prior art, domain research, adjacent pattern with source
- `reasoned:` — explicit first-principles argument written out (not a gesture)

No warrant = idea does not surface. Prevents generic AI-slop.

## Post-Generation: Merge and Synthesize

1. Merge and dedupe into master candidate list
2. Synthesize cross-cutting combinations (3-5 in specified mode; 5-8 in surprise-me)
3. Weight toward focus without excluding stronger adjacent ideas
4. Spread across dimensions: workflow/DX, reliability, extensibility, capabilities, docs, quality

## Phase 3: Adversarial Filtering

Load `references/post-ideation-workflow.md` for rubric. For each candidate:

1. Apply critique rubric
2. Reject with explicit reason or promote to survivor list
3. Quality mechanism: explicit rejection with reasons, not optimistic ranking

## Surprise-Me Mode

Activated when user selects "Surprise me" at subject-identification gate.

- Deterministic routing: repo present -> repo-grounded; no repo -> elsewhere-software
- Phase 1 grounding is deeper (representative files, PR activity, themes)
- Phase 2 sub-agents discover their own subjects from Phase 1 material
- Cross-subject divergence is the feature
- Cross-cutting synthesis gets extra attention (5-8 additions)

## Handoff Menu

After filtering, present options:

1. Refine — adjust survivors
2. Open and iterate in Proof — collaborative editing
3. Brainstorm — take top survivor into ce-brainstorm for requirements
4. Save and end — write artifact to `docs/ideation/`
