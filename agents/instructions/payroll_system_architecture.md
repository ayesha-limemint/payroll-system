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

## Response schema conventions

These conventions apply to every calculation endpoint. Phase 5 Pass B checks conformance.

**Currency:** All monetary amounts as **decimal strings** with exactly 2 decimal places (`"712.00"`, not `712.0` or `712`). Avoids floating-point representation drift across language boundaries.

**Field naming:** `snake_case` throughout — request fields, response fields, tax codes, enum values.

**Tax breakdown:** Return taxes as an **array of objects**, never as flat top-level fields:
```json
"taxes": [
  {"code": "federal_income_tax", "name": "Federal Income Tax", "amount": "712.00"},
  {"code": "social_security",    "name": "Social Security",    "amount": "310.00"}
]
```
Flat fields (`"federal": 712.00`) break the schema when local taxes or additional Medicare are added. Array is unconditionally extensible.

**Tax ordering:** federal income → Social Security → Medicare → state income tax → state contributions (SDI, FLI, UI). Consistent across all responses.

**Deductions:** Parallel `deductions` array, same shape `{code, name, amount}`. Always present, even when empty. Pre-tax deductions (Phase 2) populate it without a schema change.

**Input echo:** Echo `gross_pay`, `pay_frequency`, `filing_status`, `state`, and resolved `tax_year` in every response. Makes responses self-documenting and aids debugging.

**Canonical enum values:**

| Field | Accepted values |
|-------|----------------|
| `filing_status` | `single`, `married_filing_jointly`, `married_filing_separately`, `head_of_household` |
| `pay_frequency` | `weekly`, `biweekly`, `semi_monthly`, `monthly` |
| `state` | Two-letter uppercase code (`NJ`, `CA`) |
| Dates | ISO 8601 string (`2026-05-15`) |

**`tax_year` resolution:** If `pay_date` is provided, derive `tax_year` from it. If `tax_year` is provided explicitly, use it. If neither, default to `FEDERAL_TAX_YEAR` from `rates.py`. Return the resolved `tax_year` in every response as an integer.

## Extension points

- **Gross-to-net orchestrator** (future): will call federal + FICA + state calculators with shared context (`tax_year`, `pay_date`, filing statuses).
- **UI** (future): calls same REST contracts as external agents.

---

*Architecture doc version: 1.1 — added response schema conventions (informed by Symmetry, PayrollTax, Gusto, Finch industry research)*
