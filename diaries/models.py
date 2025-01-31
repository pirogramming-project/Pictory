from django.db import models
from users.models import User


########### 사진 관련 모델들 ###########
class Frame(models.Model):
    frame_css = models.TextField("프레임 css")
    # 스티커는 역참조 stickers로 접근.
    # 사진들도 역참조 photos로 접근
    
class Photo(models.Model):
    frame = models.ForeignKey(Frame, models.CASCADE, related_name="photos")
    photo = models.ImageField("사진", upload_to="images/user_photos/%Y/%m/%d")


class Sticker(models.Model):
    frame = models.ForeignKey(Frame, models.CASCADE, related_name="stickers")
    sticker_image = models.FilePathField("스티커 이미지")
    coor_x = models.FloatField("x좌표")
    coor_y = models.FloatField("y좌표")
    
### 일기 관련 모델들 ###

# 감정점수
class EmotionRating(models.IntegerChoices):
    ZERO = 0, "0점"
    ONE = 1, "1점"
    TWO = 2, "2점"
    THREE = 3, "3점"
    FOUR = 4, "4점"
    FIVE = 5, "5점"
    SIX = 6, "6점"
    SEVEN = 7, "7점"
    EIGHT = 8, "8점"
    NINE = 9, "9점"
    TEN = 10, "10점"

class Diary(models.Model):
    title = models.CharField("제목", max_length=40)
    writer = models.ForeignKey(User, models.CASCADE, verbose_name="작성자", related_name="wirte_diaries")
    date = models.DateField("날짜")
    four_cut_photo = models.OneToOneField(Frame, models.CASCADE)
    # weather = "맑음", "흐림", "d/"/
    place = models.CharField("장소", max_length=40)
    emotion = models.IntegerField("감정지수", choices=EmotionRating.choices)
    # 태그들은 역참조 tags 이용
    user_tags = models.ManyToManyField(User, through='User_Tag', related_name="tagged_diaries") # 유저태그는 매니투매니필드 사용함~
    content = models.TextField("일기 내용")
    created_at = models.DateTimeField("생성 시간", auto_now_add=True)
    modified_at = models.DateTimeField("수정 시간", auto_now=True)
    
    
class Tags(models.Model):
    diary = models.ForeignKey(Diary, verbose_name="일기", related_name="tags")
    name = models.CharField("태그명", max_length=10)
    
class User_Tag(models.Model):
    diary = models.ForeignKey(Diary, models.CASCADE, related_name="user_tags")
    user = models.ForeignKey(User, models.CASCADE, related_name="user_tags")
    created_at = models.DateTimeField("태그 시간", auto_now_add=True)  # 태그된 시간 추가

    class Meta:
        unique_together = ('diary', 'user')