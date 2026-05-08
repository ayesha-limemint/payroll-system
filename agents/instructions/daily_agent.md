# Daily Build Agent — Workflow Instructions

> This file is the index. Each phase is defined in its own file under `phases/`.
> To change a phase, edit the relevant phase file and commit.
> Changes take effect on the next Routine run.

---

## How the Routine works

This agent runs as a Claude Code Routine — it fires once on schedule,
does as much work as it can, and exits. It does not poll or wait.
Every run is stateless. All state lives in Google Drive and GitHub.

Each run either:
- Advances the current session by one phase, or
- Sends a nudge/reminder if waiting for Ash's approval, and exits

---

## Phase 2 — State Recovery

On every run, call `state_machine.find_active_session()`.

This checks the most recent folder under `daily_briefs/` on Drive:
- If Status is NOT COMPLETE → resume that session
- If Status IS COMPLETE (or no sessions exist) → start a new session for today

**There is only ever one unfinished session at a time. A new session
never starts until the previous one reaches Status: COMPLETE.**

Check `requests/pending/` on Drive — if files exist, use the oldest
one as the feature for the next new session (not the current carry-over).

---

## Phase Index

| Phase | File | Description |
|-------|------|-------------|
| 3 | [phase_03_functional_plan.md](phases/phase_03_functional_plan.md) | Write functional plan → notify Ash → exit |
| 4 | [phase_04_functional_approval.md](phases/phase_04_functional_approval.md) | Check approval status → proceed or nudge/revise → exit |
| 5 | [phase_05_technical_plan.md](phases/phase_05_technical_plan.md) | Write technical plan → notify Ash → exit |
| 6 | [phase_06_technical_approval.md](phases/phase_06_technical_approval.md) | Check approval status → proceed or nudge/revise → exit |
| 7 | [phase_07_create_branch.md](phases/phase_07_create_branch.md) | Create feature branch |
| 8 | [phase_08_write_tests.md](phases/phase_08_write_tests.md) | Write failing tests [RED] |
| 9 | [phase_09_implement.md](phases/phase_09_implement.md) | Implement until tests pass [GREEN] |
| 10 | [phase_10_regression.md](phases/phase_10_regression.md) | Run full test suite |
| 11 | [phase_11_commit_pr.md](phases/phase_11_commit_pr.md) | Commit, open PR, update changelog |
| 12 | [phase_12_session_summary.md](phases/phase_12_session_summary.md) | Write summary, set Status: COMPLETE |
| 13 | [phase_13_notify_complete.md](phases/phase_13_notify_complete.md) | Send completion notification → exit |

---

## Failure Handling

See [phases/failure_handling.md](phases/failure_handling.md)

---

## Notification Rules

All emails go to: ayesha@limemint.ai
All subjects prefixed with: `[Payroll Agent]`
Body: one paragraph maximum, always include a direct Drive or GitHub link.
