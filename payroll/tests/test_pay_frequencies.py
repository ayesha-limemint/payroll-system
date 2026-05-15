"""
Day 10 — Multiple pay frequencies: all-frequency regression pass.

Tests the POST /api/v1/calculate/ endpoint for all four pay frequencies:
weekly, semi_monthly, and monthly (biweekly is already covered in
test_calculate_api.py). Also verifies that an invalid pay_frequency
returns HTTP 400.

Each test maps to an approved scenario in the functional plan
(daily_briefs/2026-05-14/01_functional_plan.md).

Note: this is a regression / verification session. The _PAY_FREQUENCY_MAP
and PAY_PERIODS lookups in the view and calculators already exist. These
tests confirm the full API stack (normalization → calculator dispatch →
response formatting) is correct for every supported frequency value.

All expected values hand-computed and Python-verified on 2026-05-14.
"""
import json

from django.test import TestCase


class PayFrequencyTest(TestCase):

    def _post(self, payload):
        return self.client.post(
            "/api/v1/calculate/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    # --- Scenario 1 ---
    # weekly, single, $2,000/week, ytd=$0
    # Annual gross = $104,000. Federal taxable = $87,900 (−$16,100 std deduction).
    # 10%×$12,400 + 12%×$38,000 + 22%×$37,500 = $14,050.00 / 52 = $270.19.
    # NJ taxable = $102,000 (−$1,000 std − $1,000 personal).
    # NJ: 1.4%×20k+1.75%×15k+3.5%×5k+5.525%×35k+6.37%×27k = $4,371.15 / 52 = $84.06.
    # FICA and NJ contributions on gross $2,000: SS=124.00, Med=29.00, SDI=3.80,
    # FLI=4.60, UI=8.50.
    def test_weekly_single_filer(self):
        resp = self._post({
            "gross_pay": "2000.00",
            "pay_frequency": "weekly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["gross_pay"],     "2000.00")
        self.assertEqual(data["pay_frequency"], "weekly")
        self.assertEqual(data["tax_year"],      2026)

        amounts = {t["code"]: t["amount"] for t in data["taxes"]}
        self.assertEqual(amounts["federal_income_tax"],  "270.19")
        self.assertEqual(amounts["social_security"],     "124.00")
        self.assertEqual(amounts["medicare"],            "29.00")
        self.assertEqual(amounts["additional_medicare"], "0.00")
        self.assertEqual(amounts["nj_income_tax"],       "84.06")
        self.assertEqual(amounts["nj_sdi"],              "3.80")
        self.assertEqual(amounts["nj_fli"],              "4.60")
        self.assertEqual(amounts["nj_ui"],               "8.50")

        self.assertEqual(data["total_taxes"], "524.15")
        self.assertEqual(data["net_pay"],     "1475.85")

    # --- Scenario 2 ---
    # semi_monthly, single, $2,500/semi-monthly, ytd=$0
    # Annual gross = $60,000. Federal taxable = $43,900 (−$16,100).
    # 10%×$12,400 + 12%×$31,500 = $5,020.00 / 24 = $209.17.
    # NJ taxable = $58,000. NJ: $1,712.00 / 24 = $71.33.
    # NJ UI: $2,500×0.425% = $10.625 → $10.63 (ROUND_HALF_UP).
    # Confirms 24-period divisor is used (not 26 as in biweekly).
    def test_semi_monthly_single_filer(self):
        resp = self._post({
            "gross_pay": "2500.00",
            "pay_frequency": "semi_monthly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["gross_pay"],     "2500.00")
        self.assertEqual(data["pay_frequency"], "semi_monthly")
        self.assertEqual(data["tax_year"],      2026)

        amounts = {t["code"]: t["amount"] for t in data["taxes"]}
        self.assertEqual(amounts["federal_income_tax"],  "209.17")
        self.assertEqual(amounts["social_security"],     "155.00")
        self.assertEqual(amounts["medicare"],            "36.25")
        self.assertEqual(amounts["additional_medicare"], "0.00")
        self.assertEqual(amounts["nj_income_tax"],       "71.33")
        self.assertEqual(amounts["nj_sdi"],              "4.75")
        self.assertEqual(amounts["nj_fli"],              "5.75")
        self.assertEqual(amounts["nj_ui"],               "10.63")

        self.assertEqual(data["total_taxes"], "492.88")
        self.assertEqual(data["net_pay"],     "2007.12")

    # --- Scenario 3 ---
    # monthly, single, $5,000/month, ytd=$0
    # Annual gross = $60,000 (same annual as Sc2 — demonstrates ÷12 vs ÷24).
    # Federal: $5,020.00 / 12 = $418.33.  NJ: $1,712.00 / 12 = $142.67.
    # FICA/NJ contributions on gross $5,000.
    def test_monthly_single_filer(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "monthly",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["gross_pay"],     "5000.00")
        self.assertEqual(data["pay_frequency"], "monthly")
        self.assertEqual(data["tax_year"],      2026)

        amounts = {t["code"]: t["amount"] for t in data["taxes"]}
        self.assertEqual(amounts["federal_income_tax"],  "418.33")
        self.assertEqual(amounts["social_security"],     "310.00")
        self.assertEqual(amounts["medicare"],            "72.50")
        self.assertEqual(amounts["additional_medicare"], "0.00")
        self.assertEqual(amounts["nj_income_tax"],       "142.67")
        self.assertEqual(amounts["nj_sdi"],              "9.50")
        self.assertEqual(amounts["nj_fli"],              "11.50")
        self.assertEqual(amounts["nj_ui"],               "21.25")

        self.assertEqual(data["total_taxes"], "985.75")
        self.assertEqual(data["net_pay"],     "4014.25")

    # --- Scenario 4 ---
    # Invalid pay_frequency → 400.
    # "daily" is not in _PAY_FREQUENCY_MAP — the view should return a 400
    # with a detail message naming the accepted values.
    def test_invalid_pay_frequency_returns_400(self):
        resp = self._post({
            "gross_pay": "5000.00",
            "pay_frequency": "daily",
            "filing_status": "single",
            "state": "NJ",
            "ytd_gross": "0.00",
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn("detail", resp.json())

    # --- Scenario 5 ---
    # weekly, MFJ, $3,000/week, ytd=$0
    # Annual gross = $156,000. Federal MFJ taxable = $123,800 (−$32,200 std deduction).
    # 10%×$24,800 + 12%×$76,000 + 22%×$23,000 = $16,660.00 / 52 = $320.38.
    # NJ MFJ taxable = $152,000 (−$4,000). NJ MFJ brackets → $5,639.90 / 52 = $108.46.
    # Verifies MFJ brackets are applied correctly at a non-biweekly frequency.
    def test_weekly_mfj_filer(self):
        resp = self._post({
            "gross_pay": "3000.00",
            "pay_frequency": "weekly",
            "filing_status": "married_filing_jointly",
            "state": "NJ",
            "ytd_gross": "0.00",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["gross_pay"],     "3000.00")
        self.assertEqual(data["pay_frequency"], "weekly")
        self.assertEqual(data["filing_status"], "married_filing_jointly")
        self.assertEqual(data["tax_year"],      2026)

        amounts = {t["code"]: t["amount"] for t in data["taxes"]}
        self.assertEqual(amounts["federal_income_tax"],  "320.38")
        self.assertEqual(amounts["social_security"],     "186.00")
        self.assertEqual(amounts["medicare"],            "43.50")
        self.assertEqual(amounts["additional_medicare"], "0.00")
        self.assertEqual(amounts["nj_income_tax"],       "108.46")
        self.assertEqual(amounts["nj_sdi"],              "5.70")
        self.assertEqual(amounts["nj_fli"],              "6.90")
        self.assertEqual(amounts["nj_ui"],               "12.75")

        self.assertEqual(data["total_taxes"], "683.69")
        self.assertEqual(data["net_pay"],     "2316.31")
