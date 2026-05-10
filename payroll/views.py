from django.shortcuts import render

from payroll.calculators.nj.nj_contributions import calculate_nj_contributions


def nj_contributions(request):
    result = None
    if request.method == "POST":
        gross_pay = request.POST.get("gross_pay", "0")
        ytd_gross = request.POST.get("ytd_gross", "0")
        result = calculate_nj_contributions(gross_pay, ytd_gross)
    return render(request, "payroll/nj_contributions.html", {"result": result})
