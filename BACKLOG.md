# Payroll System — Backlog

> This is the single source of truth for what Milton builds next.
> Stored in the repo so every change is version controlled.
> Milton reads this at the start of every session to select the next item.
> Milton updates this after every session to mark progress.
> Ash can reorder, add, or annotate items at any time.

---

## How to read this

- `[ ]` — not started
- `[~]` — in progress (Milton sets this when a session begins)
- `[x]` — complete (Milton sets this after a successful PR is merged)

Items are in priority order. Milton always picks the first `[ ]` item
unless Ash has dropped a file in `requests/pending/` — those take priority.

Each item includes a **Context** section so Milton understands the why,
not just the what. This matters for planning decisions.

---

## Phase 1 — Foundation (Week 1)

### [x] Session 0 — Project scaffold
**Goal:** Django project structure, agent instructions, CI, Google Drive setup.
**Context:** Done. The repo exists. The Routine exists. Milton is reading this.

---

### [ ] Day 1 — Health check endpoint
**Goal:** `GET /api/v1/health` returns `{"status": "ok", "service": "payroll-system"}`
**Context:** Every API needs a health check. This also verifies the Django
setup is correct, the URL routing works, DRF is configured, and CI is green
before we touch any real payroll logic. Start here — always.
**Acceptance:** 3 tests passing. CI green on GitHub.
**Out of scope:** Authentication, any payroll calculation.

---

### [ ] Day 2 — Federal income tax calculator
**Goal:** Calculate federal income tax withholding for a given gross income,
filing status, and pay frequency.
**Context:** Federal tax is the foundation everything else builds on. It must
be correct before NJ state tax is layered on top. Use the brackets in
`payroll/calculators/nj/rates.py` (FEDERAL_BRACKETS_SINGLE and
FEDERAL_BRACKETS_MARRIED_FILING_JOINTLY). The standard deduction is applied
before bracket calculation. Pay attention to annualisation — withholding is
calculated on an annualised basis then divided by pay periods.
**Acceptance:** Test scenarios covering single and MFJ, multiple income levels
including bracket boundaries, and all pay frequencies (weekly, bi-weekly,
semi-monthly, monthly).
**Out of scope:** Additional Medicare tax, pre-tax deductions, NJ state tax.
**Depends on:** Day 1 complete.

---

### [ ] Day 3 — FICA contributions
**Goal:** Calculate Social Security and Medicare employee contributions.
**Context:** FICA is straightforward but has two important constraints:
Social Security has a wage base cap ($168,600 for 2024 — in rates.py).
Medicare has no cap but has an Additional Medicare Tax at high incomes
(0.9% over $200k single / $250k MFJ) — however, defer the additional
Medicare tax to a later day. Keep this day focused on the base rates only.
Both are a flat percentage of gross — no brackets, no deductions.
**Acceptance:** Tests covering wage below cap, wage at cap, wage above cap
for Social Security. Basic Medicare on various income levels.
**Out of scope:** Additional Medicare Tax (deferred), pre-tax deductions.
**Depends on:** Day 1 complete.

---

### [ ] Day 4 — NJ state income tax calculator
**Goal:** Calculate NJ state income tax withholding for a given gross income,
filing status, and pay frequency.
**Context:** NJ has 7 brackets (in rates.py under NJ_BRACKETS_*). The
calculation mirrors federal: annualise, apply standard deduction and personal
exemption, apply brackets, divide by pay periods. NJ standard deductions and
personal exemptions are modest ($1,000 single / $2,000 MFJ). The top bracket
of 10.75% kicks in at $1M+ — make sure the test scenarios include this.
**Acceptance:** Tests covering all filing statuses, multiple income levels,
bracket boundaries, and the top bracket.
**Out of scope:** Part-year residents, NJ SDI/FLI/UI (separate day).
**Depends on:** Day 2 complete (mirror the federal pattern).

---

### [ ] Day 5 — NJ SDI, FLI, and UI contributions
**Goal:** Calculate NJ State Disability Insurance, Family Leave Insurance,
and Unemployment Insurance employee contributions.
**Context:** All three are flat rates on gross wages up to a wage base
(all use the same $161,400 base for 2024, except UI which uses $42,300).
Rates are in rates.py. These are simple calculations but they must respect
the wage base — once gross YTD exceeds the wage base, contributions stop.
For now, assume no YTD tracking — calculate as if every pay period is
within the wage base. YTD tracking is a future item.
**Acceptance:** Tests covering wages below and above each wage base.
**Out of scope:** YTD wage base tracking, employer contributions.
**Depends on:** Day 1 complete.

---

### [ ] Day 6 — Core gross-to-net API endpoint
**Goal:** `POST /api/v1/calculate` wires all calculators together and returns
a complete gross-to-net breakdown.
**Context:** This is the main API endpoint — the reason the system exists.
It takes gross pay, filing status, pay frequency, and state (NJ for now)
and returns every deduction itemised. The response must be clean and
well-documented because external agents (CloudCoreWorks etc.) will call this.
Design the request/response schema carefully — it needs to be extensible
when more states are added.
**Acceptance:** End-to-end tests covering a complete NJ payroll calculation,
verifying every line item in the response. Schema validated.
**Out of scope:** Authentication, pre-tax deductions, YTD tracking.
**Depends on:** Days 2, 3, 4, 5 all complete.

---

### [ ] Day 7 — Django UI: calculator form
**Goal:** A simple web form at `/` that calls `POST /api/v1/calculate`
and displays the gross-to-net breakdown in a readable format.
**Context:** The UI is secondary to the API — it exists for manual testing
and demos, not as the primary interface. Keep it simple: a form with
gross pay, filing status, pay frequency inputs. A results table showing
every deduction. No authentication, no history, no styling framework needed
beyond basic readable HTML.
**Acceptance:** Form submits, results display correctly, matches API output.
**Out of scope:** Authentication, saved calculations, mobile optimisation.
**Depends on:** Day 6 complete.

---

## Phase 2 — Completeness (Week 2)

### [ ] Additional Medicare Tax (0.9%)
**Goal:** Apply the 0.9% Additional Medicare Tax for high earners.
**Context:** Deferred from Day 3. Applies to wages over $200,000 (single)
or $250,000 (MFJ). Employers withhold on wages over $200,000 regardless
of filing status — the employee reconciles at tax time.
**Depends on:** Day 3 complete.

---

### [ ] Pre-tax deductions
**Goal:** Support flat-dollar pre-tax deductions (401k, health insurance)
that reduce federal and NJ taxable income before bracket calculation.
**Context:** Pre-tax deductions (traditional 401k, health insurance premiums)
reduce the income subject to federal and state income tax. They do NOT
reduce FICA wages (SS and Medicare are calculated on gross). This distinction
is critical — get it wrong and every calculation is incorrect.
**Acceptance:** Tests verifying that deductions reduce income tax but not FICA.
**Depends on:** Days 2 and 4 complete.

---

### [ ] Multiple pay frequencies
**Goal:** Ensure all calculators correctly handle weekly, bi-weekly,
semi-monthly, and monthly pay frequencies.
**Context:** Withholding is calculated by annualising gross pay, applying
brackets, then dividing back down by the number of pay periods.
Pay periods: weekly=52, bi-weekly=26, semi-monthly=24, monthly=12.
This should already be partially handled from Day 2 — this item is a
full regression pass to confirm all frequencies are correct across all
calculators.
**Depends on:** Day 6 complete.

---

### [ ] API input validation and error responses
**Goal:** Return clear, structured error responses for invalid input.
**Context:** External agents calling the API need predictable error formats.
Define a consistent error response schema. Validate: required fields present,
filing status is a known value, pay frequency is a known value, gross pay
is a positive number, state is a supported state.
**Depends on:** Day 6 complete.

---

## Phase 3 — Future (Unscheduled)

These items are defined so Milton understands the direction, but no
session should be started on them until Phase 2 is complete.

- [ ] YTD wage base tracking (SS cap, SDI/FLI/UI caps across pay periods)
- [ ] NJ part-year resident handling
- [ ] Additional states (PA, NY, CA) — architecture is ready
- [ ] Batch / multi-employee payroll calculations
- [ ] API authentication
- [ ] PostgreSQL migration (currently SQLite)
- [ ] Cloud deployment

---

## Backlog maintenance rules for Milton

After every completed session (Phase 11):
1. Mark the completed item `[x]`
2. Set the next item to `[~]` if starting it immediately, otherwise leave `[ ]`
3. If anything discovered during implementation affects priority, reorder and
   add a note explaining why
4. Commit the updated BACKLOG.md as part of the session commit

Never remove items — mark them `[x]` and leave the history intact.
