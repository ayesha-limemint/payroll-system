"""
Day 4 — NJ state income tax calculator tests.

Each test maps to an approved scenario in the functional plan
(daily_briefs/2026-05-09/01_functional_plan_day4.md).

Method: annualise gross pay, subtract NJ standard deduction AND personal
exemption (both reduce taxable income), apply NJ progressive brackets,
divide by pay periods, round ROUND_HALF_UP to 2dp.

Filing statuses: SINGLE, MARRIED_FILING_JOINTLY
Rates from: payroll/calculators/nj/rates.py (verified May 2026, unchanged for 2026)
"""
from decimal import Decimal

from django.test import TestCase

from payroll.calculators.nj.nj_income_tax import calculate_nj_income_tax


class NJIncomeTaxTest(TestCase):

    # --- Scenario 1 ---
    # Single, $1,000/week (annual $52,000).
    # NJ taxable: 52000 - 1000 (std) - 1000 (personal) = 50,000
    # 1.4%  x 20000 = 280.00
    # 1.75% x 15000 = 262.50
    # 3.5%  x  5000 = 175.00
    # 5.525% x 10000 = 552.50
    # Annual = 1270.00  |  weekly = 1270.00 / 52 = 24.423... -> 24.42
    def test_single_weekly(self):
        result = calculate_nj_income_tax(1000.00, "SINGLE", "WEEKLY")
        self.assertEqual(result, Decimal("24.42"))

    # --- Scenario 2 ---
    # MFJ, $3,000 bi-weekly (annual $78,000).
    # NJ taxable: 78000 - 2000 - 2000 = 74,000
    # 1.4%  x 20000 = 280.00
    # 1.75% x 30000 = 525.00
    # 2.45% x 20000 = 490.00
    # 3.5%  x  4000 = 140.00
    # Annual = 1435.00  |  bi-weekly = 1435.00 / 26 = 55.192... -> 55.19
    def test_mfj_biweekly(self):
        result = calculate_nj_income_tax(3000.00, "MARRIED_FILING_JOINTLY", "BI_WEEKLY")
        self.assertEqual(result, Decimal("55.19"))

    # --- Scenario 3 ---
    # Single, $100,000/month (annual $1,200,000) — exercises top bracket (10.75%).
    # NJ taxable: 1200000 - 2000 = 1,198,000
    # 1.4%  x   20000 =    280.00
    # 1.75% x   15000 =    262.50
    # 3.5%  x    5000 =    175.00
    # 5.525% x   35000 =  1,933.75
    # 6.37% x  425000 = 27,072.50
    # 8.97% x  500000 = 44,850.00
    # 10.75% x 198000 = 21,285.00
    # Annual = 95,858.75  |  monthly = 95858.75 / 12 = 7988.229... -> 7988.23
    def test_single_monthly_top_bracket(self):
        result = calculate_nj_income_tax(100_000.00, "SINGLE", "MONTHLY")
        self.assertEqual(result, Decimal("7988.23"))

    # --- Scenario 4 ---
    # MFJ, $2,500 semi-monthly (annual $60,000).
    # NJ taxable: 60000 - 4000 = 56,000
    # 1.4%  x 20000 = 280.00
    # 1.75% x 30000 = 525.00
    # 2.45% x  6000 = 147.00
    # Annual = 952.00  |  semi-monthly = 952.00 / 24 = 39.666... -> 39.67
    def test_mfj_semi_monthly(self):
        result = calculate_nj_income_tax(2500.00, "MARRIED_FILING_JOINTLY", "SEMI_MONTHLY")
        self.assertEqual(result, Decimal("39.67"))

    # --- Scenario 5 ---
    # Single, $3,500/month — NJ taxable exactly $40,000.
    # Annual gross: 42,000  |  NJ taxable: 42000 - 2000 = 40,000
    # $40,000 is the upper bound of the 3.5% bracket (bracket boundary test).
    # 1.4%  x 20000 = 280.00
    # 1.75% x 15000 = 262.50
    # 3.5%  x  5000 = 175.00
    # Annual = 717.50  |  monthly = 717.50 / 12 = 59.791... -> 59.79
    def test_single_at_bracket_boundary(self):
        result = calculate_nj_income_tax(3500.00, "SINGLE", "MONTHLY")
        self.assertEqual(result, Decimal("59.79"))

    # --- Scenario 6 ---
    # Zero gross pay — no NJ tax owed.
    def test_zero_gross(self):
        result = calculate_nj_income_tax(0.00, "SINGLE", "WEEKLY")
        self.assertEqual(result, Decimal("0.00"))
