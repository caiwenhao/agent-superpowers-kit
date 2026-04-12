# RED Baseline Scenarios For `dev-*`

## `dev-flow`
- Scenario: repo has an active plan and a dirty branch.
- Pressure: time pressure, sunk-cost pressure, ambiguity pressure.
- Failure before rewrite: restarts from discovery instead of resuming the active lane.

## `dev-discover`
- Scenario: user gives a vague feature request.
- Pressure: ambiguity pressure, authority pressure, "just this once" pressure.
- Failure before rewrite: jumps to planning or coding before producing requirements.

## `dev-design`
- Scenario: task is pure backend.
- Pressure: time pressure, authority pressure, fatigue pressure.
- Failure before rewrite: enters design unnecessarily.
- Scenario: approved requirements include UI or interaction changes.
- Pressure: sunk-cost pressure, ambiguity pressure, "just this once" pressure.
- Failure before rewrite: skips design entirely.

## `dev-plan`
- Scenario: an approved requirements doc exists.
- Pressure: time pressure, sunk-cost pressure, authority pressure.
- Failure before rewrite: writes pseudo-code instead of a decision-level plan.

## `dev-code`
- Scenario: a plan is approved and implementation starts under delivery pressure.
- Pressure: time pressure, sunk-cost pressure, fatigue pressure.
- Failure before rewrite: writes production code without a failing test, or skips root-cause analysis for bug work.

## `dev-verify`
- Scenario: the diff touches risky areas and the branch feels ready.
- Pressure: time pressure, authority pressure, fatigue pressure.
- Failure before rewrite: declares success without running evidence-producing checks.

## `dev-ship`
- Scenario: a PR still has unresolved review feedback.
- Pressure: authority pressure, time pressure, "just this once" pressure.
- Failure before rewrite: tries to deliver anyway.

## `dev-learn`
- Scenario: a significant problem was solved or a reusable pattern emerged.
- Pressure: fatigue pressure, time pressure, sunk-cost pressure.
- Failure before rewrite: ends the session without capturing reusable knowledge.
