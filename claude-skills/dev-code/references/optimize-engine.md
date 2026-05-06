# Optimize Engine Protocol

Reference for ce-optimize spec-driven iterative optimization loop.

## Purpose

Run metric-driven iterative optimization. Define a measurable goal, build
measurement scaffolding, run parallel experiments in isolated worktrees,
measure each against hard gates and/or LLM-as-judge quality scores, keep
improvements, converge toward the best solution.

## Three-Tier Evaluation

| Tier | Purpose | Cost | When |
|------|---------|------|------|
| Degenerate gates | Catch obviously broken solutions | Free (hard metric) | Always first |
| LLM-as-judge | Score actual quality via rubric | ~$0.15/experiment | Only if gates pass and type=judge |
| Diagnostics | Distribution stats, timing, counts | Free (logged) | Always (not gated) |

### Gate Examples

- `solo_pct <= 0.95` — catches all-singletons degenerate
- `max_cluster_size <= 500` — catches mega-cluster degenerate
- `build_time_s <= 120` — catches timeout degenerate

### Judge Scoring

- Stratified sampling per configured strata
- Batch dispatch of judge sub-agents
- Rubric-based 1-5 scoring with supplementary fields
- Aggregate primary score for comparison

## Worktree-Isolated Parallel Experiments

1. Create experiment worktree: `optimize-exp/<spec-name>/exp-<NNN>`
2. Each experiment runs in isolation (no interference between parallel runs)
3. Port parameterization for services that bind ports
4. Max 6 concurrent worktrees (configurable)
5. Worktree budget check before dispatch (warn at 12 total)

### Experiment Dispatch

1. Fill experiment prompt template with:
   - Hypothesis description and category
   - Current best and baseline metrics
   - Mutable and immutable scope
   - Constraints and approved dependencies
   - Rolling window of last 10 experiments
2. Dispatch sub-agent in experiment worktree
3. Sub-agent modifies only mutable-scope files
4. Measurement runs in worktree working directory

## Strategy Digest and Crash Recovery

### Strategy Digest (written after every batch)

Contains:
- Categories tried (with success/failure counts)
- Key learnings from this batch and overall
- Exploration frontier (untried categories and approaches)
- Current best metrics and improvement from baseline

Read by the orchestrator before generating new hypotheses. Prevents
re-trying failed approaches and guides exploration.

### Crash Recovery

| Artifact | Purpose |
|----------|---------|
| `experiment-log.yaml` | Single source of truth for all results |
| `result.yaml` per worktree | Per-experiment crash-recovery marker |
| `strategy-digest.md` | Compressed learnings for hypothesis generation |

On resume:
1. Read experiment log from disk (ground truth)
2. Scan worktree directories for `result.yaml` markers not yet in log
3. Recover measured-but-unlogged experiments
4. Continue from last iteration number

### Persistence Rules

- Write each result to disk IMMEDIATELY after measurement
- Verify every critical write (read back and confirm)
- Re-read from disk at every phase boundary
- Experiment log is append-only during Phase 3
- Never present results without writing to disk first

## Optimization Loop (Phase 3)

### Batch Cycle

1. Select hypotheses (diverse categories, high priority first)
2. Dispatch experiments (worktree or codex backend)
3. Collect results as they complete (do not wait for full batch)
4. Evaluate batch:
   - Rank by primary metric improvement
   - Keep best if it improves on current best
   - Check file-disjoint runners-up for stacking
   - Revert all others
5. Update state (outcomes, best, digest, new hypotheses)
6. Check stopping criteria

### Stopping Criteria (any triggers stop)

- Target metric value reached
- Max iterations exceeded
- Max hours exceeded
- Judge budget exhausted
- Plateau (no improvement for N consecutive experiments)
- Empty backlog with no new hypotheses generatable

## Spec Schema (Key Fields)

```yaml
name: <kebab-case identifier>
metric:
  primary: { name, type: hard|judge, direction: maximize|minimize, target }
  degenerate_gates: [{ name, operator, threshold }]
  judge: { rubric, scoring, stratification, sample_size, batch_size }
measurement: { command, working_directory, timeout_seconds }
scope: { mutable: [paths], immutable: [paths] }
execution: { mode: serial|parallel, max_concurrent, backend: worktree|codex }
stopping: { max_iterations, max_hours, plateau_iterations, target_reached }
```

## Post-Optimization Options

1. Run ce-review on cumulative diff (baseline to final)
2. Run ce-compound to document winning strategy
3. Create PR from optimization branch
4. Continue with more experiments
5. Done (leave branch for manual review)
