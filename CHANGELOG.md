# Changelog

All notable changes to the Payroll System are documented here.
Updated automatically by the daily build agent after each successful session.

Format: `## YYYY-MM-DD — Day N: <feature name>`

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
