"""
Day 6 — Core gross-to-net API endpoint tests.

Each test maps to an approved scenario in the functional plan
(daily_briefs/2026-05-11/01_functional_plan.md).

Endpoint: POST /api/v1/calculate/
Returns a complete NJ gross-to-net breakdown: federal income tax, FICA,
NJ income tax, NJ SDI/FLI/UI, total taxes, and net pay.
"""
import json
from decimal import Decimal

from django.test import TestCase


class CalculateAPITest(TestCase):

    def _post(self, payload):
        return self.client.post(
            "/api/v1/calculate/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    # --- Scenario 1 ---
    # Golden path: single filer, $5,000 biweekly, ytd_gross=$0, NJ.
    # Verifies all 7 tax line items, schema shape, decimal string format,
    # total_taxes, net_pay, tax_year, and deductions=[].
    #
    # Hand-verified expected values:
    #   Federal:  annual=130,000; taxable=113,900; 10%×12,400+12%×38,000+22%×55,300+24%×8,200=19,934/26=766.69
    #   SS:       5,000×0.062=310.00
    #   Medicare: 5,000×0.0145=72.50
    #   NJ IT:    annual taxable=128,000; brackets → 6,027.35/26=231.82
    #   SDI/FLI/UI: 9.50 / 11.50 / 21.25
    #   Total:    1,423.26  Net: 3,576.74
    def test_complete_nj_calculation(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Top-level schema shape
        for key in ("gross_pay", "net_pay", "pay_frequency", "filing_status",
                    "state", "tax_year", "taxes", "total_taxes", "deductions"):
            self.assertIn(key, data, f"Missing key: {key}")

        # Echo fields
        self.assertEqual(data["gross_pay"], "5000.00")
        self.assertEqual(data["pay_frequency"], "biweekly")
        self.assertEqual(data["filing_status"], "single")
        self.assertEqual(data["state"], "NJ")
        self.assertEqual(data["tax_year"], 2026)
        self.assertEqual(data["deductions"], [])

        # Taxes array: 7 items in canonical order with code/name/amount keys
        self.assertEqual(len(data["taxes"]), 7)
        expected_codes = [
            "federal_income_tax", "social_security", "medicare",
            "nj_income_tax", "nj_sdi", "nj_fli", "nj_ui",
        ]
        for i, code in enumerate(expected_codes):
            self.assertEqual(data["taxes"][i]["code"], code)
            self.assertIn("name", data["taxes"][i])
            self.assertIn("amount", data["taxes"][i])

        # Tax amounts
        amounts = {t["code"]: t["amount"] for t in data["taxes"]}
        self.assertEqual(amounts["federal_income_tax"], "766.69")
        self.assertEqual(amounts["social_security"],    "310.00")
        self.assertEqual(amounts["medicare"],           "72.50")
        self.assertEqual(amounts["nj_income_tax"],      "231.82")
        self.assertEqual(amounts["nj_sdi"],             "9.50")
        self.assertEqual(amounts["nj_fli"],             "11.50")
        self.assertEqual(amounts["nj_ui"],              "21.25")

        # Totals
        self.assertEqual(data["total_taxes"], "1423.26")
        self.assertEqual(data["net_pay"],     "3576.74")

    # --- Scenario 2 ---
    # Mid-year ytd_gross=$180,000 exercises SS cap and exhausts all NJ bases.
    # SS eligible = max(0, 184,500 - 180,000) = 4,500 → 4,500×0.062 = 279.00
    # SDI/FLI eligible = max(0, 171,100 - 180,000) = 0 → 0.00 each
    # UI eligible = max(0, 44,800 - 180,000) = 0 → 0.00
    def test_ss_wage_base_cap_mid_year(self):
        resp = self._post({
            "gross_pay": "10000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "180000.00",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        amounts = {t["code"]: t["amount"] for t in data["taxes"]}

        self.assertEqual(amounts["social_security"], "279.00")
        self.assertEqual(amounts["medicare"],        "145.00")
        self.assertEqual(amounts["nj_sdi"],          "0.00")
        self.assertEqual(amounts["nj_fli"],          "0.00")
        self.assertEqual(amounts["nj_ui"],           "0.00")

    # --- Scenario 3 ---
    # Missing required field ytd_gross → 400.
    def test_missing_ytd_gross_returns_400(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
            # ytd_gross intentionally omitted
        })
        self.assertEqual(resp.status_code, 400)

    # --- Scenario 4 ---
    # Unsupported state → 400.
    def test_unsupported_state_returns_400(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "CA",
            "ytd_gross": "0.00",
        })
        self.assertEqual(resp.status_code, 400)

    # --- Scenario 5 ---
    # pay_date="2026-05-15" (no explicit tax_year) → tax_year=2026 in response.
    def test_pay_date_determines_tax_year(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
            "pay_date": "2026-05-15",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["tax_year"], 2026)
