"""
Day 9 — Pre-tax deductions (401k, health insurance) tests.

Each test maps to an approved scenario in the technical plan
(daily_briefs/2026-05-13/02_technical_plan.md).

Endpoint: POST /api/v1/calculate/
New optional field: deductions — array of {code, amount} objects.

Deductions reduce federal and NJ income taxable income.
FICA (SS, Medicare) and NJ contributions (SDI, FLI, UI) remain on gross_pay.
net_pay = gross_pay - total_taxes - sum(deduction amounts)
"""
import json

from django.test import TestCase


class PreTaxDeductionsTest(TestCase):

    def _post(self, payload):
        return self.client.post(
            "/api/v1/calculate/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    # --- Scenario 1 ---
    # No deductions — golden path must be fully backward-compatible.
    # deductions=[] (absent) behaves identically to the Day 6 golden path.
    #
    # Hand-verified:
    #   Federal: 130,000 annual; taxable 113,900 → 19,934/26 = 766.69
    #   NJ IT:   128,000 NJ taxable → 6,027.35/26 = 231.82
    #   SS/Medicare: 310.00 / 72.50
    #   SDI/FLI/UI: 9.50 / 11.50 / 21.25
    #   total_taxes=1423.26  net_pay=3576.74
    def test_no_deductions_golden_path_unchanged(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["deductions"], [])
        amounts = {t["code"]: t["amount"] for t in data["taxes"]}
        self.assertEqual(amounts["federal_income_tax"], "766.69")
        self.assertEqual(amounts["nj_income_tax"],      "231.82")
        self.assertEqual(amounts["social_security"],    "310.00")
        self.assertEqual(amounts["medicare"],           "72.50")
        self.assertEqual(data["total_taxes"], "1423.26")
        self.assertEqual(data["net_pay"],     "3576.74")

    # --- Scenario 2 ---
    # 401k $500 reduces federal and NJ income tax; FICA unchanged.
    #
    # Hand-verified (taxable = 4,500):
    #   Federal: 117,000 annual; taxable 100,900 → 16,910/26 = 650.38
    #   NJ IT:   115,000 NJ taxable → 5,199.25/26 = 199.97
    #   SS/Medicare: 310.00 / 72.50 (on gross 5,000 — unchanged)
    #   SDI/FLI/UI: 9.50 / 11.50 / 21.25 (on gross 5,000 — unchanged)
    #   total_taxes=1275.10  net_pay=5000−1275.10−500=3224.90
    def test_deduction_reduces_income_taxes_not_fica(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
            "deductions": [{"code": "401k", "amount": "500.00"}],
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        amounts = {t["code"]: t["amount"] for t in data["taxes"]}

        # Income taxes reduced (taxable income = 4,500 not 5,000)
        self.assertEqual(amounts["federal_income_tax"], "650.38")
        self.assertEqual(amounts["nj_income_tax"],      "199.97")

        # FICA unchanged (calculated on gross 5,000)
        self.assertEqual(amounts["social_security"], "310.00")
        self.assertEqual(amounts["medicare"],        "72.50")

        # NJ contributions unchanged (calculated on gross 5,000)
        self.assertEqual(amounts["nj_sdi"], "9.50")
        self.assertEqual(amounts["nj_fli"], "11.50")
        self.assertEqual(amounts["nj_ui"],  "21.25")

        # Totals
        self.assertEqual(data["total_taxes"], "1275.10")
        self.assertEqual(data["net_pay"],     "3224.90")

        # Deduction passed through in response
        self.assertEqual(len(data["deductions"]), 1)
        self.assertEqual(data["deductions"][0]["code"],   "401k")
        self.assertEqual(data["deductions"][0]["amount"], "500.00")

    # --- Scenario 3 ---
    # Multiple deductions (401k $300 + health_insurance $200) combine to $500.
    # Income tax result is identical to Scenario 2 (same total taxable income).
    # Both deduction objects appear in the response.
    def test_multiple_deductions_combine(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
            "deductions": [
                {"code": "401k",             "amount": "300.00"},
                {"code": "health_insurance", "amount": "200.00"},
            ],
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        amounts = {t["code"]: t["amount"] for t in data["taxes"]}

        # Combined $500 deduction → same income tax as Scenario 2
        self.assertEqual(amounts["federal_income_tax"], "650.38")
        self.assertEqual(amounts["nj_income_tax"],      "199.97")

        # FICA unchanged
        self.assertEqual(amounts["social_security"], "310.00")
        self.assertEqual(amounts["medicare"],        "72.50")

        self.assertEqual(data["total_taxes"], "1275.10")
        self.assertEqual(data["net_pay"],     "3224.90")

        # Both deduction objects in response
        self.assertEqual(len(data["deductions"]), 2)
        codes = [d["code"] for d in data["deductions"]]
        self.assertIn("401k",             codes)
        self.assertIn("health_insurance", codes)

    # --- Scenario 4 ---
    # Large $2,000 401k deduction — FICA and NJ contributions must stay on gross.
    # This test is the explicit invariant check: even a large deduction
    # must not affect the five wage-based contributions.
    #
    # The first assertion proves the deduction was actually processed (income tax
    # is lower than the golden path $766.69). Without that anchor, the FICA checks
    # would always pass trivially — they don't change whether or not deductions work.
    def test_fica_and_nj_contributions_unaffected_by_large_deduction(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
            "deductions": [{"code": "401k", "amount": "2000.00"}],
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        amounts = {t["code"]: t["amount"] for t in data["taxes"]}

        # Anchor: prove the deduction was processed — federal income tax must be lower
        # than the no-deduction golden path ($766.69). If deductions are ignored,
        # this assertion fails, which is the correct RED behaviour.
        self.assertNotEqual(amounts["federal_income_tax"], "766.69",
                            "Deduction was not applied — federal income tax unchanged")

        # Social Security: 5,000 × 6.2% = 310.00 (gross, not 3,000)
        self.assertEqual(amounts["social_security"], "310.00")
        # Medicare: 5,000 × 1.45% = 72.50 (gross, not 3,000)
        self.assertEqual(amounts["medicare"], "72.50")
        # NJ SDI: 5,000 × 0.19% = 9.50
        self.assertEqual(amounts["nj_sdi"], "9.50")
        # NJ FLI: 5,000 × 0.23% = 11.50
        self.assertEqual(amounts["nj_fli"], "11.50")
        # NJ UI: 5,000 × 0.425% = 21.25
        self.assertEqual(amounts["nj_ui"], "21.25")

    # --- Scenario 5 ---
    # Same $2,000 deduction: verify net_pay formula and income tax bracket crossing.
    # The $2,000 deduction pushes taxable income from $5,000 to $3,000,
    # crossing from the 24% federal bracket zone into the 22% bracket.
    #
    # Hand-verified (taxable = 3,000):
    #   Federal: 78,000 annual; taxable 61,900 → 8,330/26 = 320.38
    #   NJ IT:   76,000 NJ taxable → 2,714.95/26 = 104.42
    #   SS/Medicare/SDI/FLI/UI unchanged (gross 5,000)
    #   total_taxes: 320.38+310.00+72.50+104.42+9.50+11.50+21.25 = 849.55
    #   net_pay = 5,000 − 849.55 − 2,000.00 = 2,150.45
    def test_net_pay_formula_and_bracket_crossing(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
            "deductions": [{"code": "401k", "amount": "2000.00"}],
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        amounts = {t["code"]: t["amount"] for t in data["taxes"]}

        # Income taxes at reduced taxable income
        self.assertEqual(amounts["federal_income_tax"], "320.38")
        self.assertEqual(amounts["nj_income_tax"],      "104.42")

        # Summary
        self.assertEqual(data["total_taxes"], "849.55")
        # net_pay = gross − total_taxes − total_deductions
        self.assertEqual(data["net_pay"], "2150.45")
