# Phase 4 — Functional Approval Check

Read `01_functional_plan.md` Status field. Check once and act — do not poll.

**APPROVED**
→ Proceed immediately to Phase 5.

**CHANGES_REQUESTED**
→ Read every line prefixed with `Ash:` anywhere in the document.
→ Revise the plan to address every note.
→ Reset Status to PENDING_REVIEW, update the Written: timestamp.
→ Re-save the doc on Drive.
→ Send Slack notification: `[Milton] Revised functional plan ready — YYYY-MM-DD` + Drive link
→ Exit.

**PENDING_REVIEW**
→ Check the Written: timestamp:
  - Less than 24 hours ago → send Slack nudge: `[Milton] Functional plan is ready for your review — YYYY-MM-DD` + Drive link
  - More than 24 hours ago → send Slack reminder: `[Milton] Reminder: functional plan waiting over 24 hours — YYYY-MM-DD` + Drive link
→ Exit either way. Never proceed without APPROVED status.
