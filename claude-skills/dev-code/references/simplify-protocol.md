# Simplify Protocol

Post-implementation code simplification pass using three parallel analysis agents.

## When to Run

After implementation is complete and tests pass, before final review-autofix.
Scans the full accumulated diff (all changes on the branch vs base).

## Three Parallel Agents

### 1. Reuse Agent

Scan the diff for code that duplicates existing utilities in the codebase.

| Check | Action |
|-------|--------|
| New helper that duplicates existing util | Replace with existing util call |
| Reimplemented standard library function | Replace with stdlib |
| Copy-pasted logic from another module | Extract shared function or import existing |
| New abstraction that wraps a one-liner | Remove abstraction, inline the call |

### 2. Quality Agent

Scan the diff for structural code quality issues.

| Pattern | Fix |
|---------|-----|
| Redundant state (derived value stored separately) | Compute on access |
| Copy-paste code blocks (3+ lines repeated) | Extract function |
| Stringly-typed values (string where enum/const fits) | Replace with typed constant |
| Useless comments (restating the code) | Delete |
| Dead code (unreachable branches, unused imports) | Delete |
| Over-abstraction (interface with one implementor) | Inline |

### 3. Efficiency Agent

Scan the diff for performance and resource issues.

| Pattern | Fix |
|---------|-----|
| Repeated computation (same calc in a loop) | Hoist or memoize |
| Serialized I/O (sequential awaits that could parallel) | Use Promise.all or equivalent |
| Hot path bloat (debug logging in tight loops) | Move behind flag or remove |
| No-op updates (re-rendering/re-computing unchanged data) | Add equality check or memo |
| Unbounded memory (growing array/map without cleanup) | Add size limit or TTL |

## Execution Rules

1. Each agent scans the full accumulated diff independently
2. Direct fix — apply the simplification immediately
3. Skip false positives without debate (no "should we?" questions)
4. Do not introduce new abstractions to fix abstraction problems
5. Do not change public API signatures without explicit approval
6. Run tests after all simplifications to confirm nothing broke

## Post-Simplify

After all three agents complete and fixes are applied:
- Run final review-autofix pass (ce-review with autofix mode)
- This catches any issues introduced by the simplification itself
