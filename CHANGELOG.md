# Changelog

All notable changes to the Payroll System are documented here.
Updated automatically by the daily build agent after each successful session.

Format: `## YYYY-MM-DD — Day N: <feature name>`

---

## 2026-05-12 — Day 8: Additional Medicare Tax (0.9%)

**Added**
- Additional Medicare Tax (0.9%) to `calculate_fica()` — returns three values now: `social_security`, `medicare`, `additional_medicare`
- Employer withholding threshold: $200,000 per employee per year, regardless of filing status (IRS Pub. 15)
- Same inverted wage-base pattern as Social Security: `amt_wages = max(0, gross - max(0, 200_000 - ytd_gross))`
- `POST /api/v1/calculate/` taxes array grows from 7 to 8 items; `additional_medicare` inserted between `medicare` and `nj_income_tax`
- Line item always present in response (shows $0.00 for wages below threshold) — consistent with SS and NJ contributions
- 5 new tests: below threshold, crossing threshold, already above, exactly at boundary, end-to-end API; 48 total, all passing
- 4 screenshots: empty form, golden path ($0 AMT), AMT triggered ($45.00), AMT crossing threshold ($90.00)

*The Additional Medicare Tax has been waiting patiently since Day 3. It applies to fewer than 4% of wage earners and generates the most questions. The threshold is $200,000 from the employer's perspective — the employee reconciles MFJ vs. single at year-end. Three lines of arithmetic and a constant that has not changed since 2013. — Milton*

### Context
~40% of 200k window — medium session: ~45 tool calls, 4 Drive reads/writes, 0 web searches,
16 repo files read. Usage split between state recovery (Day 7 COMPLETE, starting Day 8),
plan writing (functional + technical plans with Pass B), RED→GREEN→regression cycle (48 tests),
Playwright screenshot capture (4 states), and PR. No web searches — AMT rate unchanged since 2013.

---

## 2026-05-11 — Day 7: Django UI calculator home at /

**Added**
- `GET /` — home page with NJ gross-to-net calculator form
- Form fields: Gross Pay, Filing Status (all 4 statuses), Pay Frequency (all 4 frequencies), YTD Gross, Pay Date (optional)
- Client-side JavaScript calls `POST /api/v1/calculate/` on submit; results rendered in-page without reload
- Results table: 7 tax line items, total taxes, net pay, tax year
- Error display for API 4xx responses
- No server-side POST handler — clean API/UI boundary
- 4 new tests (page loads, form fields, filing status options, pay frequency options); 43 total, all passing

### Context
~55% of 200k window — medium-heavy session: ~55 tool calls, 8 Drive reads/writes, 0 web searches,
15 repo files read. Usage split between state recovery (pulling main, determining Day 6 COMPLETE),
plan writing to Drive (functional + technical, both with Pass B cross-checks), RED→GREEN→regression
cycle, Playwright screenshot capture (5 states), and PR creation. No web searches — Day 7 introduces
no new tax rates. Slack plan notifications blocked by permission hook; completion notification sent
successfully.

---

## 2026-05-11 — Day 6: Core gross-to-net API endpoint

**Added**
- `POST /api/v1/calculate/` — complete NJ payroll breakdown in a single request
- Accepts `gross_pay`, `pay_frequency`, `filing_status`, `state`, `ytd_gross` (required), `pay_date` and `tax_year` (optional)
- Wires all four calculator modules: federal income tax, FICA, NJ income tax, NJ contributions
- Response: `taxes` array with 7 line items in canonical order (federal income → SS → Medicare → NJ income → NJ SDI → NJ FLI → NJ UI), `total_taxes`, `net_pay`, `deductions` (empty, ready for Phase 2), `tax_year` (resolved integer)
- All monetary values as decimal strings (`"766.69"`) — no floating-point drift
- `ytd_gross` passed independently to both `calculate_fica()` and `calculate_nj_contributions()` — each cap applied against its own wage base
- State validation: only NJ supported; unsupported states return 400
- Filing status and pay frequency normalised from lowercase API convention to uppercase calculator convention
- Django UI at `/calculate/` — accepts all inputs, renders full 7-line tax breakdown with net pay
- 5 tests: complete calculation (all 7 amounts verified), SS cap mid-year (ytd=$180k), missing ytd_gross→400, unsupported state→400, pay_date→tax_year resolution
- 39 tests total — full regression clean

*All five calculators are now connected. One POST call; seven deductions; one net figure. The hard part was always the order of operations — that ytd_gross feeds both FICA and the NJ contribution caps independently, not the same bucket. Scenario 2 was written to catch exactly the developer who forgets that. — Milton*

### Context
~40% of 200k window — medium session: ~35 tool calls, 4 Drive reads/writes, 0 web searches,
12 repo files read. Bulk of time in implementation and test verification; plans written efficiently
given all calculator building blocks were already in place.

---

## 2026-05-10 — Day 5: NJ SDI, FLI, and UI contributions

**Added**
- `payroll/calculators/nj/nj_contributions.py` — `calculate_nj_contributions(gross_pay, ytd_gross=0)`
- Returns `{"nj_sdi": Decimal, "nj_fli": Decimal, "nj_ui": Decimal}` per pay period
- SDI: 0.19% on `min(gross_pay, max(0, 171_100 - ytd_gross))` — cumulative cap, 2026 rate
- FLI: 0.23% on same SDI/FLI wage base cap — same pattern, different rate
- UI/WF/SWF: 0.425% on `min(gross_pay, max(0, 44_800 - ytd_gross))` — lower wage base exhausts first
- All three caps applied independently against the same `ytd_gross`; pattern identical to FICA
- Django UI at `/nj-contributions/` — form accepts gross_pay and ytd_gross, displays contribution table
- 6 tests: below all caps, crosses UI base mid-period, UI exhausted/SDI+FLI active, all caps exhausted, crosses SDI/FLI base mid-period, zero gross
- 34 tests total — full regression clean

*Three flat rates, three wage bases, one ytd_gross. SDI and FLI share a base; UI has its own, substantially lower one. The interesting paycheck is the one where ytd crosses $44,800 mid-year — UI goes to zero while SDI and FLI keep going. The test suite catches that. — Milton*

### Context
~45% of 200k window — medium session: ~40 tool calls, 6 Drive reads/writes, 2 web searches,
10 repo files read. Usage split between Drive plan writing (functional + technical), UI
verification via preview tool, and the RED→GREEN→regression cycle.

---

## 2026-05-09 — Day 4: NJ state income tax calculator

**Added**
- `payroll/calculators/nj/nj_income_tax.py` — `calculate_nj_income_tax(gross_pay, filing_status, pay_frequency)`
- Returns a `Decimal` — NJ withholding for one pay period, rounded to 2dp (ROUND_HALF_UP)
- Algorithm: annualise gross pay → subtract standard deduction ($1,000 single / $2,000 MFJ) AND personal exemption ($1,000 / $2,000) → apply NJ progressive brackets → divide by pay periods
- Filing statuses: `SINGLE`, `MARRIED_FILING_JOINTLY`
- Pay frequencies: `WEEKLY` (52), `BI_WEEKLY` (26), `SEMI_MONTHLY` (24), `MONTHLY` (12)
- NJ brackets (2026): 7 levels for single (1.4% → 10.75%), 8 levels for MFJ (1.4% → 10.75%)
- 6 tests: SINGLE weekly, MFJ bi-weekly, SINGLE monthly top bracket (10.75%), MFJ semi-monthly, bracket boundary at $40k taxable, zero gross
- 28 tests total — full regression clean

*NJ turns out to have more bracket layers than federal — seven for single filers, topping out at 10.75% above $1M. The combination of standard deduction plus personal exemption is the trap; the test at exactly $40,000 taxable is there for exactly that reason. — Milton*

### Context
~70% of 200k window — heavy session: ~35 tool calls, 8 Drive reads/writes, 3 web searches,
12 repo files read. Usage driven by state-machine recovery (Day 3 cleanup), dual plan
documents written to Drive, and a full RED→GREEN→regression cycle.

---

## 2026-05-09 — Day 3: FICA contributions

**Added**
- `payroll/calculators/federal/fica.py` — `calculate_fica(gross_pay, ytd_gross=0)`
- Returns `{"social_security": Decimal, "medicare": Decimal}` per pay period
- Social Security: 6.2% on `min(gross_pay, max(0, SOCIAL_SECURITY_WAGE_BASE - ytd_gross))` — correct annual cumulative cap
- Medicare: 1.45% on all gross wages, no cap
- `ytd_gross` defaults to 0 (first paycheck of year); callers supply YTD for mid-year accuracy
- 6 tests: no prior earnings (weekly), within remaining cap, exceeds remaining cap (SS truncated / Medicare full), wage base exhausted, zero income, bi-weekly no prior earnings
- 22 tests total — full regression clean

**Design correction:** Initial plan used a per-period cap (wage_base / pay_periods). Ash correctly identified this as inaccurate for mid-year hires, bonuses, and variable pay. Revised to proper YTD cumulative approach. `pay_frequency` removed from signature (unused once per-period approximation is gone).

*FICA turns out to be the most honest tax in the system — flat rates, one wage base, and it stops when it has enough. The wage base stops Social Security but not Medicare. Congress was specific about that distinction. — Milton*

---

## 2026-05-08 — Day 2: Federal income tax calculator

**Added**
- `payroll/calculators/federal/calculator.py` — `calculate_federal_income_tax(gross_pay, filing_status, pay_frequency)`
- IRS Percentage Method (Pub. 15-T), annualisation approach — annualise gross, apply brackets, divide back down
- Filing statuses: `SINGLE`, `MARRIED_FILING_JOINTLY`
- Pay frequencies: `WEEKLY` (52), `BI_WEEKLY` (26), `SEMI_MONTHLY` (24), `MONTHLY` (12)
- 6 tests: standard bracket, zero withholding, 22% bracket, MFJ, top bracket (35%+37%), frequency consistency
- `FEDERAL_TAX_YEAR` constant in `rates.py` — policy test ensures it tracks the current calendar year

**Changed**
- `payroll/tests.py` restructured to `payroll/tests/` directory; Day 1 tests moved to `test_health_check.py`

*Congress has had since 1913 to simplify the federal bracket structure and has elected not to.
Annualisation method chosen over cumulative wages — Ash reviewed the trade-off 2026-05-08.
The 37% bracket is implemented and tested. It remains, as ever, someone else's problem.*

---

## 2026-05-08 — Day 1: Health check endpoint

**Added**
- `GET /api/v1/health/` returns `{"status": "ok", "service": "payroll-system"}` with HTTP 200
- 3 tests covering status code, status field, and service name — all passing

*Every API needs a health check. This one does exactly what it says and nothing more,
which makes it the most honest endpoint we will ever write.*

---

## 2026-05-07 — Session 0: Project scaffold

**Added**
- GitHub repo: https://github.com/ayesha-limemint/payroll-system
- Django 6 + Python 3.13 project scaffold with Django REST Framework
- `CLAUDE.md` — agent bootstrap entry point
- `agents/instructions/daily_agent.md` — full daily loop workflow instructions
- `agents/instructions/research_agent.md` — research agent workflow instructions
- `agents/instructions/tech_plan_template.md` — technical plan template
- `agents/lib/` — ADC-based helpers for Drive, Gmail, GitHub, state machine
- `payroll/calculators/nj/rates.py` — NJ and federal tax rates (2024)
- `payroll/api/` — API structure with health check endpoint
- `payroll/tests.py` — Day 1 health check test cases (3 passing)
- `.github/workflows/ci.yml` — CI runs full test suite on every push
- Google Drive folder structure created

## 2026-05-07 — Session 0: Architecture update

**Changed**
- Removed GitHub Actions daily and research triggers — replaced by Claude Code Routines
- Routines run on Anthropic's cloud infrastructure on subscription, no API cost
- `agents/lib/drive_client.py` — updated to use ADC instead of service account JSON
- `agents/lib/gmail_client.py` — updated to use ADC instead of service account JSON
- `requirements.txt`, `.env.example`, `.gitignore`
- Google Drive folder structure created
