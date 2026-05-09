# Payroll system architecture (this repository)

Phase 5 technical cross-check (Pass B) compares every technical plan against this document. If a plan introduces a **new** pattern, either update this file in the same change or flag it for Ash.

---

## Layout

| Area | Path | Role |
|------|------|------|
| Django project | [`payroll_system/`](../payroll_system/) | Settings, root URLs |
| App | `payroll/` | Models, admin, API, calculators |
| REST API | `payroll/api/` | Versioned under `/api/v1/` |
| Calculators | `payroll/calculators/` | State-pluggable modules |
| Federal | `payroll/calculators/federal/` | Federal income tax (and future FICA) |
| New Jersey | `payroll/calculators/nj/` | NJ rates (`rates.py`) and future NJ calculator |
| Tests | `payroll/tests/` | Django `TestCase` modules |

**Rates:** Federal schedules keyed by tax year live in `payroll/calculators/nj/rates.py` (`FEDERAL_SCHEDULES`, `get_federal_withholding_schedule`). NJ statutory constants remain there until split out by a future refactor.

## API conventions

- Endpoints are under **`/api/v1/`** ([`payroll_system/urls.py`](../payroll_system/urls.py) includes `payroll.api.urls`).
- **`POST /api/v1/calculate/federal-income-tax/`** — federal withholding for one pay period; accepts optional **`tax_year`** and **`pay_date`** (see [`payroll/api/views.py`](../../payroll/api/views.py)).
- JSON request/response bodies; use DRF `api_view` / serializers as features grow.
- Calculation endpoints must accept **`tax_year`** and/or **`pay_date`** where withholding depends on the schedule (see playbook). Omitted → default active year from `FEDERAL_TAX_YEAR` or derived from `pay_date` per view contract.

## Calculator conventions

- Pure functions where possible: **`calculate_*`** takes numeric inputs and optional **`tax_year`** for schedule selection.
- Unsupported tax years: **`ValueError`** with a clear message listing supported years (or wrap in HTTP 400 at the API boundary).
- New states: add `payroll/calculators/<state>/` with the same discoverable layout; register in orchestration when gross-to-net aggregates exist.

## Testing

- **Test-first** for new behavior ([RED] / [GREEN] commit convention per `CLAUDE.md`).
- Policy tests: `FEDERAL_TAX_YEAR` must track the current calendar year in CI unless exempted (see `payroll/tests/test_rates_policy.py`).
- Multi-year: tests must assert **different outcomes** when schedules differ (e.g. 2025 vs 2026).

## Extension points

- **Gross-to-net orchestrator** (future): will call federal + FICA + state calculators with shared context (`tax_year`, `pay_date`, filing statuses).
- **UI** (future): calls same REST contracts as external agents.

---

*Architecture doc version: 1.0*
