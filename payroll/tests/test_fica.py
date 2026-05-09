"""
Day 3 — FICA calculator tests.

Each test maps to a scenario approved during the 2026-05-09 session.
Revised after Ash's review: added ytd_gross parameter, removed per-period
cap approximation. See session notes for rationale.

Social Security: 6.2% on gross wages up to (SOCIAL_SECURITY_WAGE_BASE - ytd_gross),
floored at zero. The wage base is an annual cumulative limit, not a per-period one.

Medicare: 1.45% on all gross wages, no cap.
Additional Medicare Tax (0.9% above $200k) is out of scope for this day.
"""
from decimal import Decimal

from django.test import TestCase

from payroll.calculators.federal.fica import calculate_fica


class FICATest(TestCase):

    # --- Scenario 1 ---
    # No prior earnings (ytd=0), weekly $1,000 — well below annual cap.
    # SS eligible = 184500 - 0 = 184500
    # SS  = min(1000, 184500) × 0.062 = 62.00
    # Med = 1000 × 0.0145 = 14.50
    def test_weekly_no_prior_earnings(self):
        result = calculate_fica(1000.00, ytd_gross=0)
        self.assertEqual(result["social_security"], Decimal("62.00"))
        self.assertEqual(result["medicare"], Decimal("14.50"))

    # --- Scenario 2 ---
    # Partial cap consumed; gross fits within remaining eligible wages.
    # Monthly $5,000, ytd=$160,000.
    # SS eligible = 184500 - 160000 = 24500
    # SS  = min(5000, 24500) × 0.062 = 5000 × 0.062 = 310.00
    # Med = 5000 × 0.0145 = 72.50
    def test_gross_within_remaining_cap(self):
        result = calculate_fica(5000.00, ytd_gross=160_000)
        self.assertEqual(result["social_security"], Decimal("310.00"))
        self.assertEqual(result["medicare"], Decimal("72.50"))

    # --- Scenario 3 ---
    # Partial cap consumed; gross exceeds remaining eligible wages (SS truncated).
    # Monthly $10,000, ytd=$180,000.
    # SS eligible = 184500 - 180000 = 4500
    # SS  = min(10000, 4500) × 0.062 = 4500 × 0.062 = 279.00
    # Med = 10000 × 0.0145 = 145.00  (Medicare continues on full gross)
    def test_gross_exceeds_remaining_cap(self):
        result = calculate_fica(10_000.00, ytd_gross=180_000)
        self.assertEqual(result["social_security"], Decimal("279.00"))
        self.assertEqual(result["medicare"], Decimal("145.00"))

    # --- Scenario 4 ---
    # Wage base already exhausted — SS = $0, Medicare continues.
    # Monthly $5,000, ytd=$185,000 (above $184,500 cap).
    # SS eligible = max(0, 184500 - 185000) = 0
    # SS  = 0.00
    # Med = 5000 × 0.0145 = 72.50
    def test_wage_base_exhausted(self):
        result = calculate_fica(5000.00, ytd_gross=185_000)
        self.assertEqual(result["social_security"], Decimal("0.00"))
        self.assertEqual(result["medicare"], Decimal("72.50"))

    # --- Scenario 5 ---
    # Zero gross pay — both contributions must be $0.00.
    def test_zero_gross(self):
        result = calculate_fica(0.00, ytd_gross=0)
        self.assertEqual(result["social_security"], Decimal("0.00"))
        self.assertEqual(result["medicare"], Decimal("0.00"))

    # --- Scenario 6 ---
    # Bi-weekly, no prior earnings — standard case for a new employee.
    # SS eligible = 184500; SS = 3000 × 0.062 = 186.00; Med = 3000 × 0.0145 = 43.50
    def test_biweekly_no_prior_earnings(self):
        result = calculate_fica(3000.00, ytd_gross=0)
        self.assertEqual(result["social_security"], Decimal("186.00"))
        self.assertEqual(result["medicare"], Decimal("43.50"))
