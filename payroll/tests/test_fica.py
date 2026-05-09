"""
Day 3 — FICA calculator tests.

Each test maps to an approved scenario in the functional plan
(daily_briefs/2026-05-09/01_functional_plan.md).

Social Security: 6.2% on gross wages up to $184,500 annual wage base (2026).
Per-period cap = SOCIAL_SECURITY_WAGE_BASE / pay_periods — no YTD tracking
(deliberate; see technical plan notes and backlog).

Medicare: 1.45% on all gross wages, no cap.
Additional Medicare Tax (0.9% above $200k) is out of scope for this day.
"""
from decimal import Decimal

from django.test import TestCase

from payroll.calculators.federal.fica import calculate_fica


class FICATest(TestCase):

    # --- Scenario 1 ---
    # Weekly $1,000 (annual $52,000 — well below SS wage base of $184,500).
    # SS  = 1000 × 0.062 = 62.00
    # Med = 1000 × 0.0145 = 14.50
    def test_weekly_below_cap(self):
        result = calculate_fica(1000.00, "WEEKLY")
        self.assertEqual(result["social_security"], Decimal("62.00"))
        self.assertEqual(result["medicare"], Decimal("14.50"))

    # --- Scenario 2 ---
    # Monthly $15,375 (annual $184,500 — exactly at SS wage base).
    # Per-period cap = 184500 / 12 = 15375.00 (exact).
    # SS  = 15375 × 0.062 = 953.25
    # Med = 15375 × 0.0145 = 222.9375 → ROUND_HALF_UP → 222.94
    def test_monthly_at_cap(self):
        result = calculate_fica(15375.00, "MONTHLY")
        self.assertEqual(result["social_security"], Decimal("953.25"))
        self.assertEqual(result["medicare"], Decimal("222.94"))

    # --- Scenario 3 ---
    # Monthly $20,000 (annual $240,000 — above SS wage base).
    # Per-period cap = 15375.00; SS capped at cap, Medicare on full gross.
    # SS  = 15375 × 0.062 = 953.25 (capped)
    # Med = 20000 × 0.0145 = 290.00 (no cap)
    def test_monthly_above_cap(self):
        result = calculate_fica(20000.00, "MONTHLY")
        self.assertEqual(result["social_security"], Decimal("953.25"))
        self.assertEqual(result["medicare"], Decimal("290.00"))

    # --- Scenario 4 ---
    # Bi-weekly $3,000 (annual $78,000 — below SS wage base).
    # Per-period cap = 184500 / 26 = 7096.15...  (gross is well below)
    # SS  = 3000 × 0.062 = 186.00
    # Med = 3000 × 0.0145 = 43.50
    def test_biweekly_below_cap(self):
        result = calculate_fica(3000.00, "BI_WEEKLY")
        self.assertEqual(result["social_security"], Decimal("186.00"))
        self.assertEqual(result["medicare"], Decimal("43.50"))

    # --- Scenario 5 ---
    # Zero gross pay — both contributions must be $0.00.
    def test_zero_gross(self):
        result = calculate_fica(0.00, "WEEKLY")
        self.assertEqual(result["social_security"], Decimal("0.00"))
        self.assertEqual(result["medicare"], Decimal("0.00"))
