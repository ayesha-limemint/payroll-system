"""
Payroll app tests.
Tests are added here incrementally, one daily session at a time.
Each test maps to an approved scenario in the functional plan.
"""
from django.test import TestCase


class HealthCheckTest(TestCase):
    """Day 1 — Health check endpoint tests."""

    def test_health_returns_200(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, 200)

    def test_health_returns_ok_status(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.json()["status"], "ok")

    def test_health_returns_service_name(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.json()["service"], "payroll-system")
