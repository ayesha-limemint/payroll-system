# Phase 5 — Technical Plan

## Before writing anything — think first

Do not start filling in the template immediately. Work through these
questions in your reasoning before producing any output:

1. **Understand the codebase first.**
   Before designing anything, read the existing structure:
   - `payroll/calculators/` — what patterns are already established?
   - `payroll/api/` — what does the existing API look like?
   - `payroll/tests.py` — what test patterns are already in use?
   The new feature must fit naturally into what already exists.
   Do not invent new patterns when existing ones work fine.

2. **Where exactly does this code live?**
   Name the specific files and functions before writing the template.
   If a new file is needed, justify why an existing file won't do.

3. **What is the API contract precisely?**
   Write out the exact request and response JSON before filling in the template.
   Think through: what happens with invalid input? What HTTP status codes apply?

4. **How do the test scenarios map to test methods?**
   For each scenario in the functional plan, name the exact test method
   and describe the assertion. If a scenario is ambiguous, resolve it now
   or flag it as a blocker — do not carry ambiguity into implementation.

5. **Are there any dependencies or ordering constraints?**
   Does this feature depend on something not yet built?
   If so, flag it before proceeding — do not design around a missing foundation.

6. **What is the simplest correct implementation?**
   Resist the urge to over-engineer. The implementation that passes the
   approved tests and nothing more is the right implementation.

Only after working through all six questions should you fill in the template.

---

Read:
- The approved `01_functional_plan.md` from Drive
- `agents/instructions/tech_plan_template.md` from the repo

Fill in the template exactly. Do not free-form it.
Save to Drive: `daily_briefs/YYYY-MM-DD/02_technical_plan.md`

After saving, send Ash a Gmail notification:
- Subject: `[Milton] Technical plan ready for review — YYYY-MM-DD`
- Body: one-paragraph summary + direct Drive link

Then exit. Wait for approval before proceeding.
