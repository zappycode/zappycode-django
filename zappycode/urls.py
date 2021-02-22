from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
import chit_chat.views
from django.views.generic import RedirectView, TemplateView
from django.contrib.sitemaps.views import sitemap
from .sitemap import StaticViewSitemap, CourseSitemap, MoneySitemap 
import sitewide.views
import challenge.views
import courses.views
import allauth.account.views
import sitewide

sitemaps = {
     'static': StaticViewSitemap,
     'courses': CourseSitemap,
     'money': MoneySitemap,
}

handler404 = 'sitewide.views.error404'

urlpatterns = [
                  path('', sitewide.views.home, name='home'),
                  path('admin/', admin.site.urls),
                  path('check', sitewide.views.check_active_memberships, name='check_membership'),
                  path('courses', include('courses.urls')),
                  path('api', include('api.urls')),
                  path('posts', include('posts.urls')),
                  path('money', include('money.urls')),
                  path('somebodylovesyou', include('invites.urls')),
                  path('account', sitewide.views.account, name='account'),
                  path('pricing', sitewide.views.pricing, name='pricing'),
                  path('payment_success', sitewide.views.payment_success, name='payment_success'),
                  path('cancel_subscription/<str:membership>', sitewide.views.cancel_subscription, name='cancel_subscription'),
                  path('challenge/<int:pk>', challenge.views.challenge, name='challenge'),
                  path('newsletter', sitewide.views.newsletter, name='newsletter'),
                  path('paypal', sitewide.views.paypal, name='paypal'),
                  path('paypal_validation', sitewide.views.paypal_validation, name='paypal_validation'),
                  path('discourse/sso', chit_chat.views.discourse_sso, name='discourse_sso'),
                  path('tinymce/', include('tinymce.urls')),

                  path("robots.txt", TemplateView.as_view(template_name="sitewide/robots.txt", content_type="text/plain")),
                  path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),

                  # Auth
                  path("auth/signup", allauth.account.views.signup, name="account_signup"),
                  path("login", allauth.account.views.login, name="account_login"),
                  path("logout", allauth.account.views.logout, name="account_logout"),
                  path("password/change", allauth.account.views.password_change,
                       name="account_change_password"),
                  path("password/set", allauth.account.views.password_set, name="account_set_password"),
                  path("inactive", allauth.account.views.account_inactive, name="account_inactive"),

                  # Auth E-mail
                  path("email", allauth.account.views.email, name="account_email"),
                  path("confirm-email", allauth.account.views.email_verification_sent,
                       name="account_email_verification_sent"),
                  re_path(r"^confirm-email/(?P<key>[-:\w]+)/$", allauth.account.views.confirm_email,
                          name="account_confirm_email"),

                  # Auth Password reset
                  path("password/reset", allauth.account.views.password_reset,
                       name="account_reset_password"),
                  path("password/reset/done", allauth.account.views.password_reset_done,
                       name="account_reset_password_done"),
                  re_path(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
                          allauth.account.views.password_reset_from_key,
                          name="account_reset_password_from_key"),
                  path("password/reset/key/done", allauth.account.views.password_reset_from_key_done,
                       name="account_reset_password_from_key_done"),

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
                  path('weekend/', RedirectView.as_view(url='https://zappycode.com/posts/15/python-in-a-weekend')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,
                                                                                         document_root=settings.STATIC_ROOT)
