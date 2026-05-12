"""
Day 7 — Django UI: Calculator home page at /.

Each test maps to an approved scenario in the functional plan
(daily_briefs/2026-05-11/01_functional_plan.md).

Route: GET /
Template: payroll/templates/payroll/calculator.html
View: payroll.views.calculator

Note: JavaScript-driven result rendering is not testable via Django's test
client. Visual verification is done in Phase 9b via screenshot.
"""
from django.test import TestCase


class CalculatorHomeTest(TestCase):

    # --- Scenario 1 ---
    # GET / returns 200 OK.
    def test_get_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    # --- Scenario 2 ---
    # Response contains form fields for all required inputs.
    def test_form_fields_present(self):
        response = self.client.get("/")
        self.assertContains(response, 'name="gross_pay"')
        self.assertContains(response, 'name="filing_status"')
        self.assertContains(response, 'name="pay_frequency"')
        self.assertContains(response, 'name="ytd_gross"')
        self.assertContains(response, 'name="pay_date"')

    # --- Scenario 3 ---
    # All four filing status values that the API accepts are present as options.
    def test_filing_status_options(self):
        response = self.client.get("/")
        self.assertContains(response, 'value="single"')
        self.assertContains(response, 'value="married_filing_jointly"')
        self.assertContains(response, 'value="married_filing_separately"')
        self.assertContains(response, 'value="head_of_household"')

    # --- Scenario 4 ---
    # All four pay frequency values that the API accepts are present as options.
    def test_pay_frequency_options(self):
        response = self.client.get("/")
        self.assertContains(response, 'value="weekly"')
        self.assertContains(response, 'value="biweekly"')
        self.assertContains(response, 'value="semi_monthly"')
        self.assertContains(response, 'value="monthly"')
