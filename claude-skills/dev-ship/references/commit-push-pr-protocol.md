# Commit-Push-PR Protocol

Reference for ce-commit-push-pr adaptive delivery workflow.

## Purpose

Go from working changes to an open pull request in one step. Produces PR
descriptions that scale in depth with the complexity of the change.

## Three-Mode Dispatch

| Mode | Trigger | Actions |
|------|---------|---------|
| Full workflow | "commit and PR", "ship this", "create a PR" | Branch + stage + commit + push + create PR |
| Description update | "update PR description", "refresh the PR body" | Rewrite existing PR body only, no git state changes |
| Description-only | "write a PR description", "describe this PR" | Generate description text, apply only if user asks |

## Branch State Decision Tree

| State | Action |
|-------|--------|
| On default branch, unpushed commits | Ask to create feature branch |
| On default branch, all pushed, no PR | Report no feature branch work; stop |
| Feature branch, no upstream | Skip to push |
| Feature branch, unpushed commits | Skip to push |
| Feature branch, all pushed, no open PR | Skip to create PR |
| Feature branch, all pushed, open PR | Report up to date; stop |
| Detached HEAD | Ask to create branch or stop |

## Convention Detection Priority

1. Repo conventions in project instructions (CLAUDE.md / AGENTS.md)
2. Recent commit history pattern (last 10 commits)
3. Default: `type(scope): description` (conventional commits)

Type selection: default to `fix:` when fix and feat both seem to fit.
Reserve `feat:` for new capabilities. Other types (`chore:`, `refactor:`,
`docs:`, `perf:`, `test:`, `ci:`, `build:`, `style:`) when they fit better.

## Smart Commit Splitting

1. Scan changed files for naturally distinct concerns
2. Group at file level only (no `git add -p`)
3. Create 2-3 separate commits maximum when files clearly group
4. When ambiguous, one commit is fine
5. Never use `git add -A` or `git add .`

## Adaptive PR Description Sizing

PR body scales with change complexity:

| Change Size | Description Depth |
|-------------|------------------|
| 1-3 files, single concern | 2-3 sentence summary, no sections |
| 4-10 files, clear theme | Short narrative + key decisions |
| 10+ files or multi-concern | Full structured description with sections |

## Body-File Safety

Never use `--body` inline, `--body-file -`, stdin pipes, or heredoc-to-stdin.
Always write body to temp file and pass via `--body-file <path>`:

```bash
BODY_FILE=$(mktemp "${TMPDIR:-/tmp}/ce-pr-body.XXXXXX")
cat > "$BODY_FILE" <<'__CE_PR_BODY_END__'
<body markdown>
__CE_PR_BODY_END__
gh pr create --title "<TITLE>" --body-file "$BODY_FILE"
```

Quoted sentinel prevents expansion of `$VAR`, backticks, and literal `EOF`
inside the body.

## Evidence Decision

Before composing, determine if observable behavior warrants a demo:

1. User explicitly asked for evidence -> capture
2. Agent authored changes and knows they are non-observable -> skip silently
3. Otherwise, if diff changes observable behavior (UI, CLI, API) -> ask user

Capture via ce-demo-reel. Splice URL into `## Demo` section if public.
Skip without asking for: docs-only, config-only, test-only, internal refactors.
