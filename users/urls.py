from django.conf import settings
from django.urls import path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    path('register-user/', RegisterView.as_view(), name='register-user'),
    path('user-email-verify-otp/', UserEmailVerifyOTP.as_view(),
         name='user-email-verify-otp'),
    path('login-user/', LoginView.as_view(), name='login-user'),
    path('get-all-user/', AllUserView.as_view(), name='get-all-user'),
    path(r'get-user/', UserView.as_view(), name='get-user'),
    path('user-edit/', UserEdit.as_view(), name='user-edit'),
    path('change-password/', ChangePasswordAPI.as_view(), name='change-password'),
    path('forgot-otp/', ForgotOtpAPI.as_view(), name='forgot-otp'),
    path('forgot-password/', ForgotPasswordAPI.as_view(), name='forgot-password'),
    path('delete-user/', DeleteUserAPI.as_view(), name='delete-user'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
