# `dev:*` Alias Contract

- Public phase vocabulary uses `dev:*`.
- Current literal Codex CLI invocation uses `$dev-flow`, `$dev-plan`, and the other `$dev-*` `$name` forms.
- Repo-local Codex discovery uses `.codex/skills/<hyphenated-name>/SKILL.md`.
- Frontmatter `name:` values use hyphenated names such as `dev-flow`.
- No `SKILL.md` in this suite may use a colon in `name:`.
- `.codex/skills/<hyphenated-name>/SKILL.md` entries are symlinks to canonical `plugins/dev/skills/<hyphenated-name>/SKILL.md` source files.
- `.agents/skills/<hyphenated-name>/SKILL.md` may exist as a legacy compatibility mirror, but it is not the canonical project skill root.
- Project-local `dev-*` skills are only live in Codex/OMX sessions when project scope is active, for example after `omx setup --scope project` or an equivalent `CODEX_HOME=./.codex` launch with project config present.
