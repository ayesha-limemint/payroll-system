"""
FICA employee contribution calculator.

Social Security: 6.2% on gross wages up to the annual wage base, minus any
wages already subject to SS this year (ytd_gross). The $184,500 cap is annual
and cumulative — not a per-period limit.

Medicare: 1.45% on all gross wages, no cap.

Additional Medicare Tax (0.9% above $200k) is deferred to Phase 2.
"""
from decimal import ROUND_HALF_UP, Decimal

from payroll.calculators.nj import rates


def calculate_fica(gross_pay, ytd_gross=0):
    """
    Return Social Security and Medicare employee contributions for one pay period.

    gross_pay  -- gross pay for this period (float or Decimal, dollars)
    ytd_gross  -- total gross wages already paid this calendar year before this
                  period (default 0 — i.e. first paycheck of the year)

    Returns dict: {"social_security": Decimal, "medicare": Decimal}
    """
    gross = Decimal(str(gross_pay))
    ytd = Decimal(str(ytd_gross))

    ss_eligible = max(Decimal("0"), Decimal(str(rates.SOCIAL_SECURITY_WAGE_BASE)) - ytd)
    ss_wages = min(gross, ss_eligible)

    social_security = (ss_wages * Decimal(str(rates.SOCIAL_SECURITY_RATE))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    medicare = (gross * Decimal(str(rates.MEDICARE_RATE))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return {"social_security": social_security, "medicare": medicare}
