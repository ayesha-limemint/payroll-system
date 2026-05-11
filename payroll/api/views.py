"""
API views for the payroll system.
Built incrementally — one endpoint per daily session.
"""
from decimal import Decimal, InvalidOperation

from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from payroll.calculators.federal.calculator import (
    calculate_federal_income_tax,
    resolve_federal_tax_year,
)
from payroll.calculators.federal.fica import calculate_fica
from payroll.calculators.nj.nj_contributions import calculate_nj_contributions
from payroll.calculators.nj.nj_income_tax import calculate_nj_income_tax

_FILING_STATUS_MAP = {
    "single": "SINGLE",
    "married_filing_jointly": "MARRIED_FILING_JOINTLY",
    "married_filing_separately": "MARRIED_FILING_SEPARATELY",
    "head_of_household": "HEAD_OF_HOUSEHOLD",
}

_PAY_FREQUENCY_MAP = {
    "weekly": "WEEKLY",
    "biweekly": "BI_WEEKLY",
    "semi_monthly": "SEMI_MONTHLY",
    "monthly": "MONTHLY",
}

_SUPPORTED_STATES = {"NJ"}


@api_view(["GET"])
def health_check(request):
    """
    GET /api/v1/health
    Health check endpoint. Day 1 target.
    """
    return Response({"status": "ok", "service": "payroll-system"})


@api_view(["POST"])
def federal_income_tax(request):
    """
    POST /api/v1/calculate/federal-income-tax

    Request JSON:
      gross_pay (number, required)
      filing_status (string, required) -- SINGLE | MARRIED_FILING_JOINTLY
      pay_frequency (string, required) -- WEEKLY | BI_WEEKLY | SEMI_MONTHLY | MONTHLY
      tax_year (integer, optional) -- federal withholding table year
      pay_date (YYYY-MM-DD, optional) -- when tax_year omitted, calendar year is used

    When both tax_year and pay_date are sent, they must agree on calendar year.
    """
    data = request.data
    try:
        gross_pay = Decimal(str(data["gross_pay"]))
        filing_status = data["filing_status"]
        pay_frequency = data["pay_frequency"]
    except (KeyError, TypeError, InvalidOperation):
        return Response(
            {"detail": "gross_pay, filing_status, and pay_frequency are required and valid."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    raw_ty = data.get("tax_year")
    try:
        tax_year_arg = int(raw_ty) if raw_ty is not None else None
    except (TypeError, ValueError):
        return Response({"detail": "tax_year must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

    pay_raw = data.get("pay_date")
    pay_date = None
    if pay_raw:
        pay_date = parse_date(str(pay_raw))
        if pay_date is None:
            return Response({"detail": "pay_date must be YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        year = resolve_federal_tax_year(tax_year=tax_year_arg, pay_date=pay_date)
        amount = calculate_federal_income_tax(
            gross_pay, filing_status, pay_frequency, tax_year=year
        )
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "federal_income_tax": str(amount),
            "tax_year_used": year,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def calculate(request):
    """
    POST /api/v1/calculate/

    Full NJ gross-to-net breakdown. Returns all seven tax line items:
    federal income tax, Social Security, Medicare, NJ income tax,
    NJ SDI, NJ FLI, NJ UI.

    Request fields:
      gross_pay      (required) — gross pay for this period
      pay_frequency  (required) — weekly | biweekly | semi_monthly | monthly
      filing_status  (required) — single | married_filing_jointly
      state          (required) — NJ (only NJ supported)
      ytd_gross      (required) — total gross wages paid YTD before this period
      pay_date       (optional) — YYYY-MM-DD; determines tax_year
      tax_year       (optional) — integer override
    """
    data = request.data

    try:
        gross = Decimal(str(data["gross_pay"]))
        ytd = Decimal(str(data["ytd_gross"]))
        filing_status_raw = str(data["filing_status"])
        pay_frequency_raw = str(data["pay_frequency"])
        state = str(data["state"])
    except (KeyError, TypeError, InvalidOperation):
        return Response(
            {"detail": "gross_pay, ytd_gross, filing_status, pay_frequency, and state are required and must be valid."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if state not in _SUPPORTED_STATES:
        return Response(
            {"detail": f"Unsupported state: {state!r}. Supported states: NJ"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    calc_filing = _FILING_STATUS_MAP.get(filing_status_raw)
    if calc_filing is None:
        return Response(
            {"detail": f"Invalid filing_status: {filing_status_raw!r}. Accepted: {list(_FILING_STATUS_MAP)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    calc_freq = _PAY_FREQUENCY_MAP.get(pay_frequency_raw)
    if calc_freq is None:
        return Response(
            {"detail": f"Invalid pay_frequency: {pay_frequency_raw!r}. Accepted: {list(_PAY_FREQUENCY_MAP)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    raw_ty = data.get("tax_year")
    try:
        tax_year_arg = int(raw_ty) if raw_ty is not None else None
    except (TypeError, ValueError):
        return Response({"detail": "tax_year must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

    pay_raw = data.get("pay_date")
    pay_date = None
    if pay_raw:
        pay_date = parse_date(str(pay_raw))
        if pay_date is None:
            return Response({"detail": "pay_date must be YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        year = resolve_federal_tax_year(tax_year=tax_year_arg, pay_date=pay_date)
        fed = calculate_federal_income_tax(gross, calc_filing, calc_freq, tax_year=year)
        fica = calculate_fica(gross, ytd_gross=ytd)
        nj_it = calculate_nj_income_tax(gross, calc_filing, calc_freq)
        nj_contrib = calculate_nj_contributions(gross, ytd_gross=ytd)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    taxes = [
        {"code": "federal_income_tax", "name": "Federal Income Tax",  "amount": str(fed)},
        {"code": "social_security",    "name": "Social Security",     "amount": str(fica["social_security"])},
        {"code": "medicare",           "name": "Medicare",            "amount": str(fica["medicare"])},
        {"code": "nj_income_tax",      "name": "NJ State Income Tax", "amount": str(nj_it)},
        {"code": "nj_sdi",             "name": "NJ SDI",              "amount": str(nj_contrib["nj_sdi"])},
        {"code": "nj_fli",             "name": "NJ FLI",              "amount": str(nj_contrib["nj_fli"])},
        {"code": "nj_ui",              "name": "NJ UI",               "amount": str(nj_contrib["nj_ui"])},
    ]
    total_taxes = sum(Decimal(t["amount"]) for t in taxes)
    net_pay = gross - total_taxes

    return Response(
        {
            "gross_pay":     str(gross.quantize(Decimal("0.01"))),
            "net_pay":       str(net_pay.quantize(Decimal("0.01"))),
            "pay_frequency": pay_frequency_raw,
            "filing_status": filing_status_raw,
            "state":         state,
            "tax_year":      year,
            "taxes":         taxes,
            "total_taxes":   str(total_taxes.quantize(Decimal("0.01"))),
            "deductions":    [],
        },
        status=status.HTTP_200_OK,
    )

