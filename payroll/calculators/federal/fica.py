"""
FICA employee contribution calculator.

Social Security: 6.2% on gross wages up to the annual wage base (per-period
cap = SOCIAL_SECURITY_WAGE_BASE / pay_periods). No YTD tracking — each period
calculated independently (deliberate; see backlog Day 3 notes).

Medicare: 1.45% on all gross wages, no cap.

Additional Medicare Tax (0.9% above $200k) is deferred to Phase 2.
"""
from decimal import ROUND_HALF_UP, Decimal

from payroll.calculators.nj import rates

PAY_PERIODS = {
    "WEEKLY": 52,
    "BI_WEEKLY": 26,
    "SEMI_MONTHLY": 24,
    "MONTHLY": 12,
}


def calculate_fica(gross_pay, pay_frequency):
    """
    Return Social Security and Medicare employee contributions for one pay period.

    gross_pay      -- gross pay for this period (float or Decimal, dollars)
    pay_frequency  -- "WEEKLY", "BI_WEEKLY", "SEMI_MONTHLY", or "MONTHLY"

    Returns dict: {"social_security": Decimal, "medicare": Decimal}
    Raises KeyError if pay_frequency is not recognised (validation deferred to API layer).
    """
    gross = Decimal(str(gross_pay))
    periods = PAY_PERIODS[pay_frequency]

    per_period_cap = Decimal(str(rates.SOCIAL_SECURITY_WAGE_BASE)) / periods
    ss_wages = min(gross, per_period_cap)

    social_security = (ss_wages * Decimal(str(rates.SOCIAL_SECURITY_RATE))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    medicare = (gross * Decimal(str(rates.MEDICARE_RATE))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return {"social_security": social_security, "medicare": medicare}
