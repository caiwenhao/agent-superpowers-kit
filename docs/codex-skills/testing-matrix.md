# Codex `dev-*` Testing Matrix

| Skill | RED baseline | Green proof |
|---|---|---|
| `dev-flow` | Active plan plus dirty branch restarts from discovery | Resumes the active lane before considering earlier phases |
| `dev-discover` | Vague feature request jumps to planning or code | Produces a requirements lane before planning begins |
| `dev-design` | Pure backend work enters design, or UI work skips design | Skips backend-only work and selects a design lane for UI changes |
| `dev-plan` | Approved requirements turn into pseudo-code instead of a plan | Produces a reviewed decision-level plan with implementation units and test scenarios |
| `dev-code` | Approved work writes code without a failing test or bug-analysis discipline | Uses the right execution posture and preserves TDD/debugging gates |
| `dev-verify` | Risky diff is declared done without evidence-producing checks | Returns an evidence-backed pass or needs-work result |
| `dev-ship` | Unresolved review feedback is ignored during delivery | Blocks delivery until review feedback is resolved and the delivery path is appropriate |
| `dev-learn` | Meaningful work ends with no reusable knowledge capture | Routes to the correct learning lane or records an explicit skip |

## Validation Commands

```bash
bash plugins/dev/tests/validate-frontmatter.sh || true
bash plugins/dev/tests/validate-discovery.sh
```

Expected Task 2 state:
- `validate-frontmatter.sh` fails on workflow-summary descriptions that still need rewrites.
- `validate-discovery.sh` passes once `.agents/skills/dev-*` discovery paths exist and point at the canonical skill files.
