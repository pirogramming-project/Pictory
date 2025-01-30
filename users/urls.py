from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('', login_view , name='login'),
    path('signup/', signup , name='signup'),
    path('login_kakao/', kakao_login, name='login_kakao'),
    path('accounts/kakao/callback/', kakao_callback, name='login_kakao_callback')
]