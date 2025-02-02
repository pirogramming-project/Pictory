from django.urls import path
from .views import *

app_name = 'diaries'

urlpatterns = [
    path('create/', create_diary, name='create_diary'),
    path('create/custom_photo', custom_photo, name='custom_photo'),
    path('detail/<int:diary_id>/', diary_detail, name='diary_detail'),
    path('edit/<int:diary_id>/', edit_diary, name='edit_diary'),
    path('community/', community, name='community'),
    path('friend_request/', friend_request, name='friend_request'),
    path('diary_map', diary_map, name='diary_map'),
]