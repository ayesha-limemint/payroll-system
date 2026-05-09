"""
New Jersey tax rates - source of truth.

All rates sourced from official publications.
The research agent checks these against current published rates every ~2 months.

Last verified: May 2026
Sources:
  - NJ income tax: https://www.nj.gov/treasury/taxation/
  - NJ SDI/FLI/UI: https://www.nj.gov/labor/ea/employer-services/rate-info/
  - Federal brackets/deductions (2026): IRS Rev. Proc. 2025-32 (tax year 2026)
  - Federal brackets/deductions (2025): IRS Rev. Proc. 2024-40 (tax year 2025)
  - Federal FICA: SSA contribution and benefit base announcement 2026
  - One Big Beautiful Bill Act (P.L. 119-21): permanently extends TCJA bracket
    structure; new tips/overtime/senior deductions are W-4 elections, not
    employer-calculated - no change to withholding methodology.
"""

from __future__ import annotations

from typing import Any

FEDERAL_TAX_YEAR = 2026

# Federal withholding - IRS Percentage Method (Publication 15-T), annualised per period.
# Multiple tax years: schedules keyed by year; default active year = FEDERAL_TAX_YEAR.
FEDERAL_SCHEDULES: dict[int, dict[str, Any]] = {
    2025: {
        "STANDARD_SINGLE": 15_000,
        "STANDARD_MFJ": 30_000,
        "BRACKETS_SINGLE": [
            (11_925, 0.10),
            (48_475, 0.12),
            (103_350, 0.22),
            (197_300, 0.24),
            (250_525, 0.32),
            (626_350, 0.35),
            (None, 0.37),
        ],
        "BRACKETS_MARRIED_FILING_JOINTLY": [
            (23_850, 0.10),
            (96_950, 0.12),
            (206_700, 0.22),
            (394_600, 0.24),
            (501_050, 0.32),
            (751_600, 0.35),
            (None, 0.37),
        ],
    },
    2026: {
        "STANDARD_SINGLE": 16_100,
        "STANDARD_MFJ": 32_200,
        "BRACKETS_SINGLE": [
            (12_400, 0.10),
            (50_400, 0.12),
            (105_700, 0.22),
            (201_775, 0.24),
            (256_225, 0.32),
            (640_600, 0.35),
            (None, 0.37),
        ],
        "BRACKETS_MARRIED_FILING_JOINTLY": [
            (24_800, 0.10),
            (100_800, 0.12),
            (211_400, 0.22),
            (403_550, 0.24),
            (512_450, 0.32),
            (768_700, 0.35),
            (None, 0.37),
        ],
    },
}


def supported_federal_tax_years() -> tuple[int, ...]:
    return tuple(sorted(FEDERAL_SCHEDULES.keys()))


def get_federal_withholding_schedule(tax_year: int) -> dict[str, Any]:
    """Bracket tuples and standard deductions for the given federal tax year."""
    try:
        return FEDERAL_SCHEDULES[tax_year]
    except KeyError as exc:
        supported = ", ".join(str(y) for y in supported_federal_tax_years())
        raise ValueError(
            f"Unsupported federal tax year: {tax_year}. Supported: {supported}"
        ) from exc


_active = get_federal_withholding_schedule(FEDERAL_TAX_YEAR)

# Active-year exports (backwards compatibility for imports that assume one schedule)
FEDERAL_BRACKETS_SINGLE = _active["BRACKETS_SINGLE"]
FEDERAL_BRACKETS_MARRIED_FILING_JOINTLY = _active["BRACKETS_MARRIED_FILING_JOINTLY"]
FEDERAL_STANDARD_DEDUCTION_SINGLE = _active["STANDARD_SINGLE"]
FEDERAL_STANDARD_DEDUCTION_MFJ = _active["STANDARD_MFJ"]

# FICA
SOCIAL_SECURITY_RATE = 0.062
SOCIAL_SECURITY_WAGE_BASE = 184_500  # 2026
MEDICARE_RATE = 0.0145
ADDITIONAL_MEDICARE_RATE = 0.009
ADDITIONAL_MEDICARE_THRESHOLD_SINGLE = 200_000

# --- New Jersey Rates ---
# NJ income tax brackets and rates unchanged for 2026.

NJ_BRACKETS_SINGLE = [
    (20_000, 0.014),
    (35_000, 0.0175),
    (40_000, 0.035),
    (75_000, 0.05525),
    (500_000, 0.0637),
    (1_000_000, 0.0897),
    (None, 0.1075),
]

NJ_BRACKETS_MARRIED_FILING_JOINTLY = [
    (20_000, 0.014),
    (50_000, 0.0175),
    (70_000, 0.0245),
    (80_000, 0.035),
    (150_000, 0.05525),
    (500_000, 0.0637),
    (1_000_000, 0.0897),
    (None, 0.1075),
]

NJ_STANDARD_DEDUCTION_SINGLE = 1_000
NJ_STANDARD_DEDUCTION_MFJ = 2_000
NJ_PERSONAL_EXEMPTION_SINGLE = 1_000
NJ_PERSONAL_EXEMPTION_MFJ = 2_000

# NJ SDI (Temporary Disability Insurance) ? employee contribution
NJ_SDI_RATE = 0.0019  # 0.19% for 2026 (was 0.09% in 2024, 0.23% in 2025)
NJ_SDI_WAGE_BASE = 171_100  # 2026 (was 161,400 in 2024)

# NJ FLI (Family Leave Insurance) ? employee contribution
NJ_FLI_RATE = 0.0023  # 0.23% for 2026 (was 0.06% in 2024, 0.33% in 2025)
NJ_FLI_WAGE_BASE = 171_100  # 2026 (was 161,400 in 2024)

# NJ UI/WF/SWF ? employee contribution (UI 0.3825% + WF/SWF 0.0425% = 0.425%)
NJ_UI_EMPLOYEE_RATE = 0.00425  # unchanged for 2026
NJ_UI_WAGE_BASE = 44_800  # 2026 (was 42,300 in 2024)
