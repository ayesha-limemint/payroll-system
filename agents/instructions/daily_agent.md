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

## Phase 2 — State Recovery & Feature Selection

On every run:

**Step 1 — Find the active session**
Call `state_machine.find_active_session()`.

This checks the most recent folder under `daily_briefs/` on Drive:
- If Status is NOT COMPLETE → resume that session, skip to the correct phase
- If Status IS COMPLETE (or no sessions exist) → start a new session for today

**There is only ever one unfinished session at a time. A new session
never starts until the previous one reaches Status: COMPLETE.**

**Step 2 — Select today's feature (only when starting a NEW session)**

1. Check `requests/pending/` on Drive first — if any files exist,
   use the oldest one. Move it to `requests/processed/` once picked up.

2. Otherwise read `BACKLOG.md` from the repo. Find the first item
   marked `[ ]` (not started). That is today's feature.
   Mark it `[~]` in BACKLOG.md and commit before proceeding.

3. Read the full context for that backlog item — the Why, the
   Acceptance criteria, the Out of scope, and the Dependencies.
   Verify all dependencies are marked `[x]` before proceeding.
   If a dependency is not complete, skip to the next `[ ]` item
   whose dependencies ARE met, and note the skip in the functional plan.

---

## Phase Index

| Phase | File | Description |
|-------|------|-------------|
| 2a | [phase_02a_questions.md](phases/phase_02a_questions.md) | Questions pending — check for `(Ash)` answers in `00_questions.md`, nudge if none, proceed if resolved |
| 3 | [phase_03_functional_plan.md](phases/phase_03_functional_plan.md) | Write functional plan (or questions doc if clarification needed) → notify Ash → exit |
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

## Domain and architecture references

Before Phase 3 / 5 Pass B cross-checks:

- [payroll_domain_playbook.md](payroll_domain_playbook.md)
- [payroll_system_architecture.md](payroll_system_architecture.md)
- [superpowers_crosscheck_prompts.md](superpowers_crosscheck_prompts.md)

## Failure Handling

See [phases/failure_handling.md](phases/failure_handling.md)

---

## Notification Rules

All notifications go to the `#payroll-agent` Slack channel via incoming webhook.
Webhook URL is in `.env` as `SLACK_WEBHOOK_URL` — never hardcode it.

Standard send command (use this in every phase):
```bash
curl -s -X POST "$SLACK_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"<message>\"}"
```

Message format:
- Lead with `[Milton]`
- One sentence on what happened, then optionally one brief dry observation — never more
- Always append the relevant Drive or GitHub URL on a new line
- Example: `"[Milton] Functional plan ready. FICA is mercifully simple — two rates, one cap, zero brackets. Good news: this one fits on a page.\nhttps://drive.google.com/..."`
