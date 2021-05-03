import json
from calendar import month_name
from datetime import datetime
from operator import itemgetter

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from paypalrestsdk.exceptions import MethodNotAllowed

from .models import Month, PaypalUsers, PaypalRevenue
from paypalrestsdk import BillingAgreement, BillingPlan, ResourceNotFound
import environ
from sitewide.models import ZappyUser


env = environ.Env()
environ.Env.read_env()


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


# access to paypal mrr is restricted. only staff can see page.
# but if u want bigger restrictions, u can uncomment decorator
# permission_required. but remember to set it for users u want to grant
@method_decorator(staff_member_required, name='dispatch')
#@method_decorator(permission_required('money.view_paypalusers', raise_exception=True), name='dispatch')
class Paypal(View):
    template_name = "paypal_mrr.html"

    def __init__(self):
        super().__init__()
        user_list = self.get_paypal_users()
        if user_list:
            self.paypal_user_list = sorted(user_list, key=itemgetter('username'))
            self.for_chart = self.get_monthly_revenue()
            self.price_chart = self.get_subs_chart()
        else:
            self.price_chart = None
            self.for_chart = None
            self.paypal_user_list = None

    def get(self, request, *args, **kwargs):
        active_users = None
        cancelled_users = None
        if self.paypal_user_list:
            active_users = [user for user in self.paypal_user_list if user['state'] == 'active']
            cancelled_users = [user for user in self.paypal_user_list if user['state'] == 'cancelled']

        return render(request, "money/paypal_mrr.html", {
            "active_users": active_users,
            "cancelled_users": cancelled_users,
            "chart": self.price_chart,
            "data": self.for_chart,
        })

    def post(self, request, *args, **kwargs):
        self.paypal_user_list = sorted(self.get_paypal_users(True), key=itemgetter('username'))
        active_users = [user for user in self.paypal_user_list if user['state'] == 'active']
        cancelled_users = [user for user in self.paypal_user_list if user['state'] == 'cancelled']
        self.for_chart = self.get_monthly_revenue()
        self.price_chart = self.get_subs_chart()

        return render(request, "money/paypal_mrr.html", {
            "active_users": active_users,
            "cancelled_users": cancelled_users,
            "chart": self.price_chart,
            "data": self.for_chart,
        })

    @staticmethod
    def get_paypal_users(from_api=False):
        """returning all active users and cancelled with valid subs"""
        paypal_users = ZappyUser.objects.filter(paypal_subscription_id__isnull=False)
        paypal_users_lists = []
        billing_agreement = None

        for user in paypal_users:
            # in case there is empty string instead PayPal sub id
            if user.paypal_subscription_id:
                if from_api:
                    date = datetime.now().date()
                    try:
                        billing_agreement = BillingAgreement.find(user.paypal_subscription_id).to_dict()
                        PaypalUsers.objects.update_or_create(
                            user=user,
                            defaults={'subs_details': json.dumps(billing_agreement), 'date': date},
                        )
                    except ResourceNotFound:
                        print("Billing Agreement Not Found")
                    except MethodNotAllowed:
                        print("Billing Agreement Not Found")
                else:
                    if user.paypalusers_set.values():
                        billing_agreement = json.loads(user.paypalusers_set.values().first()['subs_details'])
                        date = user.paypalusers_set.values().first()['date']
                    else:
                        break

                if billing_agreement['plan']['payment_definitions'][0]['frequency'] == 'MONTH':
                    sub_type = 'monthly'
                else:
                    sub_type = 'yearly'

                # we need below values for collecting revenues
                next_pay = datetime.strptime(
                    billing_agreement['agreement_details']['next_billing_date'], "%Y-%m-%dT%H:%M:%SZ"
                )
                last_pay = datetime.strptime(
                    billing_agreement['agreement_details']['last_payment_date'], "%Y-%m-%dT%H:%M:%SZ"
                )

                paypal_user = {
                    'username': user.username,
                    'email': user.email,
                    'sub_price': float(billing_agreement['plan']['payment_definitions'][0]['amount']['value']),
                    'sub_type': sub_type,
                    'state': billing_agreement['state'].lower(),
                    'date': date,
                    'next_pay': next_pay,
                    'last_pay': last_pay,
                }

                # we need a list with active users and those, who cancelled sub and it is still valid
                if paypal_user['state'] == 'active' or next_pay.date() >= date:
                    paypal_users_lists.append(paypal_user)

        return paypal_users_lists

    def get_subs_chart(self):
        """Prepares data for price table. Counts as well average subscriptions prices"""
        chart = {
            'monthly': {},
            'yearly': {}
        }
        yearly, monthly = 0, 0
        # collect set of subscription prices and amount for each price
        for pal in self.paypal_user_list:
            if pal['state'] == 'active':
                chart[pal['sub_type']][pal['sub_price']] = chart[pal['sub_type']].get(pal['sub_price'], 0) + 1

        # count average prices of subscriptions. if statements in case, there are no monthly or yearly subs
        if chart['yearly']:
            yearly = sum([k * v for k, v in chart['yearly'].items()])/sum([v for v in chart['yearly'].values()])
        if chart['monthly']:
            monthly = sum([k * v for k, v in chart['monthly'].items()])/sum([v for v in chart['monthly'].values()])

        combined = (yearly/12 + monthly)/2

        chart['avg'] = {
            'yearly': yearly,
            'monthly': monthly,
            'combined': combined,
        }
        return chart

    def get_monthly_revenue(self):
        """Prepares data for chart. Collects revenues and save to database"""
        self.get_paypal_users()
        month = self.paypal_user_list[0]['date'].month
        year = self.paypal_user_list[0]['date'].year

        # update last month's revenue only if completed flag = False
        previous_month = month -1

        # in case of january
        if previous_month == 0:
            previous_month = 12
            year = year - 1

        if not PaypalRevenue.objects.filter(month=month-1, completed=True):
            # sum all payments made in previous month
            last_month_revenue = sum([user['sub_price'] for user in self.paypal_user_list
                                      if user['last_pay'].month == previous_month])
            # save result to db
            PaypalRevenue.objects.update_or_create(
                month=previous_month, year=year,
                defaults={'amount': last_month_revenue,'completed': True},
            )

        # current month projected revenue
        current_revenue = sum([user['sub_price'] for user in self.paypal_user_list
                              if (user['state'] == 'active' and user['next_pay'].month == month)
                              or user['last_pay'].month == month])

        # save result to db
        PaypalRevenue.objects.update_or_create(
            month=month,
            year=year,
            defaults={'amount': current_revenue},
        )

        # prepare data for chart.js
        paypal_mrr = PaypalRevenue.objects.filter(completed=True).order_by('month', 'year')
        labels = []
        data = []

        # limit months in the chart to 24
        for _ in paypal_mrr[:24]:
            labels.append(month_name[_.month] + "\'" + str(year)[2:])
            data.append(str(_.amount))

        # add current month and current revenue to lists of data
        labels.append(month_name[month] + "\'" + str(year)[2:])
        data.append(str(current_revenue))

        data_for_chart = {
            'labels': labels,
            'data': data,
        }

        return json.dumps(data_for_chart)
