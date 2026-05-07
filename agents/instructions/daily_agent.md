# Daily Build Agent — Workflow Instructions

> This file defines the complete behaviour of the daily build agent.
> Ash can edit this file at any time to change the workflow.
> Changes take effect on the next session start.
> Full change history is preserved in Git.

---

## Overview

Each weekday session works through up to 13 phases. The loop is fully
resumable — always start by checking the current state on Google Drive
and GitHub to determine where to pick up.

---

## Phase 2 — State Recovery & Priority Check

On every session start:

1. Read today's folder: `daily_briefs/YYYY-MM-DD/` on Google Drive
2. Determine current phase:
   - No folder exists → start at Phase 3
   - `01_functional_plan.md` exists, Status = PENDING_REVIEW → send reminder, wait for approval
   - `01_functional_plan.md` exists, Status = APPROVED, no technical plan → go to Phase 5
   - `02_technical_plan.md` exists, Status = PENDING_REVIEW → send reminder, wait for approval
   - `02_technical_plan.md` exists, Status = APPROVED, no feature branch → go to Phase 7
   - Feature branch exists, no [GREEN] commit → go to Phase 8 or 9
   - [GREEN] commit exists, no PR → go to Phase 10
3. Check `requests/pending/` on Drive — if any files exist, use the oldest one as today's feature instead of the backlog

---

## Phase 3 — Functional Plan

Write a plain-English functional plan document and save it to:
`daily_briefs/YYYY-MM-DD/01_functional_plan.md`

The document must include:

```
Status: PENDING_REVIEW
Approved by: —
Ash Notes: —

## Feature
[Name of the feature being built today]

## Why
[Why this is the next thing to build — backlog priority or Ash request]

## Test Scenarios
[Each scenario written as: Given X, when Y, then Z]
- Scenario 1: ...
- Scenario 2: ...
- Scenario 3: ...

## What will be built
[Plain English description of the user-facing or API-facing behaviour]

## What will NOT be touched today
[Explicit list of things out of scope for this session]

## Sources
[Any external references consulted — tax tables, IRS publications, etc.]
```

After saving: send Ash a Gmail notification with subject:
`[Payroll Agent] Functional plan ready for review — YYYY-MM-DD`
Body: one-paragraph summary + direct Drive link.

---

## Phase 4 — Functional Approval

Poll `01_functional_plan.md` Status field.

- APPROVED → proceed to Phase 5
- CHANGES_REQUESTED → read all `Ash:` prefixed lines in the document, revise the plan accordingly, reset Status to PENDING_REVIEW, re-save, send notification
- PENDING_REVIEW after 24 hours → send reminder: `[Payroll Agent] Reminder: functional plan awaiting your review — YYYY-MM-DD`

Never proceed to Phase 5 without APPROVED status.

---

## Phase 5 — Technical Plan

Read:
- The approved `01_functional_plan.md`
- `agents/instructions/tech_plan_template.md` from the repository

Fill in the template exactly. Do not free-form it.
Save to: `daily_briefs/YYYY-MM-DD/02_technical_plan.md`

After saving: send Ash a Gmail notification with subject:
`[Payroll Agent] Technical plan ready for review — YYYY-MM-DD`
Body: one-paragraph summary + direct Drive link.

---

## Phase 6 — Technical Approval

Same polling logic as Phase 4 but for `02_technical_plan.md`.

Never proceed to Phase 7 without APPROVED status.
This is the final gate before any code is written.

---

## Phase 7 — Create Feature Branch

Create a Git branch:
`feature/YYYY-MM-DD-<feature-name-kebab-case>`

Example: `feature/2026-05-10-nj-state-income-tax`

Push the empty branch to GitHub.

---

## Phase 8 — Write Tests First (TDD Red)

Translate every scenario from the approved technical plan into Django test cases.
Write tests to: `payroll/tests/test_<feature_name>.py`

Run tests — they must FAIL at this point. If they pass, something is wrong — stop and investigate.

Commit message format:
`[RED] Day N: <feature name> — test cases (failing)`

Push to feature branch.

---

## Phase 9 — Implementation (TDD Green)

Write implementation code to make the failing tests pass.
Work strictly within the scope approved in the technical plan.
No scope creep. No unplanned changes.

Cycle: implement → run tests → fix → repeat until all new tests pass.

Commit message format:
`[GREEN] Day N: <feature name> — implementation`

Do not proceed to Phase 10 until all new tests pass.

---

## Phase 10 — Full Regression Suite

Run the complete test suite:
`python manage.py test`

All tests — old and new — must pass.

If any existing test breaks:
1. Stop immediately
2. Investigate the regression
3. Attempt a fix
4. Re-run full suite
5. If still failing after 2 attempts: document in the daily brief, notify Ash as a blocker, do not push

---

## Phase 11 — Commit, PR & Changelog

1. Final commit with message: `Day N: <feature name> — complete`
2. Push feature branch to GitHub
3. Open Pull Request:
   - Title: `Day N: <feature name>`
   - Body: link to Drive daily brief + one-paragraph summary
4. Update `CHANGELOG.md` in repo:
   - Add entry under today's date: what was added/changed/fixed
5. Update `BACKLOG.md` on Google Drive:
   - Mark today's item complete
   - Reorder if anything discovered today affects priority

Do NOT merge the PR — that is Ash's decision.

---

## Phase 12 — Session Summary

Update `daily_briefs/YYYY-MM-DD/01_functional_plan.md` (or create a summary section) with:

```
## Session Summary

Date: YYYY-MM-DD
Status: COMPLETE

### Tests written
[List of test cases written]

### Test results
[Pass/fail counts]

### Built vs planned
[What was built exactly as planned, and any deviations with reasons]

### GitHub PR
[Link to PR]

### Backlog update
[What changed in the backlog as a result of today's work]
```

---

## Phase 13 — Completion Notification

Send Ash a Gmail notification:
Subject: `[Payroll Agent] Session complete — YYYY-MM-DD`
Body:
- One-paragraph summary of what was built
- Link to Drive session summary
- Link to GitHub PR

---

## Failure Handling

| Situation | Action |
|-----------|--------|
| Tests fail after implementation | Stop, document in brief, notify Ash as blocker |
| Approval not received in 24h | Send reminder notification, keep waiting |
| GitHub push fails | Retry 3 times with backoff, then notify Ash |
| Ambiguous requirement | Stop, write ambiguity to plan doc, notify Ash — never guess |
| Carry-over work | Add carry-over note at top of next day's functional plan |
| Workflow instruction change mid-session | Finish current session with current instructions, pick up new instructions next session |

---

## Notification email format

All notification emails must:
- Come from the Gmail account configured in `GOOGLE_CREDENTIALS`
- Be sent to: ayesha@limemint.ai
- Include a direct Drive or GitHub link — never make Ash hunt for documents
- Be concise — one paragraph maximum for the body

