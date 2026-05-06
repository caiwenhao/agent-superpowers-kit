# Compound Engine Protocol

Reference for ce-compound knowledge documentation workflow.

## Purpose

Capture problem solutions while context is fresh. Create structured documentation
in `docs/solutions/` with YAML frontmatter for searchability. Uses parallel
subagents for maximum efficiency.

## Two Execution Modes

| Mode | When | Agents | Output |
|------|------|--------|--------|
| Full | Default, recommended | 3-4 parallel research + optional session historian | Cross-referenced doc with overlap detection |
| Lightweight | Long sessions, simple fixes, context limits | None (single pass) | Same doc structure, no cross-referencing |

## Track Classification

| Track | problem_type values | Key sections |
|-------|-------------------|--------------|
| Bug | build_error, test_failure, runtime_error, performance_issue, database_issue, security_issue, ui_bug, integration_issue, logic_error | Problem, Symptoms, What Didn't Work, Solution, Why This Works, Prevention |
| Knowledge | architecture_pattern, design_pattern, tooling_decision, convention, workflow_issue, developer_experience, documentation_gap, best_practice | Context, Guidance, Why This Matters, When to Apply, Examples |

## Phase 1: Parallel Research Subagents (Full Mode)

Dispatch in parallel (background), then session historian in foreground:

### 1. Context Analyzer
- Extract conversation history
- Determine track (bug vs knowledge) from problem_type using the inline tables below
- Return: YAML frontmatter skeleton, category directory path, suggested filename

### 2. Solution Extractor
- Adapt output structure based on track
- Bug track: Problem, Symptoms, What Didn't Work, Solution, Why This Works, Prevention
- Knowledge track: Context, Guidance, Why This Matters, When to Apply, Examples

### 3. Related Docs Finder
- Search `docs/solutions/` for related documentation
- Identify cross-references and links
- Flag stale/contradicted docs
- Assess overlap across 5 dimensions:

| Overlap Score | Dimensions Matching | Action |
|---------------|-------------------|--------|
| High | 4-5 (problem, root cause, solution, files, prevention) | Update existing doc |
| Moderate | 2-3 | Create new, flag for consolidation |
| Low | 0-1 | Create new normally |

### 4. Session Historian (optional, foreground)
- Only if user opted in
- Dispatch as ce-session-historian on mid-tier model
- Search session files for relevant prior context
- Return: what was tried before, what didn't work, key decisions

## Phase 2: Assembly and Write

1. Collect all Phase 1 results
2. Check overlap assessment — update existing doc if High overlap
3. Incorporate session history findings
4. Assemble markdown from the template in the Output Artifact Structure section below
5. Validate YAML frontmatter against the inline structure and required keys
6. Create directory: `mkdir -p docs/solutions/[category]/`
7. Write file
8. Run a frontmatter structure check or equivalent repo-available validator until exit 0

## Discoverability Check

After writing, verify project instruction files (AGENTS.md / CLAUDE.md) would lead
agents to discover `docs/solutions/`. If not, propose minimal addition:
- That a searchable knowledge store exists
- Its structure (categories, YAML frontmatter fields)
- When to search it (before implementing or debugging in documented areas)

## Phase 2.5: Selective Refresh Trigger

Invoke `ce-compound-refresh` when:
- Related doc recommends approach the new fix contradicts
- New fix supersedes an older documented solution
- Refactor/migration/rename invalidated references in older docs
- Pattern doc is overly broad or outdated
- Moderate overlap detected

Do NOT invoke when:
- No related docs found
- Related docs still consistent
- Overlap is superficial

## Output Artifact Structure

```yaml
---
title: <descriptive title>
date: YYYY-MM-DD
problem_type: <enum from schema>
category: <mapped from problem_type>
module: <affected module>
tags: [tag1, tag2]
# Bug track only:
symptoms: [observable symptoms]
root_cause: <technical explanation>
resolution_type: <fix type>
# Knowledge track only:
applies_when: <conditions>
---
```

Categories auto-detected: build-errors/, test-failures/, runtime-errors/,
performance-issues/, database-issues/, security-issues/, ui-bugs/,
integration-issues/, logic-errors/, architecture-patterns/, design-patterns/,
tooling-decisions/, conventions/, workflow-issues/, developer-experience/,
documentation-gaps/, best-practices/
