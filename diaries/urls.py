from django.urls import path
from .views import *

app_name = 'diaries'

urlpatterns = [
    path('create/', create_diary, name='create_diary'),
]