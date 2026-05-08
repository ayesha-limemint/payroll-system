# Phase 3 — Functional Plan

## Before writing anything — think first

Do not start writing the plan immediately. Work through these questions
in your reasoning before producing any output:

1. **What exactly is the feature?**
   Re-read the backlog item or request file carefully. What is the precise
   scope — not what you assume, what is actually written?

2. **What are the real-world rules?**
   For anything involving tax calculations: what does the actual law say?
   Are the rates in `payroll/calculators/nj/rates.py` correct for this feature?
   If uncertain, search for the authoritative source before proceeding.

3. **What are the edge cases?**
   Think through at least 3 edge cases before writing scenarios.
   Examples: zero income, income exactly at a bracket boundary, maximum
   wage base, different filing statuses, pre-tax deductions affecting the base.

4. **What could go wrong?**
   What is the most likely mistake a developer would make implementing this?
   Make sure the test scenarios catch that mistake.

5. **What is explicitly out of scope?**
   Be precise. Vague out-of-scope lists lead to scope creep.

Only after working through all five questions should you write the plan document.

---

## If you have questions before writing

If any of the five questions above cannot be answered confidently —
the scope is unclear, a tax rule is ambiguous, or a requirement conflicts
with something already built — do NOT guess and do NOT write an incomplete plan.

Instead, write a questions document and save it to Drive:
`daily_briefs/YYYY-MM-DD/00_questions.md`

Format:

```
Status: AWAITING_ANSWERS
Written: YYYY-MM-DD HH:MM UTC

## Questions for Ash

**Q1:** [Your question — be specific, explain why it matters]

**Q2:** [Your question]
```

Send Ash a Gmail notification:
- Subject: `[Milton] Questions before I can plan — YYYY-MM-DD`
- Body: brief summary of what you need to know + direct Drive link

Then exit. Do not write the functional plan until answers arrive.

**Reading answers:** On the next run, check for `00_questions.md` with
Status: AWAITING_ANSWERS. Ash's answers will appear in the document
prefixed with `(Ash)` — for example:

```
**Q1:** Should pre-tax deductions reduce the NJ taxable income as well?

(Ash) Yes, same treatment as federal — deduct before applying state brackets.
```

Once all questions have an `(Ash)` answer, set Status: RESOLVED,
proceed to write the functional plan incorporating those answers.

---

## Writing the plan

Write the plan and save it to Drive:
`daily_briefs/YYYY-MM-DD/01_functional_plan.md`

The document must use this exact format:

```
Status: PENDING_REVIEW
Approved by: —
Ash Notes: —
Written: YYYY-MM-DD HH:MM UTC

## Feature
[Name of the feature being built today]

## Why
[Why this is next — backlog priority or Ash request]

## Test Scenarios
[Each scenario as: Given X, when Y, then Z]
- Scenario 1: ...
- Scenario 2: ...
- Scenario 3: ...

## What will be built
[Plain English description of the user-facing or API-facing behaviour]

## What will NOT be touched today
[Explicit list of things out of scope]

## Sources
[Any external references consulted — tax tables, IRS publications, etc.]
```

After saving, send Ash a Gmail notification:
- Subject: `[Milton] Functional plan ready for review — YYYY-MM-DD`
- Body: one-paragraph summary + direct Drive link

Then exit. Wait for approval before proceeding.
