# `dev:*` Alias Contract

- Public phase vocabulary uses `dev:*`.
- Current literal Codex CLI invocation uses `$dev-flow`, `$dev-plan`, and the other `$dev-*` `$name` forms.
- Repo-local Codex discovery uses `.agents/skills/<hyphenated-name>/SKILL.md`.
- Frontmatter `name:` values use hyphenated names such as `dev-flow`.
- No `SKILL.md` in this suite may use a colon in `name:`.
- `.agents/skills/<hyphenated-name>/SKILL.md` entries are symlinks to canonical `plugins/dev/skills/<hyphenated-name>/SKILL.md` source files.
