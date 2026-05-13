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

### [x] Day 1 — Health check endpoint
**Goal:** `GET /api/v1/health` returns `{"status": "ok", "service": "payroll-system"}`
**Context:** Every API needs a health check. This also verifies the Django
setup is correct, the URL routing works, DRF is configured, and CI is green
before we touch any real payroll logic. Start here — always.
**Acceptance:** 3 tests passing. CI green on GitHub.
**Out of scope:** Authentication, any payroll calculation.

---

### [x] Day 2 — Federal income tax calculator
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

### [x] Day 3 — FICA contributions
**Goal:** Calculate Social Security and Medicare employee contributions.
**Context:** FICA is straightforward but has two important constraints:
Social Security has an annual wage base cap ($184,500 for 2026 — in rates.py).
The cap is cumulative: the calculator requires `ytd_gross` (year-to-date gross
wages before this period) to determine how much of the wage base remains.
Medicare (1.45%) has no wage base cap — it applies to every dollar of gross.
The Additional Medicare Tax (0.9% above $200k) is deferred to Phase 2.
**Acceptance:** Tests covering wage below cap, gross exceeding remaining cap
(SS truncated, Medicare full), wage base already exhausted, and zero income.
**Out of scope:** Additional Medicare Tax (deferred), pre-tax deductions.
**Depends on:** Day 1 complete.

---

### [x] Day 4 — NJ state income tax calculator
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

### [x] Day 5 — NJ SDI, FLI, and UI contributions
**Goal:** Calculate NJ State Disability Insurance, Family Leave Insurance,
and Unemployment Insurance employee contributions.
**Context:** All three are flat rates on gross wages up to an annual wage base
(SDI and FLI share $171,100 for 2026; UI uses $44,800 for 2026 — all in rates.py).
The caps are cumulative, exactly like Social Security in Day 3: the calculator
requires `ytd_gross` to determine how much of each wage base remains this year.
Use the same pattern as `calculate_fica`: `eligible = max(0, wage_base - ytd_gross)`,
then `contribution_wages = min(gross_pay, eligible)`.
Note that SDI, FLI, and UI have different wage bases, so all three caps are applied
independently against the same `ytd_gross` value.
**Acceptance:** Tests covering wages below each cap, gross exceeding each remaining
cap (contributions truncated), caps already exhausted, and zero income.
**Out of scope:** Employer contributions (employer pays separate UI/SDI rates).
**Depends on:** Day 1 complete.

---

### [x] Day 6 — Core gross-to-net API endpoint
**Goal:** `POST /api/v1/calculate/` wires all calculators together and returns
a complete gross-to-net breakdown.
**Context:** This is the main API endpoint — the reason the system exists.
External agents (CloudCoreWorks etc.) will call it, so the schema must be
clean, self-documenting, and extensible to additional states.
`ytd_gross` is a required input: FICA (Day 3) and NJ SDI/FLI/UI (Day 5) both
need it to apply their annual wage base caps correctly. The API passes it through
to each calculator. Callers (payroll systems, integrations) are responsible for
supplying the correct YTD figure for each employee.

Schema design is informed by industry research (Symmetry, PayrollTax, Gusto,
Finch, API Ninjas). The conventions below are deliberate — follow them exactly.

**Request schema:**
```json
{
  "gross_pay": "5000.00",
  "pay_frequency": "biweekly",
  "filing_status": "single",
  "state": "NJ",
  "ytd_gross": "45000.00",
  "pay_date": "2026-05-15"
}
```
`ytd_gross` — total gross wages paid to this employee so far this calendar year,
before this paycheck. Required. Use "0.00" for the first paycheck of the year.
`pay_date` is optional (defaults to current date, determines `tax_year`).
**Acceptance:** End-to-end tests covering a complete NJ payroll calculation,
verifying every line item in the response. Schema shape validated (all keys
present, correct types, decimal string format). At least one test with
mid-year ytd_gross that exercises the SS wage base cap.
**Out of scope:** Authentication, pre-tax deductions.
  "pay_date": "2026-05-15"
}
```
`pay_date` is optional (defaults to current date, determines `tax_year`).
`tax_year` is also accepted as an integer override, consistent with Day 2.

**Response schema — 200 OK:**
```json
{
  "gross_pay": "5000.00",
  "net_pay": "3612.45",
  "pay_frequency": "biweekly",
  "filing_status": "single",
  "state": "NJ",
  "tax_year": 2026,
  "taxes": [
    {"code": "federal_income_tax", "name": "Federal Income Tax",  "amount": "712.00"},
    {"code": "social_security",    "name": "Social Security",     "amount": "310.00"},
    {"code": "medicare",           "name": "Medicare",            "amount": "72.50"},
    {"code": "nj_income_tax",      "name": "NJ State Income Tax", "amount": "175.00"},
    {"code": "nj_sdi",             "name": "NJ SDI",              "amount": "45.00"},
    {"code": "nj_fli",             "name": "NJ FLI",              "amount": "18.00"},
    {"code": "nj_ui",              "name": "NJ UI",               "amount": "55.05"}
  ],
  "total_taxes": "1387.55",
  "deductions": []
}
```

Key decisions:
- All currency as **decimal strings** (`"712.00"`) — avoids floating-point drift
- Taxes as an **array of objects** `{code, name, amount}`, not flat fields —
  flat fields break when local taxes or additional Medicare are added later
- Tax order: federal income → FICA (SS, Medicare) → state income → state contributions
- `deductions` always present even when empty — Phase 2 pre-tax deductions
  populate it without a schema break
- Key inputs echoed in response — aids debugging and makes responses self-documenting
- `filing_status` values: `single`, `married_filing_jointly`,
  `married_filing_separately`, `head_of_household`
- `pay_frequency` values: `weekly`, `biweekly`, `semi_monthly`, `monthly`
- State: two-letter uppercase (`NJ`)
- Dates: ISO 8601 (`2026-05-15`)

See `agents/instructions/payroll_system_architecture.md` — "Response schema conventions"
section — for the canonical reference used in Pass B cross-checks.

**Acceptance:** End-to-end tests covering a complete NJ payroll calculation,
verifying every field and line item in the response against known-correct values.
Schema shape validated (all keys present, correct types, decimal string format).
**Out of scope:** Authentication, pre-tax deductions, YTD tracking.
**Depends on:** Days 2, 3, 4, 5 all complete.

---

### [x] Day 7 — Django UI: calculator form
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

### [~] Additional Medicare Tax (0.9%)
**Goal:** Apply the 0.9% Additional Medicare Tax for high earners.
**Context:** Deferred from Day 3. Applies to wages over $200,000 (single)
or $250,000 (MFJ). Employers withhold on wages over $200,000 regardless
of filing status — the employee reconciles at tax time.
`ytd_gross` is already in the API (Day 6) and calculator signatures, so this
calculator can simply check `if ytd_gross + gross_pay > 200_000` to determine
whether and how much additional Medicare applies this period. No new parameters needed.
**Depends on:** Day 3 complete.

---

### [~] Pre-tax deductions
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

- [ ] Annual W-2 reconciliation / cumulative accuracy (per-paycheck YTD is in place from Day 3; this covers full-year cross-period verification and edge cases like mid-year starts)
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
