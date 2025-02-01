from django.urls import path
from .views import *

app_name = 'diaries'

urlpatterns = [
    path('create/', create_diary, name='create_diary'),
    path('create/custom_photo', custom_photo, name='custom_photo'),
]