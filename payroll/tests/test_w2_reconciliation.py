"""
Day 12 — Annual W-2 reconciliation: multi-period wage base cap verification.

Scenarios 1–5 verify existing cap boundary behavior at the API level.
Scenario 6 is the RED test for the new UI cap-utilization display.

Note: Scenarios 1–5 test existing correct calculator logic and are expected to
pass on the [RED] commit (consistent with Day 10 precedent). Scenario 6 fails RED
because the "Wage Base Utilization" section does not yet exist in the template.
"""
import json

from django.test import TestCase


class WageBaseCapTest(TestCase):
    """Wage base cap behavior at exact straddle and exhaustion boundaries."""

    def _post(self, payload):
        return self.client.post(
            "/api/v1/calculate/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def _get_tax(self, data, code):
        return next(t["amount"] for t in data["taxes"] if t["code"] == code)

    def test_ss_cap_straddle(self):
        """SS cap straddle: ytd=$183,000, gross=$3,000 → only $1,500 eligible → SS=$93.00.
        NJ contributions all zero because ytd already exceeds their lower caps."""
        r = self._post({
            "gross_pay": "3000.00",
            "ytd_gross": "183000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
        })
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(self._get_tax(data, "social_security"), "93.00")
        self.assertEqual(self._get_tax(data, "medicare"), "43.50")
        self.assertEqual(self._get_tax(data, "additional_medicare"), "0.00")
        self.assertEqual(self._get_tax(data, "nj_sdi"), "0.00")
        self.assertEqual(self._get_tax(data, "nj_fli"), "0.00")
        self.assertEqual(self._get_tax(data, "nj_ui"), "0.00")

    def test_ss_cap_exhausted(self):
        """SS cap exhausted: ytd=$185,000 > $184,500 cap → SS=$0.00. Medicare continues."""
        r = self._post({
            "gross_pay": "5000.00",
            "ytd_gross": "185000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
        })
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(self._get_tax(data, "social_security"), "0.00")
        self.assertEqual(self._get_tax(data, "medicare"), "72.50")
        self.assertEqual(self._get_tax(data, "additional_medicare"), "0.00")

    def test_nj_ui_cap_straddle(self):
        """NJ UI cap straddle: ytd=$44,000, gross=$2,000 → $800 eligible → UI=$3.40.
        SS and SDI/FLI still in full — their caps are not yet reached."""
        r = self._post({
            "gross_pay": "2000.00",
            "ytd_gross": "44000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
        })
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(self._get_tax(data, "social_security"), "124.00")
        self.assertEqual(self._get_tax(data, "nj_sdi"), "3.80")
        self.assertEqual(self._get_tax(data, "nj_fli"), "4.60")
        self.assertEqual(self._get_tax(data, "nj_ui"), "3.40")

    def test_nj_sdi_fli_cap_straddle(self):
        """NJ SDI/FLI straddle: ytd=$170,000, gross=$3,000 → $1,100 eligible.
        SDI=$2.09, FLI=$2.53 (same cap, applied independently). UI already exhausted."""
        r = self._post({
            "gross_pay": "3000.00",
            "ytd_gross": "170000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
        })
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(self._get_tax(data, "social_security"), "186.00")
        self.assertEqual(self._get_tax(data, "nj_sdi"), "2.09")
        self.assertEqual(self._get_tax(data, "nj_fli"), "2.53")
        self.assertEqual(self._get_tax(data, "nj_ui"), "0.00")

    def test_additional_medicare_straddle(self):
        """AMT straddle: ytd=$198,000, gross=$5,000 → $3,000 above $200k threshold.
        AMT=$27.00. SS exhausted (ytd > $184,500). Medicare continues at 1.45%."""
        r = self._post({
            "gross_pay": "5000.00",
            "ytd_gross": "198000.00",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "state": "NJ",
        })
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(self._get_tax(data, "social_security"), "0.00")
        self.assertEqual(self._get_tax(data, "medicare"), "72.50")
        self.assertEqual(self._get_tax(data, "additional_medicare"), "27.00")

    def test_ui_shows_cap_utilization_section(self):
        """After a successful calculation the results page includes the wage base
        utilization table. This is the RED test — the section does not yet exist."""
        response = self.client.post(
            "/calculate/",
            data={
                "gross_pay": "2000.00",
                "ytd_gross": "44000.00",
                "filing_status": "single",
                "pay_frequency": "biweekly",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wage Base Utilization")
