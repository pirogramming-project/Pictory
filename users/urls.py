from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('', login_view , name='login'),
    path('signup/', signup , name='signup'),
    path('naver/login/', naver_login, name='naver_login'),
    path('naver/login/', naver_login, name='naver_login'),  
    path('naver/callback/', naver_callback, name='naver_callback'),  
    path('login_kakao/', kakao_login, name='login_kakao'),
    path('accounts/kakao/callback/', kakao_callback, name='login_kakao_callback'),
]