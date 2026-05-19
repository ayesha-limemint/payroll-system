"""
Day 11 — API input validation and error responses.

Each test maps to an approved scenario in the technical plan
(daily_briefs/2026-05-19/02_technical_plan.md).

Endpoint: POST /api/v1/calculate/
Tests the new gross_pay > 0 and ytd_gross >= 0 validations, confirms
the consistent {"detail": "..."} error schema across all 400 paths,
and verifies the UI form at /calculate/ enforces the same rules.
"""
import json

from django.test import TestCase


_VALID_PAYLOAD = {
    "gross_pay": "5000.00",
    "pay_frequency": "biweekly",
    "filing_status": "single",
    "state": "NJ",
    "ytd_gross": "0.00",
}


class APIValidationTest(TestCase):

    def _post(self, payload):
        return self.client.post(
            "/api/v1/calculate/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    # --- Scenario 1 ---
    # gross_pay = 0.00 → 400.
    # Zero pay is not a valid payroll period; returning all-zero taxes
    # without error would mislead callers. Boundary check: zero is not positive.
    def test_gross_pay_zero_returns_400(self):
        payload = {**_VALID_PAYLOAD, "gross_pay": "0.00"}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("detail", data)
        self.assertIn("gross_pay", data["detail"])
        self.assertIn("positive", data["detail"].lower())

    # --- Scenario 2 ---
    # gross_pay = -100.00 → 400.
    # Negative gross would produce negative taxes, corrupting net_pay.
    def test_gross_pay_negative_returns_400(self):
        payload = {**_VALID_PAYLOAD, "gross_pay": "-100.00"}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("detail", data)
        self.assertIn("gross_pay", data["detail"])
        self.assertIn("positive", data["detail"].lower())

    # --- Scenario 3 ---
    # ytd_gross = -0.01 → 400.
    # Negative YTD inflates wage-base eligible amounts, corrupting FICA
    # and NJ SDI/FLI/UI caps. YTD cannot be negative by definition.
    def test_ytd_gross_negative_returns_400(self):
        payload = {**_VALID_PAYLOAD, "ytd_gross": "-0.01"}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("detail", data)
        self.assertIn("ytd_gross", data["detail"])
        self.assertIn("non-negative", data["detail"].lower())

    # --- Scenario 4 ---
    # Invalid filing_status → 400 with accepted values named in detail.
    # Confirms the detail message is actionable — caller knows what values are valid.
    def test_invalid_filing_status_detail_lists_accepted_values(self):
        payload = {**_VALID_PAYLOAD, "filing_status": "unknown_status"}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("detail", data)
        self.assertIn("filing_status", data["detail"])
        self.assertIn("single", data["detail"])

    # --- Scenario 5 ---
    # All 400 error paths return {"detail": "<non-empty string>"}.
    # Formalizes the error schema: consumers can always read response["detail"].
    def test_all_400_errors_have_detail_key(self):
        error_payloads = [
            # gross_pay = 0
            {**_VALID_PAYLOAD, "gross_pay": "0.00"},
            # ytd_gross negative
            {**_VALID_PAYLOAD, "ytd_gross": "-1.00"},
            # unsupported state
            {**_VALID_PAYLOAD, "state": "CA"},
            # invalid filing_status
            {**_VALID_PAYLOAD, "filing_status": "invalid"},
            # missing required field
            {k: v for k, v in _VALID_PAYLOAD.items() if k != "ytd_gross"},
        ]
        for payload in error_payloads:
            with self.subTest(payload=payload):
                resp = self._post(payload)
                self.assertEqual(resp.status_code, 400)
                data = resp.json()
                self.assertIn("detail", data, f"No 'detail' key for payload {payload}")
                self.assertIsInstance(data["detail"], str)
                self.assertGreater(len(data["detail"]), 0)


class UIValidationTest(TestCase):

    # --- Scenario 6 ---
    # UI form at /calculate/ with gross_pay=0 → error displayed, no results.
    # The HTML form has min="0" but server-side validation must catch zero explicitly.
    def test_ui_rejects_zero_gross_pay(self):
        resp = self.client.post("/calculate/", {
            "gross_pay": "0",
            "pay_frequency": "biweekly",
            "filing_status": "single",
            "ytd_gross": "0",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context.get("error"))
        self.assertIsNone(resp.context.get("result"))
