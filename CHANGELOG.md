# Changelog

All notable changes to the Payroll System are documented here.
Updated automatically by the daily build agent after each successful session.

Format: `## YYYY-MM-DD — Day N: <feature name>`

---

## 2026-05-07 — Session 0: Project scaffold

**Added**
- Django project scaffold with Django REST Framework
- `CLAUDE.md` — agent bootstrap entry point
- `agents/instructions/daily_agent.md` — full daily loop workflow instructions
- `agents/instructions/research_agent.md` — research agent workflow instructions
- `agents/lib/` — helper stubs for Drive, Gmail, GitHub, state machine
- `payroll/calculators/nj/rates.py` — NJ and federal tax rates (2024)
- `payroll/api/` — API structure with health check endpoint stub
- `payroll/tests/test_health.py` — Day 1 test cases
- `.github/workflows/ci.yml` — CI runs full test suite on every push
- `.github/workflows/daily_trigger.yml` — 8am EST weekday notification trigger
- `.github/workflows/research_trigger.yml` — bi-monthly research trigger
- `requirements.txt`, `.env.example`, `.gitignore`
