from django.conf import settings
from django.urls import path

from account.views import PricingView, RegisterUser, LogoutUser, LoginUser, UpdateUser, MustAuthenticate, CheckoutView, \
    PasswordChangeViewP, DeleteAccountView

app_name = 'account'

urlpatterns = [

    path('pricing/', PricingView.as_view(), name='pricing'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', LogoutUser.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),
    path('login/', LoginUser.as_view(), name='login'),
    path('', UpdateUser.as_view(), name='account'),
    path('must_authenticate/', MustAuthenticate.as_view(), name='must_authenticate'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('<int:pk>/delete', DeleteAccountView.as_view(), name='delete'),
    path('password_change/', PasswordChangeViewP.as_view(template_name='registration/password_change.html'),
         name='password_change'),
]