"""
Federal income tax withholding calculator.

Method: IRS Percentage Method, Publication 15-T. Each pay period is calculated
independently via annualisation ? no YTD tracking. Schedule selection uses
`tax_year` (defaults to `rates.FEDERAL_TAX_YEAR`).
"""
from decimal import ROUND_HALF_UP, Decimal

from payroll.calculators.nj import rates

PAY_PERIODS = {
    "WEEKLY": 52,
    "BI_WEEKLY": 26,
    "SEMI_MONTHLY": 24,
    "MONTHLY": 12,
}

_FILING_KEYS = {
    "SINGLE": ("STANDARD_SINGLE", "BRACKETS_SINGLE"),
    "MARRIED_FILING_JOINTLY": ("STANDARD_MFJ", "BRACKETS_MARRIED_FILING_JOINTLY"),
}


def calculate_federal_income_tax(
    gross_pay,
    filing_status,
    pay_frequency,
    tax_year=None,
):
    """
    Return federal income tax withholding for one pay period, rounded to 2dp.

    gross_pay     -- gross pay for this period (float, dollars)
    filing_status -- "SINGLE" or "MARRIED_FILING_JOINTLY"
    pay_frequency -- "WEEKLY", "BI_WEEKLY", "SEMI_MONTHLY", or "MONTHLY"
    tax_year      -- federal tax year for bracket/deduction tables (default: active year)
    """
    if filing_status not in _FILING_KEYS:
        raise ValueError(
            f"filing_status must be one of {list(_FILING_KEYS)}, got {filing_status!r}"
        )
    year = rates.FEDERAL_TAX_YEAR if tax_year is None else int(tax_year)
    sched = rates.get_federal_withholding_schedule(year)
    std_key, br_key = _FILING_KEYS[filing_status]
    standard = sched[std_key]
    brackets = sched[br_key]

    gross_pay = Decimal(str(gross_pay))
    standard = Decimal(str(standard))
    decimal_brackets = [
        (Decimal(str(upper)) if upper is not None else None, Decimal(str(rate)))
        for upper, rate in brackets
    ]

    periods = PAY_PERIODS[pay_frequency]
    annual_gross = gross_pay * periods
    taxable = max(Decimal("0"), annual_gross - standard)
    annual_tax = _apply_brackets(taxable, decimal_brackets)
    return (annual_tax / periods).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def resolve_federal_tax_year(tax_year=None, pay_date=None):
    """
    Choose withholding tax year from explicit tax_year, pay_date, or active default.

    If both tax_year and pay_date are provided and tax_year != pay_date.year, raises
    ValueError (caller maps to HTTP 400).
    """
    if tax_year is not None and pay_date is not None:
        if int(tax_year) != pay_date.year:
            raise ValueError(
                "tax_year must match the calendar year of pay_date when both are provided"
            )
        return int(tax_year)
    if tax_year is not None:
        return int(tax_year)
    if pay_date is not None:
        return pay_date.year
    return rates.FEDERAL_TAX_YEAR


def _apply_brackets(income, brackets):
    """Apply a progressive bracket schedule to taxable income."""
    tax = Decimal("0")
    prev = Decimal("0")
    for upper, rate in brackets:
        if upper is None:
            tax += (income - prev) * rate
            break
        if income <= upper:
            tax += (income - prev) * rate
            break
        tax += (upper - prev) * rate
        prev = upper
    return tax
