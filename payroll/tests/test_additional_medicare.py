"""
Day 8 — Additional Medicare Tax (0.9%) tests.

Each test maps to a scenario approved in the 2026-05-12 functional plan.

Employer withholding rule: withhold 0.9% on wages paid above $200,000 in a
calendar year. The $200,000 threshold applies per employee per employer,
regardless of filing status. ytd_gross tracks cumulative wages before this period.

Calculation (same inverted pattern as SS wage base):
  remaining_before_amt = max(0, 200_000 - ytd_gross)
  amt_wages = max(0, gross_pay - remaining_before_amt)
  additional_medicare = amt_wages × 0.009
"""
import json
from decimal import Decimal

from django.test import TestCase

from payroll.calculators.federal.fica import calculate_fica


class AdditionalMedicareTaxTest(TestCase):

    # --- Scenario 1 ---
    # Wages well below $200,000 threshold — no AMT.
    # gross=5,000, ytd=0 → ytd+gross=5,000 < 200,000 → AMT=0.00
    def test_no_amt_below_threshold(self):
        result = calculate_fica(5000.00, ytd_gross=0)
        self.assertEqual(result["additional_medicare"], Decimal("0.00"))

    # --- Scenario 2 ---
    # Wages cross the $200,000 threshold this period.
    # gross=15,000, ytd=195,000
    # remaining_before_amt = max(0, 200,000 - 195,000) = 5,000
    # amt_wages = max(0, 15,000 - 5,000) = 10,000
    # AMT = 10,000 × 0.009 = 90.00
    def test_amt_crossing_threshold(self):
        result = calculate_fica(15_000.00, ytd_gross=195_000)
        self.assertEqual(result["additional_medicare"], Decimal("90.00"))

    # --- Scenario 3 ---
    # YTD already above $200,000 — full gross subject to AMT.
    # gross=5,000, ytd=210,000
    # remaining_before_amt = max(0, 200,000 - 210,000) = 0
    # amt_wages = max(0, 5,000 - 0) = 5,000
    # AMT = 5,000 × 0.009 = 45.00
    def test_amt_already_above_threshold(self):
        result = calculate_fica(5000.00, ytd_gross=210_000)
        self.assertEqual(result["additional_medicare"], Decimal("45.00"))

    # --- Scenario 4 ---
    # Wages exactly at $200,000 threshold — AMT not triggered (wages must EXCEED).
    # gross=200,000, ytd=0
    # remaining_before_amt = max(0, 200,000 - 0) = 200,000
    # amt_wages = max(0, 200,000 - 200,000) = 0
    # AMT = 0.00
    def test_amt_exactly_at_threshold(self):
        result = calculate_fica(200_000.00, ytd_gross=0)
        self.assertEqual(result["additional_medicare"], Decimal("0.00"))


class AdditionalMedicareTaxAPITest(TestCase):

    def _post(self, payload):
        return self.client.post(
            "/api/v1/calculate/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    # --- Scenario 5 ---
    # End-to-end: high earner, ytd=$200,000, gross=$5,000 → AMT=$45.00.
    # AMT must appear in taxes array between "medicare" and "nj_income_tax".
    # Total taxes array has 8 items.
    # AMT wages = max(0, 5000 - max(0, 200000-200000)) = 5000
    # AMT = 5000 × 0.009 = 45.00
    def test_amt_via_calculate_api(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "200000.00",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(len(data["taxes"]), 8)

        codes = [t["code"] for t in data["taxes"]]
        self.assertIn("additional_medicare", codes)

        amt_index = codes.index("additional_medicare")
        medicare_index = codes.index("medicare")
        nj_it_index = codes.index("nj_income_tax")
        self.assertGreater(amt_index, medicare_index)
        self.assertLess(amt_index, nj_it_index)

        amounts = {t["code"]: t["amount"] for t in data["taxes"]}
        self.assertEqual(amounts["additional_medicare"], "45.00")
