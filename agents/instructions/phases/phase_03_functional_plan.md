# Phase 3 — Functional Plan

## Before writing anything — think first

Do not start writing the plan immediately. Work through these questions
in your reasoning before producing any output:

1. **What exactly is the feature?**
   Re-read the backlog item or request file carefully. What is the precise
   scope — not what you assume, what is actually written?

2. **What are the real-world rules?**
   For anything involving tax calculations: what does the actual law say?

   **Rate verification is mandatory before writing this plan.**
   Do not rely on `rates.py` without checking it first. The current date
   is in your session context — use it to determine the current tax year.

   Steps (complete these before writing a single line of the plan):
   a. Compare `FEDERAL_TAX_YEAR` in `rates.py` against the current year.
      If they differ, the file is presumed stale.
   b. Search irs.gov for "Publication 15-T [current year]" and verify
      federal brackets and standard deductions.
   c. Check ssa.gov for the current-year Social Security wage base.
   d. For NJ features: check nj.gov/labor for SDI/FLI/UI rates and
      nj.gov/treasury for any NJ income tax changes.
   e. If anything is stale: update `rates.py`, commit the correction,
      then proceed. Note the sources used in the rates.py file header.

   Only after rates are confirmed current should you write the plan.

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

## Pass B — Cross-check (mandatory before notifying Ash)

Do **not** notify Ash after Pass A alone. Complete Pass B first.

1. Read [`agents/instructions/payroll_domain_playbook.md`](../payroll_domain_playbook.md).
2. Read [`agents/instructions/superpowers_crosscheck_prompts.md`](../superpowers_crosscheck_prompts.md) (Phase 3 section).
3. Append a section **exactly** titled `## Pass B — Cross-check` to the same Drive document (`01_functional_plan.md`), answering every prompt in the Superpowers file for Phase 3. Include the playbook scan (**Pass / Fail / N/A** per section).
4. **Stop rule:** Any **Fail** on a playbook item requires revising Pass A or opening questions for Ash — no silent deferral.

Only after Pass B is saved should you send the functional-plan notification.

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

## Pass B — Cross-check
[Completed after Pass A — playbook scan + Superpowers prompts from agents/instructions/superpowers_crosscheck_prompts.md]
```

After saving **Pass A and Pass B**, send Ash a Slack notification (see Notification Rules in `daily_agent.md`):
```
[Milton] Functional plan written — YYYY-MM-DD
<Drive link to 01_functional_plan.md>
```

Then proceed immediately to Phase 5 (technical plan). Do not exit or wait.
