from django.urls import path
from django.contrib.auth.views import (
    LogoutView
)
from .views import (
    IndexView,
    IntranetView,
    LoginView,
    RegistrationFormView,
    SuccessView,
    ResetPasswordView,
    ResetPasswordConfirmView,
    ResetPasswordCompleteView
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registrar/', RegistrationFormView.as_view(), name='registrar'),
    path('success/', SuccessView.as_view(), name='success'),
    path('intranet/', IntranetView.as_view(), name='intranet'),
    path('password-reset/', ResetPasswordView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', ResetPasswordCompleteView.as_view(), name='password_reset_complete'),
]
