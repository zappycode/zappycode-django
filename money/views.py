from django.shortcuts import render, get_object_or_404
from .models import Month


def home(request):
    months = Month.objects.order_by('-year', '-month')
    return render(request, 'money/home.html',
                  {'months': months, 'revenue': '14.22', 'expenses': '4.22', 'profit': '6.22',
                   'is_profit': True})


def view_month(request, month_pk, month_slug):
    month = get_object_or_404(Month, pk=month_pk)
    return render(request, 'money/view_month.html', {'month': month})
