# Phase 5 — Technical Plan

## Before writing anything — think first

Do not start filling in the template immediately. Work through these
questions in your reasoning before producing any output:

1. **Understand the codebase first.**
   Before designing anything, read the existing structure:
   - `payroll/calculators/` — what patterns are already established?
   - `payroll/api/` — what does the existing API look like?
   - `payroll/tests/` — what test patterns are already in use?
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

## Pass B — Cross-check (mandatory before notifying Ash)

Do **not** notify Ash after Pass A alone. Complete Pass B first.

1. Read [`agents/instructions/payroll_system_architecture.md`](../payroll_system_architecture.md).
2. Read [`agents/instructions/payroll_domain_playbook.md`](../payroll_domain_playbook.md).
3. Read [`agents/instructions/superpowers_crosscheck_prompts.md`](../superpowers_crosscheck_prompts.md) (Phase 5 section).
4. Append a section **exactly** titled `## Pass B — Cross-check` to `02_technical_plan.md` on Drive, answering every prompt in the Superpowers file for Phase 5 (architecture conformance + playbook + simplest implementation + test mapping).
5. If the design **violates** the architecture doc, either revise Pass A of the technical plan or update `payroll_system_architecture.md` in-repo in the same session and cite the change.

Only after Pass B is saved should you send the technical-plan notification.

---

Read:
- The approved `01_functional_plan.md` from Drive
- `agents/instructions/tech_plan_template.md` from the repo

Fill in the template exactly. Do not free-form it.
Save to Drive: `daily_briefs/YYYY-MM-DD/02_technical_plan.md` (include Pass B in the same file).

After saving **Pass A and Pass B**, send Ash a Slack notification (see Notification Rules in `daily_agent.md`):
```
[Milton] Technical plan written — YYYY-MM-DD
<Drive link to 02_technical_plan.md>
```

Then proceed immediately to Phase 7 (create feature branch). Do not exit or wait.
