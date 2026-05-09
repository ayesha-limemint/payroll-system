"""
API views for the payroll system.
Built incrementally ? one endpoint per daily session.
"""
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from payroll.calculators.federal.calculator import (
    calculate_federal_income_tax,
    resolve_federal_tax_year,
)


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
        gross_pay = float(data["gross_pay"])
        filing_status = data["filing_status"]
        pay_frequency = data["pay_frequency"]
    except (KeyError, TypeError, ValueError):
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
            "federal_income_tax": amount,
            "tax_year_used": year,
        },
        status=status.HTTP_200_OK,
    )

