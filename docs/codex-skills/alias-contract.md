# `dev:*` Alias Contract

- Public phase vocabulary uses `dev:*`.
- Current literal Codex CLI invocation uses `$dev-flow`, `$dev-plan`, and the other `$dev-*` `$name` forms.
- Repo-local Codex discovery uses `.agents/skills/<hyphenated-name>/SKILL.md`.
- Frontmatter `name:` values use hyphenated names such as `dev-flow`.
- No `SKILL.md` in this suite may use a colon in `name:`.
- `.agents/skills/<hyphenated-name>/SKILL.md` entries are symlinks to canonical `claude-skills/<hyphenated-name>/SKILL.md` source files.
- `codex-skills/<hyphenated-name>/SKILL.md` may exist as a human-facing bundle mirror, but it is not the runtime project skill root.
- Project-local `dev-*` skills are only live in Codex/OMX sessions when project scope is active, for example after `omx setup --scope project`.
