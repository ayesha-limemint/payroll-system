"""
Day 2 — Federal income tax calculator tests.

Each test maps to an approved scenario in the functional plan
(daily_briefs/2026-05-08-day2/01_functional_plan.md).

Withholding method: IRS Percentage Method (Publication 15-T),
annualisation approach. Per-period gross is annualised, brackets applied,
result divided back by pay periods. No YTD tracking — each period is
calculated independently (deliberate; see technical plan risk note 1).
"""
from django.test import TestCase
from payroll.calculators.federal.calculator import calculate_federal_income_tax
from payroll.calculators.nj import rates


class FederalIncomeTaxTest(TestCase):

    # --- Scenario 1 ---
    # Single filer, $1,000/week (annual $52,000).
    # Taxable: 52000 - 16100 = 35900
    # 10% x 12400 = 1240.00  |  12% x 23500 = 2820.00  |  annual = 4060.00
    # Weekly: 4060.00 / 52 = 78.076... -> 78.08
    def test_single_weekly_standard(self):
        result = calculate_federal_income_tax(1000.00, "SINGLE", "WEEKLY")
        self.assertEqual(result, 78.08)

    # --- Scenario 2 ---
    # Annualised income ($10,400) below standard deduction ($14,600).
    # Taxable floors at zero -> $0.00 withholding.
    def test_single_below_deduction(self):
        result = calculate_federal_income_tax(200.00, "SINGLE", "WEEKLY")
        self.assertEqual(result, 0.00)

    # --- Scenario 3 ---
    # Single filer, $2,000/week (annual $104,000) — firmly in 22% bracket.
    # Taxable: 104000 - 16100 = 87900
    # 10% x 12400 = 1240.00  |  12% x 38000 = 4560.00  |  22% x 37500 = 8250.00
    # Annual = 14050.00  |  weekly = 14050.00 / 52 = 270.192... -> 270.19
    def test_single_in_22pct_bracket(self):
        result = calculate_federal_income_tax(2000.00, "SINGLE", "WEEKLY")
        self.assertEqual(result, 270.19)

    # --- Scenario 4 ---
    # MFJ, $3,000 bi-weekly (annual $78,000).
    # Taxable: 78000 - 32200 = 45800
    # 10% x 24800 = 2480.00  |  12% x 21000 = 2520.00  |  annual = 5000.00
    # Bi-weekly: 5000.00 / 26 = 192.307... -> 192.31
    def test_mfj_biweekly(self):
        result = calculate_federal_income_tax(3000.00, "MARRIED_FILING_JOINTLY", "BI_WEEKLY")
        self.assertEqual(result, 192.31)

    # --- Scenario 5 ---
    # Single, $31,250 semi-monthly (annual $750,000) — exercises 35% and 37%.
    # Taxable: 750000 - 16100 = 733900
    # 10%x12400=1240 | 12%x38000=4560 | 22%x55300=12166 | 24%x96075=23058
    # 32%x54450=17424 | 35%x384375=134531.25 | 37%x93300=34521
    # Annual = 227500.25  |  semi-monthly = 227500.25 / 24 = 9479.177... -> 9479.18
    def test_single_top_bracket(self):
        result = calculate_federal_income_tax(31250.00, "SINGLE", "SEMI_MONTHLY")
        self.assertEqual(result, 9479.18)

    # --- Scenario 6 ---
    # Same annual income ($52,000, SINGLE) across all four frequencies.
    # Per-period amounts are rounded individually so reconstructed annual
    # totals won't be exact — tolerance of $1.00.
    def test_frequency_consistency(self):
        annual_gross = 52000.00
        frequencies = {
            "WEEKLY": 52,
            "BI_WEEKLY": 26,
            "SEMI_MONTHLY": 24,
            "MONTHLY": 12,
        }
        reconstructed = {}
        for freq, periods in frequencies.items():
            per_period = calculate_federal_income_tax(
                annual_gross / periods, "SINGLE", freq
            )
            reconstructed[freq] = per_period * periods

        # All reconstructed annual taxes should agree within $1.00
        values = list(reconstructed.values())
        for v in values:
            self.assertAlmostEqual(v, values[0], delta=1.00)
    def test_explicit_2026_matches_implicit_default(self):
        default = calculate_federal_income_tax(1000.00, "SINGLE", "WEEKLY")
        explicit = calculate_federal_income_tax(
            1000.00, "SINGLE", "WEEKLY", tax_year=rates.FEDERAL_TAX_YEAR
        )
        self.assertEqual(default, explicit)

    def test_2025_schedule_differs_from_2026(self):
        y2026 = calculate_federal_income_tax(1000.00, "SINGLE", "WEEKLY", tax_year=rates.FEDERAL_TAX_YEAR)
        y2025 = calculate_federal_income_tax(1000.00, "SINGLE", "WEEKLY", tax_year=2025)
        self.assertEqual(y2026, 78.08)
        self.assertEqual(y2025, 80.80)
        self.assertNotEqual(y2025, y2026)

