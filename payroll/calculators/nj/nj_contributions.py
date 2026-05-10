"""
NJ employee payroll contributions: SDI, FLI, and UI/WF/SWF.

All three are flat rates on gross wages up to an annual wage base.
Caps are cumulative — the caller supplies ytd_gross (total gross wages
paid before this period) so each cap is applied correctly mid-year.

Rates (2026, sourced from nj.gov/labor):
  SDI: 0.19% on first $171,100
  FLI: 0.23% on first $171,100
  UI/WF/SWF: 0.425% on first $44,800
"""
from decimal import ROUND_HALF_UP, Decimal

from payroll.calculators.nj import rates


def calculate_nj_contributions(gross_pay, ytd_gross=0):
    """
    Return NJ SDI, FLI, and UI employee contributions for one pay period.

    gross_pay  -- gross pay for this period (float or Decimal, dollars)
    ytd_gross  -- total gross wages already paid this calendar year before
                  this period (default 0 = first paycheck of the year)

    Returns dict: {"nj_sdi": Decimal, "nj_fli": Decimal, "nj_ui": Decimal}
    All values rounded to 2 decimal places (ROUND_HALF_UP).
    """
    gross = Decimal(str(gross_pay))
    ytd = Decimal(str(ytd_gross))

    def _contribution(wage_base, rate):
        eligible = max(Decimal("0"), Decimal(str(wage_base)) - ytd)
        wages = min(gross, eligible)
        return (wages * Decimal(str(rate))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    return {
        "nj_sdi": _contribution(rates.NJ_SDI_WAGE_BASE, rates.NJ_SDI_RATE),
        "nj_fli": _contribution(rates.NJ_FLI_WAGE_BASE, rates.NJ_FLI_RATE),
        "nj_ui":  _contribution(rates.NJ_UI_WAGE_BASE, rates.NJ_UI_EMPLOYEE_RATE),
    }
