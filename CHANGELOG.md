# Changelog

All notable changes to the Payroll System are documented here.
Updated automatically by the daily build agent after each successful session.

Format: `## YYYY-MM-DD — Day N: <feature name>`

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
