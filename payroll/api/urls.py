from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health_check, name="health-check"),
    path(
        "calculate/federal-income-tax/",
        views.federal_income_tax,
        name="federal-income-tax",
    ),
]
