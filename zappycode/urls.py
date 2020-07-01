from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
import sitewide.views
import challenge.views
import courses.views

urlpatterns = [
                  path('', sitewide.views.home, name='home'),
                  path('admin/', admin.site.urls),
                  path('courses/', include('courses.urls')),
                  path('auth/', include('allauth.urls')),
                  path('posts/', include('posts.urls')),
                  path('money/', include('money.urls')),
                  path('account/', sitewide.views.account, name='account'),
                  path('pricing/', sitewide.views.pricing, name='pricing'),
                  path('checkout/', sitewide.views.checkout, name='checkout'),
                  path('payment_success/', sitewide.views.payment_success, name='payment_success'),
                  path('cancel_subscription/', sitewide.views.cancel_subscription, name='cancel_subscription'),
                  path('challenge/<int:pk>', challenge.views.challenge, name='challenge'),

                  # API
                  path('api/courses', courses.views.CourseList.as_view()),

                  # These are all direct links
                  path('do/', RedirectView.as_view(url='https://m.do.co/c/1d911d0ac384')),
                  path('binance/', RedirectView.as_view(url='https://www.binance.com/?ref=18195758')),
                  path('coinbase/', RedirectView.as_view(url='https://www.coinbase.com/join/54c17a1cc5f6ec44cb000050')),
                  path('bluehost/', RedirectView.as_view(url='http://www.bluehost.com/track/zappycode/html5course')),
                  path('slack/', RedirectView.as_view(
                      url='https://docs.google.com/forms/d/e/1FAIpQLSdDM916hc-5adMAqkGkd68ojMCMeVQ788xQbxn9U7yGXmTiLA/viewform')),
                  path('help/', RedirectView.as_view(
                      url='https://docs.google.com/forms/d/e/1FAIpQLSdDM916hc-5adMAqkGkd68ojMCMeVQ788xQbxn9U7yGXmTiLA/viewform')),
                  path('djangoguide/', RedirectView.as_view(
                      url='https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04')),
                  path('vultr/', RedirectView.as_view(url='http://www.vultr.com/?ref=7055847-3B')),
                  path('mac/', RedirectView.as_view(
                      url='https://www.udemy.com/macos-programming-for-ios-developers-mac-apps-os-x-cocoa/?couponCode=YOUTUBEMAC')),
                  path('pa/', RedirectView.as_view(url='https://www.pythonanywhere.com/?affiliate_id=006444cc')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,
                                                                                         document_root=settings.STATIC_ROOT)
