from decimal import Decimal

from django.test import TestCase

from payroll.calculators.nj.nj_contributions import calculate_nj_contributions


class NJContributionsTest(TestCase):
    def test_all_below_caps(self):
        """Scenario 1: gross=$1,000, ytd=$0 — all three bases untouched."""
        result = calculate_nj_contributions(1000, ytd_gross=0)
        self.assertEqual(result["nj_sdi"], Decimal("1.90"))
        self.assertEqual(result["nj_fli"], Decimal("2.30"))
        self.assertEqual(result["nj_ui"], Decimal("4.25"))

    def test_crosses_ui_base(self):
        """Scenario 2: gross=$6,000, ytd=$40,000 — UI base partially consumed ($4,800 left)."""
        result = calculate_nj_contributions(6000, ytd_gross=40000)
        self.assertEqual(result["nj_sdi"], Decimal("11.40"))
        self.assertEqual(result["nj_fli"], Decimal("13.80"))
        self.assertEqual(result["nj_ui"], Decimal("20.40"))

    def test_ui_exhausted_sdi_fli_active(self):
        """Scenario 3: gross=$5,000, ytd=$44,800 — UI exactly exhausted, SDI/FLI still active."""
        result = calculate_nj_contributions(5000, ytd_gross=44800)
        self.assertEqual(result["nj_sdi"], Decimal("9.50"))
        self.assertEqual(result["nj_fli"], Decimal("11.50"))
        self.assertEqual(result["nj_ui"], Decimal("0.00"))

    def test_all_caps_exhausted(self):
        """Scenario 4: gross=$5,000, ytd=$171,100 — all three caps fully exhausted."""
        result = calculate_nj_contributions(5000, ytd_gross=171100)
        self.assertEqual(result["nj_sdi"], Decimal("0.00"))
        self.assertEqual(result["nj_fli"], Decimal("0.00"))
        self.assertEqual(result["nj_ui"], Decimal("0.00"))

    def test_crosses_sdi_fli_base(self):
        """Scenario 5: gross=$2,000, ytd=$170,000 — SDI/FLI nearly exhausted ($1,100 left), UI gone."""
        result = calculate_nj_contributions(2000, ytd_gross=170000)
        self.assertEqual(result["nj_sdi"], Decimal("2.09"))
        self.assertEqual(result["nj_fli"], Decimal("2.53"))
        self.assertEqual(result["nj_ui"], Decimal("0.00"))

    def test_zero_gross(self):
        """Scenario 6: gross=$0, ytd=$0 — all contributions zero."""
        result = calculate_nj_contributions(0, ytd_gross=0)
        self.assertEqual(result["nj_sdi"], Decimal("0.00"))
        self.assertEqual(result["nj_fli"], Decimal("0.00"))
        self.assertEqual(result["nj_ui"], Decimal("0.00"))
