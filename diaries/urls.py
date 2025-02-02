from django.urls import path
from .views import *

app_name = 'diaries'

urlpatterns = [
    path('create/', create_diary, name='create_diary'),
    path('create/type', select_photo_type, name='select_photo_type'),
    path('create/frame', select_frame, name='select_frame'),
    path('create/customize', custom_photo, name='custom_photo'),
    path('detail/<int:diary_id>/', diary_detail, name='diary_detail'),
    path('edit/<int:diary_id>/', edit_diary, name='edit_diary'),
]