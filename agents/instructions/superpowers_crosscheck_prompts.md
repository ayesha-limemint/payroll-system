# Superpowers-aligned cross-check prompts

This repo follows the **think-before-acting** discipline from the open-source **[obra/superpowers](https://github.com/obra/superpowers)** project (MIT). We do not vendor the full skill tree; we apply a **minimal subset** at planning gates so the daily Routine does not ship shallow plans.

Use these **after** Pass A (draft plan) and **before** notifying Ash.

---

## Phase 3 — Functional plan — Pass B

Answer in writing (append to `01_functional_plan.md` under `## Pass B — Cross-check` or attach `01_functional_plan_crosscheck.md` on Drive):

1. **Scope discipline (Superpowers: smallest correct slice)**  
   What is the *smallest* change that satisfies the backlog item? What did you almost add that is out of scope?

2. **Playbook scan** — [`payroll_domain_playbook.md`](payroll_domain_playbook.md)  
   For each section (tax year vs pay date, effective dating, rounding, bases, non-goals): state **Pass / Fail / N/A** in one line. If Fail: fix Pass A or escalate to Ash with a question—no silent deferral.

3. **Assumption audit**  
   List three assumptions. For each: where is it stated in the backlog or prior approved docs? If it is not stated, mark **needs Ash** or remove.

4. **Edge cases**  
   Name the bracket boundary or wage-base case most likely to break the implementation. Which test scenario catches it?

---

## Phase 5 — Technical plan — Pass B

Answer in writing (append to `02_technical_plan.md` under `## Pass B — Cross-check`):

1. **Architecture conformance** — [`payroll_system_architecture.md`](payroll_system_architecture.md)  
   Files touched, API paths, calculator boundaries: **conforms / violates / out of scope with doc update**. If violates: revise Pass A of technical plan or update the architecture doc in-repo.

2. **Playbook conformance**  
   Does the JSON contract include **`tax_year`** / **`pay_date`** where withholding schedules apply? If not yet in scope, say so explicitly.

3. **Superpowers: simplest implementation**  
   What is the simplest design that passes the approved functional scenarios? What abstraction did you deliberately *not* add?

4. **Test mapping completeness**  
   Every functional scenario maps to a named test method—confirm **yes/no**. If no: fix before notifying Ash.

---

## Optional upstream integration

To install Superpowers skills globally (Claude Code / Cursor plugins), see the upstream README: [github.com/obra/superpowers](https://github.com/obra/superpowers). Repo-specific behavior remains governed by `agents/instructions/` phase files.
