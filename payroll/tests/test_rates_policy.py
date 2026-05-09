"""CI policy: declared federal active tax year tracks the calendar year."""
import datetime

from django.test import TestCase

from payroll.calculators.nj import rates


class RatesPolicyTest(TestCase):
    def test_federal_tax_year_matches_calendar_year(self):
        self.assertEqual(rates.FEDERAL_TAX_YEAR, datetime.date.today().year)
