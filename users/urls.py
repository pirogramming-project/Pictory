from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('login/', login_view , name='login'),
    path('signup/', signup , name='signup'),
    path('naver/login/', naver_login, name='naver_login'),
    path('naver/login/', naver_login, name='naver_login'),  
    path('naver/callback/', naver_callback, name='naver_callback'),  
    path('login_kakao/', kakao_login, name='login_kakao'),
    path('accounts/kakao/callback/', kakao_callback, name='login_kakao_callback'),
    path('logout/', logout_view, name='logout'),
    path('', main , name='main'),
    path('main/', main , name='main'),
    path('profile/', profile, name='profile'),  
    path('alarm/', alarm, name='alarm'), 
    path('alarm_read_ajax/', alarm_read_ajax, name='alarm_read_ajax'), 
    path('search_ajax/', user_search_ajax, name="user_search_ajax"),
    path('send_friend_request_ajax/', send_friend_request_ajax, name="send_friend_request_ajax"),
    path('cancel_friend_request_ajax/', cancel_friend_request_ajax, name="cancel_friend_request_ajax"),
    path('reject_friend_request_ajax/', reject_friend_request_ajax, name="reject_friend_request_ajax"),
    path('diary/by_date/<int:year>/<int:month>/<int:day>/', get_diaries_by_date, name='diary_by_date'),
    path('update_profile_photo/', update_profile_photo, name='update_profile_photo'),
    path('diary/today/', get_today_diaries, name='today_diaries'),
    path('diary/last_week/', get_last_week_diaries, name='last_week_diaries'),
]