# Payroll domain playbook

Canonical invariants for this codebase. Phase 3 functional cross-check (Pass B) and Phase 5 technical cross-check must scan this document.

**Not legal advice.** Rules cite engineering behavior this system aims to model.

---

## Tax year vs pay date

- **Withholding** for a given paycheck generally follows rules **in effect for that pay event** (pay date / payroll period), not the developer’s “today” when writing code.
- The API accepts optional **`pay_date`** (ISO 8601). When `tax_year` is omitted, **`pay_date.year`** may be used as the withholding tax year (calendar-year simplification; see limitations below).
- Do not assume “whatever year is latest in `rates.py`” is correct for every check without an explicit pay date or tax year.

## Effective dating and rate tables

- Federal income tax brackets and standard deductions **change by tax year**. Schedules are keyed by **integer tax year** in [`payroll/calculators/nj/rates.py`](../payroll/calculators/nj/rates.py) (`FEDERAL_SCHEDULES`).
- Mid-year law changes that require **effective dates inside** a calendar year are **not** modeled until explicitly specified in a backlog item; until then, **one schedule per tax year** is the contract.
- Adding a new supported year requires published sources in the `rates.py` header and tests proving distinct behavior vs adjacent years where applicable.

## Rounding

- Federal withholding in this codebase rounds **per pay period** to **two decimal places** (currency). Annualisation uses exact floats for intermediate steps; document any future change to banker's rounding or per-component rules in the functional plan.

## Wage bases and caps

- **Social Security** applies only up to the annual wage base for that tax year (see SSA announcements). Reset each calendar/tax year per implementation when FICA is added.
- **Medicare** additional rate above threshold: model when those calculators exist; threshold is filing-status dependent.

## Pre-tax deductions and bases

- Order of operations (401k, health, etc.) affects taxable wages. Until modeled, state explicitly in plans what is **pre-tax for federal** vs **not applied**.

## New Jersey (when implemented)

- NJ income tax, SDI, FLI, and UI employee rates have **separate** wage bases and schedules; do not blend them with federal tables.
- Multi-year NJ schedules follow the same **versioned** pattern as federal when NJ calculators ship.

## Explicit non-goals (unless backlog says otherwise)

- Full **Form W-4** step-by-step mirroring (allowances vs 2020+ method) may be simplified to filing status + dollar inputs already exposed.
- **YTD accuracy** and lock-in for annual W-2 reconciliation: current federal income tax calculator uses **percentage method per period** without YTD; changing that is a separate feature.

---

*Playbook version: 1.0 — edit here when domain scope changes.*
