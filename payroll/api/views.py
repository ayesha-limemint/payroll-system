"""
API views for the payroll system.
Built incrementally — one endpoint per daily session.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health_check(request):
    """
    GET /api/v1/health
    Health check endpoint. Day 1 target.
    """
    return Response({"status": "ok", "service": "payroll-system"})
