"""
Day 2 — Federal income tax calculator tests.

Each test maps to an approved scenario in the functional plan
(daily_briefs/2026-05-08-day2/01_functional_plan.md).

Withholding method: IRS Percentage Method (Publication 15-T 2024),
annualisation approach. Per-period gross is annualised, brackets applied,
result divided back by pay periods. No YTD tracking — each period is
calculated independently (deliberate; see technical plan risk note 1).
"""
from django.test import TestCase
from payroll.calculators.federal.calculator import calculate_federal_income_tax


class FederalIncomeTaxTest(TestCase):

    # --- Scenario 1 ---
    # Single filer, $1,000/week (annual $52,000).
    # Taxable: 52000 - 14600 = 37400
    # 10% x 11600 = 1160.00  |  12% x 25800 = 3096.00  |  annual = 4256.00
    # Weekly: 4256.00 / 52 = 81.846... -> 81.85
    def test_single_weekly_standard(self):
        result = calculate_federal_income_tax(1000.00, "SINGLE", "WEEKLY")
        self.assertEqual(result, 81.85)

    # --- Scenario 2 ---
    # Annualised income ($10,400) below standard deduction ($14,600).
    # Taxable floors at zero -> $0.00 withholding.
    def test_single_below_deduction(self):
        result = calculate_federal_income_tax(200.00, "SINGLE", "WEEKLY")
        self.assertEqual(result, 0.00)

    # --- Scenario 3 ---
    # Single filer, $2,000/week (annual $104,000) — firmly in 22% bracket.
    # Taxable: 104000 - 14600 = 89400
    # 10% x 11600 = 1160.00  |  12% x 35550 = 4266.00  |  22% x 42250 = 9295.00
    # Annual = 14721.00  |  weekly = 14721.00 / 52 = 283.096... -> 283.10
    def test_single_in_22pct_bracket(self):
        result = calculate_federal_income_tax(2000.00, "SINGLE", "WEEKLY")
        self.assertEqual(result, 283.10)

    # --- Scenario 4 ---
    # MFJ, $3,000 bi-weekly (annual $78,000).
    # Taxable: 78000 - 29200 = 48800
    # 10% x 23200 = 2320.00  |  12% x 25600 = 3072.00  |  annual = 5392.00
    # Bi-weekly: 5392.00 / 26 = 207.384... -> 207.38
    def test_mfj_biweekly(self):
        result = calculate_federal_income_tax(3000.00, "MARRIED_FILING_JOINTLY", "BI_WEEKLY")
        self.assertEqual(result, 207.38)

    # --- Scenario 5 ---
    # Single, $31,250 semi-monthly (annual $750,000) — exercises 35% and 37%.
    # Taxable: 750000 - 14600 = 735400
    # 10%x11600=1160 | 12%x35550=4266 | 22%x53375=11742.50 | 24%x91425=21942
    # 32%x51775=16568 | 35%x365625=127968.75 | 37%x126050=46638.50
    # Annual = 230285.75  |  semi-monthly = 230285.75 / 24 = 9595.239... -> 9595.24
    def test_single_top_bracket(self):
        result = calculate_federal_income_tax(31250.00, "SINGLE", "SEMI_MONTHLY")
        self.assertEqual(result, 9595.24)

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
