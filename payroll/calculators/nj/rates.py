"""
New Jersey tax rates — source of truth.

All rates sourced from official publications.
The research agent checks these against current published rates every ~2 months.

Last verified: May 2026
Sources:
  - NJ income tax: https://www.nj.gov/treasury/taxation/
  - NJ SDI/FLI/UI: https://www.nj.gov/labor/
  - Federal: https://www.irs.gov/
"""

FEDERAL_TAX_YEAR = 2024

# --- Federal Rates ---

FEDERAL_BRACKETS_SINGLE = [
    # (upper_limit, rate) — last entry upper_limit=None means no cap
    (11_600,   0.10),
    (47_150,   0.12),
    (100_525,  0.22),
    (191_950,  0.24),
    (243_725,  0.32),
    (609_350,  0.35),
    (None,     0.37),
]

FEDERAL_BRACKETS_MARRIED_FILING_JOINTLY = [
    (23_200,   0.10),
    (94_300,   0.12),
    (201_050,  0.22),
    (383_900,  0.24),
    (487_450,  0.32),
    (731_200,  0.35),
    (None,     0.37),
]

FEDERAL_STANDARD_DEDUCTION_SINGLE = 14_600
FEDERAL_STANDARD_DEDUCTION_MFJ = 29_200

# FICA
SOCIAL_SECURITY_RATE = 0.062
SOCIAL_SECURITY_WAGE_BASE = 168_600  # 2024
MEDICARE_RATE = 0.0145
ADDITIONAL_MEDICARE_RATE = 0.009
ADDITIONAL_MEDICARE_THRESHOLD_SINGLE = 200_000

# --- New Jersey Rates ---

NJ_BRACKETS_SINGLE = [
    (20_000,   0.014),
    (35_000,   0.0175),
    (40_000,   0.035),
    (75_000,   0.05525),
    (500_000,  0.0637),
    (1_000_000, 0.0897),
    (None,     0.1075),
]

NJ_BRACKETS_MARRIED_FILING_JOINTLY = [
    (20_000,   0.014),
    (50_000,   0.0175),
    (70_000,   0.0245),
    (80_000,   0.035),
    (150_000,  0.05525),
    (500_000,  0.0637),
    (1_000_000, 0.0897),
    (None,     0.1075),
]

NJ_STANDARD_DEDUCTION_SINGLE = 1_000
NJ_STANDARD_DEDUCTION_MFJ = 2_000
NJ_PERSONAL_EXEMPTION_SINGLE = 1_000
NJ_PERSONAL_EXEMPTION_MFJ = 2_000

# NJ SDI (State Disability Insurance) — employee contribution
NJ_SDI_RATE = 0.0009
NJ_SDI_WAGE_BASE = 161_400  # 2024

# NJ FLI (Family Leave Insurance) — employee contribution
NJ_FLI_RATE = 0.0006
NJ_FLI_WAGE_BASE = 161_400  # 2024

# NJ UI/WF/SWF — employee contribution (UI + Workforce Development + Supplemental WD)
NJ_UI_EMPLOYEE_RATE = 0.00425
NJ_UI_WAGE_BASE = 42_300  # 2024
