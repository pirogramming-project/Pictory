from django.db import models
from users.models import User
from datetime import date

########### 사진 관련 모델들 ###########
class Frame(models.Model):
    image_file = models.ImageField("최종 이미지 파일", upload_to="images/frames/%Y/%m/%d")
    
### 일기 관련 모델들 ###

# 감정점수
class EmotionRating(models.IntegerChoices):
    ONE = 1, "1점"
    TWO = 2, "2점"
    THREE = 3, "3점"
    FOUR = 4, "4점"
    FIVE = 5, "5점"
    SIX = 6, "6점"
    SEVEN = 7, "7점"

class Diary(models.Model):
    WEATHER_CHOICES = [
        ('sunny', '맑음'),
        ('partly_cloudy', '구름많음'),
        ('cloudy', '흐림'),
        ('rainy', '비'),
        ('snowy', '눈'),
        ('windy', '바람'),
    ]
    
    title = models.CharField("제목", max_length=40)
    writer = models.ForeignKey(User, models.CASCADE, verbose_name="작성자", related_name="wirte_diaries")
    date = models.DateField("날짜", default=date.today)
    four_cut_photo = models.ForeignKey(Frame, models.CASCADE, verbose_name="프레임", related_name="diaries")
    weather = models.CharField("날씨", max_length=20, choices=WEATHER_CHOICES, default='sunny')  # 기본값 '맑음'
    place = models.CharField("장소", max_length=40)
    place_address = models.CharField("실주소", max_length=120)
    emotion = models.IntegerField("감정지수", choices=EmotionRating.choices)
    # 태그들은 역참조 tags 이용
    user_tags = models.ManyToManyField(User, through='User_Tag', related_name="tagged_diaries") # 유저태그는 매니투매니필드 사용함~
    content = models.TextField("일기 내용")
    created_at = models.DateTimeField("생성 시간", auto_now_add=True)
    modified_at = models.DateTimeField("수정 시간", auto_now=True)
    
    # 추가: 좋아요랑 댓글부분 매니투매니로 정의함
    likers = models.ManyToManyField(User, through='Like', related_name='liked_diaries')
    comments = models.ManyToManyField(User, through='Comment', related_name='commented_diaries')

    def __str__(self):
        return f'{self.date}({self.writer})'
    
class Tag(models.Model):
    diary = models.ForeignKey(Diary, models.CASCADE,verbose_name="일기", related_name="tags")
    name = models.CharField("태그명", max_length=50)
    
    def __str__(self):
        return f'{self.name}({self.diary})'
    
class User_Tag(models.Model):
    diary = models.ForeignKey(Diary, models.CASCADE, related_name="tagged_diaries")
    user = models.ForeignKey(User, models.CASCADE, related_name="tagged_users")
    created_at = models.DateTimeField("태그 시간", auto_now_add=True)  # 태그된 시간 추가

    class Meta:
        unique_together = ('diary', 'user')
    
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # 좋아요 생성 시간 저장

    class Meta:
        unique_together = ('user', 'diary')  # 유저는 같은 일기에 한 번만 좋아요 가능


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 댓글 작성자
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE)  # 대상 일기
    comment_content = models.CharField("댓글 본문", max_length=150)  # 댓글 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 댓글 작성 시간
    modified_at = models.DateTimeField(auto_now=True)  # 댓글 수정 시간
    
    