from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from .models import Month


def home(request):
    months = Month.objects.order_by('-year', '-month')
    totals = Month.objects.aggregate(revenue=Sum('revenue'), expenses=Sum('expenses'))
    data = Month.objects.to_json()
    profit = 0
    if totals['revenue'] is not None and totals['expenses'] is not None:
        profit = totals['revenue'] - totals['expenses']
    return render(request, 'money/home.html', {
        'months': months, 
        'revenue': totals['revenue'], 
        'expenses': totals['expenses'], 
        'profit': profit, 
        'is_profit': profit >= 0,
        'data': data})


def view_month(request, month_pk, month_slug):
    month = get_object_or_404(Month, pk=month_pk)
    return render(request, 'money/view_month.html', {'month': month})
