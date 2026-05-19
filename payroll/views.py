from decimal import Decimal, InvalidOperation

from django.shortcuts import render
from django.utils.dateparse import parse_date

from payroll.calculators.federal.calculator import (
    calculate_federal_income_tax,
    resolve_federal_tax_year,
)
from payroll.calculators.federal.fica import calculate_fica
from payroll.calculators.nj.nj_contributions import calculate_nj_contributions
from payroll.calculators.nj.nj_income_tax import calculate_nj_income_tax
from payroll.calculators.nj.rates import (
    NJ_SDI_WAGE_BASE,
    NJ_UI_WAGE_BASE,
    SOCIAL_SECURITY_WAGE_BASE,
)

_FILING_STATUS_MAP = {
    "single": "SINGLE",
    "married_filing_jointly": "MARRIED_FILING_JOINTLY",
}

_PAY_FREQUENCY_MAP = {
    "weekly": "WEEKLY",
    "biweekly": "BI_WEEKLY",
    "semi_monthly": "SEMI_MONTHLY",
    "monthly": "MONTHLY",
}

FILING_STATUS_CHOICES = [
    ("single", "Single"),
    ("married_filing_jointly", "Married Filing Jointly"),
]

PAY_FREQUENCY_CHOICES = [
    ("weekly", "Weekly"),
    ("biweekly", "Biweekly"),
    ("semi_monthly", "Semi-Monthly"),
    ("monthly", "Monthly"),
]


def calculator(request):
    return render(request, "payroll/calculator.html", {})


def nj_contributions(request):
    result = None
    if request.method == "POST":
        gross_pay = request.POST.get("gross_pay", "0")
        ytd_gross = request.POST.get("ytd_gross", "0")
        result = calculate_nj_contributions(gross_pay, ytd_gross)
    return render(request, "payroll/nj_contributions.html", {"result": result})


def nj_calculate(request):
    result = None
    error = None
    cap_utilization = None
    if request.method == "POST":
        try:
            gross = Decimal(request.POST.get("gross_pay", "0"))
            ytd = Decimal(request.POST.get("ytd_gross", "0"))
            filing = request.POST.get("filing_status", "single")
            freq = request.POST.get("pay_frequency", "biweekly")
            pay_date_str = request.POST.get("pay_date", "").strip()

            calc_filing = _FILING_STATUS_MAP.get(filing)
            calc_freq = _PAY_FREQUENCY_MAP.get(freq)
            if not calc_filing or not calc_freq:
                raise ValueError("Invalid filing status or pay frequency.")

            pay_date = parse_date(pay_date_str) if pay_date_str else None
            year = resolve_federal_tax_year(pay_date=pay_date)

            fed = calculate_federal_income_tax(gross, calc_filing, calc_freq, tax_year=year)
            fica = calculate_fica(gross, ytd_gross=ytd)
            nj_it = calculate_nj_income_tax(gross, calc_filing, calc_freq)
            nj_contrib = calculate_nj_contributions(gross, ytd_gross=ytd)

            taxes = [
                {"name": "Federal Income Tax",  "amount": fed},
                {"name": "Social Security",     "amount": fica["social_security"]},
                {"name": "Medicare",            "amount": fica["medicare"]},
                {"name": "NJ State Income Tax", "amount": nj_it},
                {"name": "NJ SDI",              "amount": nj_contrib["nj_sdi"]},
                {"name": "NJ FLI",              "amount": nj_contrib["nj_fli"]},
                {"name": "NJ UI",               "amount": nj_contrib["nj_ui"]},
            ]
            total_taxes = sum(t["amount"] for t in taxes)
            result = {
                "gross_pay":   gross,
                "taxes":       taxes,
                "total_taxes": total_taxes,
                "net_pay":     gross - total_taxes,
                "tax_year":    year,
            }
            ytd_after = ytd + gross
            ss_wb = Decimal(str(SOCIAL_SECURITY_WAGE_BASE))
            sdi_fli_wb = Decimal(str(NJ_SDI_WAGE_BASE))
            ui_wb = Decimal(str(NJ_UI_WAGE_BASE))
            cap_utilization = {
                "ss_wage_base":         SOCIAL_SECURITY_WAGE_BASE,
                "ss_used":              min(ytd_after, ss_wb),
                "ss_remaining":         max(Decimal("0"), ss_wb - ytd_after),
                "nj_sdi_fli_wage_base": NJ_SDI_WAGE_BASE,
                "nj_sdi_fli_used":      min(ytd_after, sdi_fli_wb),
                "nj_sdi_fli_remaining": max(Decimal("0"), sdi_fli_wb - ytd_after),
                "nj_ui_wage_base":      NJ_UI_WAGE_BASE,
                "nj_ui_used":           min(ytd_after, ui_wb),
                "nj_ui_remaining":      max(Decimal("0"), ui_wb - ytd_after),
            }
        except (InvalidOperation, ValueError) as exc:
            error = str(exc)

    return render(request, "payroll/calculate.html", {
        "result": result,
        "error": error,
        "cap_utilization": cap_utilization,
        "filing_status_choices": FILING_STATUS_CHOICES,
        "pay_frequency_choices": PAY_FREQUENCY_CHOICES,
    })
