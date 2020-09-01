from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from .models import Month


def home(request):
    months = Month.objects.order_by('-year', '-month')
    totals = Month.objects.aggregate(revenue=Sum('revenue'), expenses=Sum('expenses'))
    #profit = totals['revenue'] - totals['expenses']
    profit = Month.objects.aggregate(Sum('revenue'), Sum('expenses'))
    if profit is None:
        return render(request, 'money/home.html',
                  {'months': months, 'revenue': totals['revenue'], 'expenses': totals['expenses'], 'profit': profit})
    else:
        return render(request, 'money/home.html',
                  {'months': months, 'revenue': 0, 'expenses': 0, 'profit': 0})


def view_month(request, month_pk, month_slug):
    month = get_object_or_404(Month, pk=month_pk)
    return render(request, 'money/view_month.html', {'month': month})
