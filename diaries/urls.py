from django.urls import path
from .views import *

app_name = 'diaries'

urlpatterns = [
    path('create/<int:related_frame_id>/', create_diary, name='create_diary'),
    path('create/type', select_photo_type, name='select_photo_type'),
    path('create/frame', select_frame, name='select_frame'),
    path('create/customize/<int:frame_type>', custom_photo, name='custom_photo'),
    path('detail/<int:diary_id>/', diary_detail, name='diary_detail'),
    path('edit/<int:diary_id>/', edit_diary, name='edit_diary'),
    path('delete/<int:diary_id>/', delete_diary, name='delete_diary'),
    path('community/', community, name='community'),
    path('friend_request/', friend_request, name='friend_request'),
    path('diary_map', diary_map, name='diary_map'),
    path('by_date/<int:year>/<int:month>/<int:day>/', diaries_by_date, name='diaries_by_date'),
    path('mydiaries/', mydiaries, name='mydiaries'),
    path('upload_photo/', upload_photo, name='upload_photo'),
    path('mydiaries_tag_search_ajax/', mydiariesTagSearchAjax, name='mydiaries_tag_search_ajax'),
    path('community_tag_search_ajax/', communityTagSearchAjax, name='community_tag_search_ajax'),
    path('diaries/by_place/<str:place_name>/', diaries_by_place, name='diaries_by_place'),
]