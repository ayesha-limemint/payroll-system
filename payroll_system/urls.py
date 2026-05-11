from django.contrib import admin
from django.urls import path, include

from payroll import views as payroll_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("payroll.api.urls")),
    path("nj-contributions/", payroll_views.nj_contributions, name="nj-contributions"),
    path("calculate/", payroll_views.nj_calculate, name="nj-calculate"),
]
