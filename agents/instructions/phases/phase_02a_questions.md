# Phase 2a — Questions Pending

Milton has previously written a `00_questions.md` with Status: AWAITING_ANSWERS.
This phase checks whether Ash has responded.

## Check for answers

Read `daily_briefs/YYYY-MM-DD/00_questions.md`.

Scan every question block for an `(Ash)` response directly beneath it.
A question is answered when it has a line starting with `(Ash)`.

Example of an answered question:
```
**Q1:** Should pre-tax deductions reduce the NJ taxable income as well?

(Ash) Yes, same treatment as federal — deduct before applying state brackets.
```

## If ALL questions have an (Ash) answer

- Set Status: RESOLVED in `00_questions.md`
- Proceed immediately to Phase 3 to write the functional plan
- Incorporate every answer into the plan — do not ask the same question twice

## If ANY question is still unanswered

- Check the Written: timestamp in the doc
- Less than 24 hours ago → send nudge: `[Milton] Waiting on your answers before I can plan — YYYY-MM-DD`
- More than 24 hours ago → send reminder: `[Milton] Reminder: questions still awaiting your answers — YYYY-MM-DD`
- Exit either way. Do not write the functional plan until all questions are answered.
