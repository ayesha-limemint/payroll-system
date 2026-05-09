"""
New Jersey state income tax withholding calculator.

Method: annualise gross pay, subtract standard deduction and personal
exemption, apply NJ progressive brackets, divide by pay periods, round 2dp.

No YTD tracking — each period calculated independently (NJ income tax has no
annual wage base cap; annualisation alone determines the correct bracket).
Mirrors the federal income tax calculator pattern (Day 2).
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
    "SINGLE": (
        rates.NJ_STANDARD_DEDUCTION_SINGLE,
        rates.NJ_PERSONAL_EXEMPTION_SINGLE,
        rates.NJ_BRACKETS_SINGLE,
    ),
    "MARRIED_FILING_JOINTLY": (
        rates.NJ_STANDARD_DEDUCTION_MFJ,
        rates.NJ_PERSONAL_EXEMPTION_MFJ,
        rates.NJ_BRACKETS_MARRIED_FILING_JOINTLY,
    ),
}


def calculate_nj_income_tax(gross_pay, filing_status, pay_frequency):
    """
    Return NJ state income tax withholding for one pay period, rounded to 2dp.

    gross_pay     -- gross pay for this period (float or Decimal, dollars)
    filing_status -- "SINGLE" or "MARRIED_FILING_JOINTLY"
    pay_frequency -- "WEEKLY", "BI_WEEKLY", "SEMI_MONTHLY", or "MONTHLY"
    """
    if filing_status not in _FILING_KEYS:
        raise ValueError(
            f"filing_status must be one of {list(_FILING_KEYS)}, got {filing_status!r}"
        )

    standard, personal, brackets = _FILING_KEYS[filing_status]
    standard = Decimal(str(standard))
    personal = Decimal(str(personal))
    decimal_brackets = [
        (Decimal(str(upper)) if upper is not None else None, Decimal(str(rate)))
        for upper, rate in brackets
    ]

    gross = Decimal(str(gross_pay))
    periods = PAY_PERIODS[pay_frequency]
    annual_gross = gross * periods
    taxable = max(Decimal("0"), annual_gross - standard - personal)
    annual_tax = _apply_brackets(taxable, decimal_brackets)
    return (annual_tax / periods).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


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
