# Changelog

All notable changes to the Payroll System are documented here.
Updated automatically by the daily build agent after each successful session.

Format: `## YYYY-MM-DD — Day N: <feature name>`

---

## 2026-05-08 — Day 2: Federal income tax calculator

**Added**
- `payroll/calculators/federal/calculator.py` — `calculate_federal_income_tax(gross_pay, filing_status, pay_frequency)`
- IRS Percentage Method (Pub. 15-T 2024), annualisation approach
- Filing statuses: `SINGLE`, `MARRIED_FILING_JOINTLY`
- Pay frequencies: `WEEKLY` (52), `BI_WEEKLY` (26), `SEMI_MONTHLY` (24), `MONTHLY` (12)
- 6 tests: standard bracket, zero withholding, 22% bracket, MFJ, top bracket (35%+37%), frequency consistency
- `FEDERAL_TAX_YEAR = 2024` constant added to `rates.py`

**Changed**
- `payroll/tests.py` restructured to `payroll/tests/` directory; Day 1 tests moved to `test_health_check.py`

*Annualisation method chosen deliberately over cumulative wages method — Ash reviewed the trade-off 2026-05-08.*

---

## 2026-05-08 — Day 1: Health check endpoint

**Added**
- `GET /api/v1/health/` returns `{"status": "ok", "service": "payroll-system"}` with HTTP 200
- 3 tests in `payroll/tests.py` covering status code, status field, and service name — all passing
- Feature branch `feature/2026-05-08-health-check` — PR open for review

*The endpoint and tests were scaffolded in Session 0; this session confirmed the test suite passes cleanly and the API contract is correct.*

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
