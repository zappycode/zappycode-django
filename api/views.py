import datetime
import json
import requests
import environ
from allauth.account.forms import SignupForm
import allauth.account.utils
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from courses.models import Course
from .permissions import IsMember
from .serializers import CourseSerializer, CourseWithSectionsAndLecturesSerializer
from rest_framework import generics, permissions
from sitewide.models import ZappyUser
from django.core.mail import send_mail
import sentry_sdk


env = environ.Env()
environ.Env.read_env()


@csrf_exempt
def iap_signup(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        receipt = data['receipt']
        if ZappyUser.objects.filter(apple_receipt=receipt).exists():
            # return JsonResponse({'error': 'This In App Purchase has already been used. Please contact nick@ZappyCode.com', 'kick_out': True}, status=400)
            send_mail(
                'Check your api/views.py',
                'I think someone is double dipping on an already used IAP',
                'nick@zappycode.com',
                ['nick@zappycode.com'],
                fail_silently=False,
            )
        verify_url = 'https://buy.itunes.apple.com/verifyReceipt'
        
        receipt_json = json.dumps(
            {"receipt-data": receipt, 'password': env.str('APP_SHARED_SECRET', default='')})
        response = requests.request(
            method='POST',
            url=verify_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=receipt_json
        )
        
        res_json = response.json()
        
        if res_json['status'] == 21007:
            # Apple docs say try prod and if no dice, then do sandbox https://developer.apple.com/library/archive/technotes/tn2413/_index.html#//apple_ref/doc/uid/DTS40016228-CH1-RECEIPTURL
            response = requests.request(
                method='POST',
                url='https://sandbox.itunes.apple.com/verifyReceipt',
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data=receipt_json
            )

        res_json = response.json()
        try:
            request.POST._mutable = True
            request.POST['email'] = data['email']
            request.POST['password1'] = data['password']
            form = SignupForm(request.POST)
            form.is_valid()
            user = form.save(request)
            
            send_mail(
                'New Member from the App!',
                str(data['email']) + ' ' + str(res_json),
                'nick@zappycode.com',
                ['nick@zappycode.com'],
                fail_silently=False,
            )
            
            # TODO I need to put this back to normal
            # user.apple_product_id = res_json['latest_receipt_info'][-1]['product_id']
            # user.apple_expires_date = datetime.datetime.fromtimestamp(int(res_json['latest_receipt_info'][-1]['expires_date_ms']) / 1000)
            user.active_membership = True
            user.apple_receipt = receipt
            user.save()
            token = Token.objects.create(user=user)
            
            allauth.account.utils.send_email_confirmation(request, user)
            
            return JsonResponse({'token': str(token)}, status=201)
        except IntegrityError:
            sentry_sdk.capture_message("PSomething is wrong fam1", level="error")
            return JsonResponse({'error': 'That email has already been taken'},
                                status=400)
        except KeyError:
            sentry_sdk.capture_message("PSomething is wrong fam2", level="error")
            return JsonResponse({'error': 'We had problems verifying the receipt. Please contact nick@ZappyCode.com', 'kick_out': True},
                                status=400)
        except Exception as e:
            print(e)
            sentry_sdk.capture_message("PSomething is wrong fam3", level="error")
            return JsonResponse({'error': 'Something went wrong. Please contact nick@ZappyCode.com', 'kick_out': True},
                                status=400)


@csrf_exempt
def login(request):
    data = JSONParser().parse(request)
    user = authenticate(request, email=data['email'], password=data['password'])
    if user is None:
        return JsonResponse({'error': 'Could not login. Please check username and password'}, status=400)
    else:
        try:
            token = Token.objects.get(user=user)
        except:
            token = Token.objects.create(user=user)
        return JsonResponse({'token': str(token)}, status=200)


class CourseList(generics.ListAPIView):
    queryset = Course.objects.all().filter(published=True).order_by('-release_date')
    serializer_class = CourseSerializer


class CourseWithSectionsAndLectures(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMember]
    queryset = Course.objects.all()
    serializer_class = CourseWithSectionsAndLecturesSerializer
