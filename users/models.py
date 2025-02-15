from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class CustomUserManager(BaseUserManager):
    """
    커스텀 사용자 모델 관리자.
    """
    def create_user(self, login_id, password, **extra_fields):
        if not login_id:
            raise ValueError("로그인 아이디는 필수입니다.")
        if not password:
            raise ValueError("패스워드는 필수입니다.")
        
        user = self.model(login_id=login_id, nickname=login_id, **extra_fields)
        user.set_password(password)  # 비밀번호 해싱
        user.save(using=self._db)
        return user

    def create_superuser(self, login_id, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("슈퍼유저는 is_staff=True이어야 합니다.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("슈퍼유저는 is_superuser=True이어야 합니다.")

        return self.create_user(login_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    커스텀 사용자 모델.
    """

    login_id = models.CharField("로그인 아이디", max_length=50, primary_key=True, unique=True)  # 로그인 아이디
    password = models.CharField("패스워드", max_length=128)  # 비밀번호
    nickname = models.CharField("닉네임", max_length=50, unique=True)  # 닉네임
    profile_photo = models.ImageField("프로필 사진", default='images/default_images/default_profile_photo.png', upload_to="images/users/profile_photo/%Y/%m/%d")
    email = models.EmailField("이메일", null=True, blank=True, unique=True)
    birthday = models.DateField("생일", null=True, blank=True)
    created_at = models.DateTimeField("생성일시", auto_now_add=True)
    name = models.CharField("이름", max_length=50, null=True, blank=True)
    introduce = models.CharField("소개", max_length=50, null=True, blank=True) 

    # 추가 필드 (Django 인증 시스템과의 호환성)
    is_active = models.BooleanField(default=True)  # 계정 활성화 여부
    is_staff = models.BooleanField(default=False)  # 관리자 여부

    objects = CustomUserManager()

    USERNAME_FIELD = 'login_id'  # 사용자 인증 시 사용할 필드
    REQUIRED_FIELDS = ['email']  # 슈퍼유저 생성 시 필요한 필드

    def __str__(self):
        return f"{self.nickname}"


## 유저 이웃 관련 모델들
class NeighborRequest(models.Model):
    """이웃 추가 신청"""
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_neighbor_requests", verbose_name="신청 보낸 유저")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_neighbor_requests", verbose_name="신청 받은 유저")
    created_at = models.DateTimeField("생성시간", auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')  # 같은 유저에게 중복 신청 방지
                
    def __str__(self):
        return f"{self.sender} → {self.receiver}"


class Neighbor(models.Model):
    """이웃 관계"""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="neighbors1", verbose_name="이웃 A")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="neighbors2", verbose_name="이웃 B")
    created_at = models.DateTimeField("생성시간", auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_neighbor')
        ]

    def save(self, *args, **kwargs):
        """항상 user1 < user2 순서로 저장하여 중복 방지"""
        if self.user1.login_id > self.user2.login_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user1} ↔ {self.user2}"
    

## 배지 관련 모델들
class Badge(models.Model):
    """배지 정보"""
    id = models.CharField("식별자", max_length=20, primary_key=True, unique=True)
    image = models.FilePathField(
        "배지 이미지", 
        path='static/images/badges', 
        match=r".*\.(png|jpg|jpeg|gif|webp|bmp|tiff)$", 
        recursive=True
    )
    description = models.CharField("배지 설명", max_length=50)
    
    @property
    def image_url(self):
        """OS에 상관없이 항상 '/'로 경로를 변환"""
        return self.image.replace("\\", "/")

    def __str__(self):
        return f'{self.id} - {self.description}'


class UserBadge(models.Model):
    """유저가 획득한 배지"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="user_badges")
    created_at = models.DateTimeField("생성일시", auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')  # 동일한 유저가 같은 배지를 여러 번 받을 수 없도록 설정

    def __str__(self):
        return f"{self.user.nickname} - {self.badge.description}"


class Notification(models.Model):
    notification_type_choices = (
        ('SYS', 'system'),
        ('NFR', 'new friend request'),
        ('FRA', 'friend request accepted'),
        ('TAG', 'tagged'),
        ('NBA', 'new badge acquire')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField("알림 타입", max_length=10, choices=notification_type_choices, default='SYS')
    message = models.CharField("메시지", max_length=255)
    is_read = models.BooleanField("읽음", default=False)
    created_at = models.DateTimeField("생성일시", auto_now_add=True)
    # 역참조 nfr_notification
    # 역참조 tag_notification
    
    def __str__(self):
        return f"{self.user} - {self.message} ({self.id})"

class Notification_NFR(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, primary_key=True, related_name="nfr_notification")
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="related_notifications")

class Notification_TAG(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, primary_key=True, related_name="tag_notification")
    tagged_diary = models.ForeignKey('diaries.Diary', on_delete=models.CASCADE, related_name="related_notifications")

class Notification_NBA(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, primary_key=True, related_name="nba_notification")
    acquired_badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="related_notifications")

###### 사용하게 될 지도 모르는 utility 함수들
# def are_neighbors(user_a, user_b):
#     """두 유저가 이웃인지 확인"""
#     user1, user2 = sorted([user_a, user_b], key=lambda u: u.id)
#     return Neighbor.objects.filter(user1=user1, user2=user2).exists()