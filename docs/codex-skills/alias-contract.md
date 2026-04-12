# `dev:*` Alias Contract

- Public invocation uses `dev:*` vocabulary.
- Repo-local Codex discovery uses `.agents/skills/<hyphenated-name>/SKILL.md`.
- Frontmatter `name:` values use hyphenated names such as `dev-flow`.
- No `SKILL.md` in this suite may use a colon in `name:`.
- `.agents/skills/<hyphenated-name>/SKILL.md` entries are symlinks to canonical `plugins/dev/skills/<hyphenated-name>/SKILL.md` source files.
