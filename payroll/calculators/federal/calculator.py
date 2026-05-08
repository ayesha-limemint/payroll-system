"""
Federal income tax withholding calculator.

Method: IRS Percentage Method, Publication 15-T (tax year 2024).
Each pay period is calculated independently via annualisation —
no YTD tracking. See rates.FEDERAL_TAX_YEAR for the effective tax year.
"""
from payroll.calculators.nj import rates

PAY_PERIODS = {
    "WEEKLY": 52,
    "BI_WEEKLY": 26,
    "SEMI_MONTHLY": 24,
    "MONTHLY": 12,
}

_STANDARD_DEDUCTIONS = {
    "SINGLE": rates.FEDERAL_STANDARD_DEDUCTION_SINGLE,
    "MARRIED_FILING_JOINTLY": rates.FEDERAL_STANDARD_DEDUCTION_MFJ,
}

_BRACKETS = {
    "SINGLE": rates.FEDERAL_BRACKETS_SINGLE,
    "MARRIED_FILING_JOINTLY": rates.FEDERAL_BRACKETS_MARRIED_FILING_JOINTLY,
}


def calculate_federal_income_tax(gross_pay, filing_status, pay_frequency):
    """
    Return federal income tax withholding for one pay period, rounded to 2dp.

    gross_pay     -- gross pay for this period (float, dollars)
    filing_status -- "SINGLE" or "MARRIED_FILING_JOINTLY"
    pay_frequency -- "WEEKLY", "BI_WEEKLY", "SEMI_MONTHLY", or "MONTHLY"
    """
    periods = PAY_PERIODS[pay_frequency]
    annual_gross = gross_pay * periods
    taxable = max(0.0, annual_gross - _STANDARD_DEDUCTIONS[filing_status])
    annual_tax = _apply_brackets(taxable, _BRACKETS[filing_status])
    return round(annual_tax / periods, 2)


def _apply_brackets(income, brackets):
    """Apply a progressive bracket schedule to taxable income."""
    tax = 0.0
    prev = 0.0
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
