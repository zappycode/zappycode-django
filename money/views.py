from datetime import datetime
from operator import itemgetter

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from paypalrestsdk.exceptions import MethodNotAllowed
from paypalrestsdk import BillingAgreement, ResourceNotFound

from .models import Month
from sitewide.models import ZappyUser

import environ
import requests
import time

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

class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class Paypal(SuperuserRequiredMixin, View):
    template_name = "paypal_mrr.html"

    def __init__(self):
        super().__init__()
        user_list = self.get_active_paypal_users()
        self.current_date = datetime.now()
        if user_list:
            self.paypal_user_list = sorted(user_list, key=itemgetter('username'))
            self.price_chart = self.get_subs_chart()
        else:
            self.price_chart = None
            self.paypal_user_list = None

    def get(self, request, *args, **kwargs):
        return render(request, "money/paypal_mrr.html", {
            "active_users": self.paypal_user_list,
            "chart": self.price_chart,
            "current_date": self.current_date
        })

    def post(self, request, *args, **kwargs):
        return render(request, "money/paypal_mrr.html", {
            "active_users": self.paypal_user_list,
            "chart": self.price_chart,
            "current_date": self.current_date
        })

    @staticmethod
    def get_active_paypal_users():
        """returns all active paypal users"""
        paypal_users = ZappyUser.objects.filter(paypal_subscription_id__isnull=False)
        paypal_active_users = []
        
        env = environ.Env()
        environ.Env.read_env()
        
        token = env.str('PAYPAL_TOKEN', default='')
        
        headers = {
           'Content-Type': 'application/json',
           'Authorization': f'Bearer {token}',
           }

        for user in paypal_users:
            # in case there is empty string instead PayPal sub id
            if user.paypal_subscription_id:
                try:
                    response = requests.get(f'https://api-m.paypal.com/v1/billing/subscriptions/{user.paypal_subscription_id}', headers=headers)
                except ResourceNotFound:
                    print("Billing Agreement Not Found")
                    continue
                except MethodNotAllowed:
                    print("Billing Agreement Not Found")
                    continue

                if response.json()['status'].lower() == 'active':
                    plan_id = response.json()['plan_id']
                    billing_response = requests.get(f'https://api-m.paypal.com/v1/billing/plans/{plan_id}', headers=headers)
                    if billing_response.json()['billing_cycles'][0]['frequency']['interval_unit'] == 'MONTH':
                        sub_type = 'monthly'
                    else:
                        sub_type = 'yearly'

                    paypal_user = {
                        'username': user.username,
                        'email': user.email,
                        'sub_price': float(response.json()['billing_info']['last_payment']['amount']['value']),
                        'sub_type': sub_type,
                    }
                    paypal_active_users.append(paypal_user)

        return paypal_active_users

    def get_subs_chart(self):
        """prepares data for price table. Counts as well average subscriptions prices and MMR"""
        chart = {
            'monthly': {},
            'yearly': {}
        }
        yearly, monthly = 0, 0
        # collect set of subscription prices and amount for each price
        for pal in self.paypal_user_list:
            chart[pal['sub_type']][pal['sub_price']] = chart[pal['sub_type']].get(pal['sub_price'], 0) + 1

        yearly_sum = sum([k * v for k, v in chart['yearly'].items()])
        monthly_sum = sum([k * v for k, v in chart['monthly'].items()])

        # count average prices of subscriptions. if statements to avoid division by 0
        if chart['yearly']:
            yearly = yearly_sum/sum([v for v in chart['yearly'].values()])
        if chart['monthly']:
            monthly = monthly_sum/sum([v for v in chart['monthly'].values()])

        combined = yearly/12 + monthly

        chart['avg'] = {
            'yearly': yearly,
            'monthly': monthly,
            'combined': combined,
        }

        # count MRR
        chart['monthly_revenue'] = yearly_sum/12 + monthly_sum

        return chart
