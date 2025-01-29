from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('', login , name='login'),
    path('signup/', signup , name='signup'),
    path('naver/login/', naver_login, name='naver_login'),
    path('naver/login/', naver_login, name='naver_login'),  
    path('naver/callback/', naver_callback, name='naver_callback'),  
]