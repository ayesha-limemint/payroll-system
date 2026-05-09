"""API tests for federal income tax calculation endpoint."""
import json

from django.test import TestCase

from payroll.calculators.federal.calculator import calculate_federal_income_tax
from payroll.calculators.nj import rates



class FederalIncomeTaxAPITest(TestCase):
    def test_defaults_to_active_tax_year(self):
        response = self.client.post(
            "/api/v1/calculate/federal-income-tax/",
            data=json.dumps(
                {
                    "gross_pay": 1000.0,
                    "filing_status": "SINGLE",
                    "pay_frequency": "WEEKLY",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        expected = calculate_federal_income_tax(1000.0, "SINGLE", "WEEKLY")
        self.assertEqual(body["tax_year_used"], rates.FEDERAL_TAX_YEAR)
        self.assertEqual(body["federal_income_tax"], str(expected))

    def test_pay_date_selects_schedule_year(self):
        response = self.client.post(
            "/api/v1/calculate/federal-income-tax/",
            data=json.dumps(
                {
                    "gross_pay": 1000.0,
                    "filing_status": "SINGLE",
                    "pay_frequency": "WEEKLY",
                    "pay_date": "2025-06-01",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        expected = calculate_federal_income_tax(
            1000.0, "SINGLE", "WEEKLY", tax_year=2025
        )
        self.assertEqual(body["tax_year_used"], 2025)
        self.assertEqual(body["federal_income_tax"], str(expected))

    def test_tax_year_conflicts_with_pay_date_returns_400(self):
        ty = rates.FEDERAL_TAX_YEAR
        response = self.client.post(
            "/api/v1/calculate/federal-income-tax/",
            data=json.dumps(
                {
                    "gross_pay": 1000.0,
                    "filing_status": "SINGLE",
                    "pay_frequency": "WEEKLY",
                    "tax_year": ty,
                    "pay_date": f"{ty - 1}-06-01",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_unsupported_tax_year_returns_400(self):
        response = self.client.post(
            "/api/v1/calculate/federal-income-tax/",
            data=json.dumps(
                {
                    "gross_pay": 1000.0,
                    "filing_status": "SINGLE",
                    "pay_frequency": "WEEKLY",
                    "tax_year": 1999,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
