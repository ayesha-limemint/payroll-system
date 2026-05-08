# Phase 6 — Technical Approval Check

Same logic as Phase 4 but for `02_technical_plan.md`.

**APPROVED**
→ Proceed immediately to Phase 7.

**CHANGES_REQUESTED**
→ Read every `Ash:` prefixed line in the document.
→ Revise the plan to address every note.
→ Reset Status to PENDING_REVIEW, update the Written: timestamp.
→ Re-save the doc on Drive.
→ Send notification: `[Payroll Agent] Revised technical plan ready — YYYY-MM-DD`
→ Exit.

**PENDING_REVIEW**
→ Check the Written: timestamp:
  - Less than 24 hours ago → send nudge: `[Payroll Agent] Technical plan is ready for your review — YYYY-MM-DD`
  - More than 24 hours ago → send reminder: `[Payroll Agent] Reminder: technical plan waiting over 24 hours — YYYY-MM-DD`
→ Exit either way.

This is the final gate before any code is written.
Never proceed to Phase 7 without APPROVED status.
