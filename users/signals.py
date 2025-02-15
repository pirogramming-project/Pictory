from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.dispatch import receiver
from .models import Neighbor, NeighborRequest, Notification, Notification_NFR, Notification_TAG, Notification_NBA, Badge, UserBadge
from diaries.models import Diary
from django.db.models import Q
from datetime import timedelta
from django.utils.timezone import now

@receiver(user_logged_in)
def check_anniversary(sender, request, user, **kwargs):
    """유저가 가입한 지 1년이 넘었으면 배지를 추가"""
    if user.created_at + timedelta(days=365) <= now():
        UserBadge.objects.get_or_create(
            user=user,
            badge=Badge.objects.get(id='register_1year')
        )

# 이웃 요청 모델에 뭔가 저장되면 실행됨.
@receiver(post_save, sender=NeighborRequest)
def create_NewFriendRequest_notification(sender, instance, created, **kwargs):
    """이웃 요청이 생성되면 알림을 생성하는 함수"""
    if created:  # 새로운 요청이 생성된 경우에만 실행
        def notify():
            new_notification = Notification.objects.create(
                user=instance.receiver,
                type="NFR",
                message=f"@{instance.sender.nickname}님이 이웃을 요청했습니다."
            )
            Notification_NFR.objects.create(
                notification=new_notification,
                from_user=instance.sender
            )
            
        transaction.on_commit(notify)
        
        
# 유저 배지 모델에 뭔가 저장되면 실행됨.
@receiver(post_save, sender=UserBadge)
def create_NewBadge_notification(sender, instance, created, **kwargs):
    """유저가 배지를 받으면 알림을 생성하는 함수"""
    if created:  # 새로운 요청이 생성된 경우에만 실행
        def notify():
            new_notification = Notification.objects.create(
                user=instance.user,
                type="NBA",
                message=f"배지를 획득했어요! 축하해요!"
            )
            Notification_NBA.objects.create(
                notification=new_notification,
                acquired_badge=instance.badge
            )
            
        transaction.on_commit(notify)

        
# 친구관계 모델에 뭔가 추가되면 실행됨.
@receiver(post_save, sender=Neighbor)
def create_FriendRequestAccepted_notification(sender, instance, created, **kwargs):
    """친구가 생기면 알림을 생성하는 함수"""
    if created:
        def notify():
            ## 1. 알림 만들기
            Notification.objects.create(
                user=instance.user1,
                type="FRA",
                message=f"@{instance.user2.nickname}님과 이웃이 되었습니다."
            )
            Notification.objects.create(
                user=instance.user2,
                type="FRA",
                message=f"@{instance.user1.nickname}님과 이웃이 되었습니다."
            )
        
            ## 2. 배지 지급
            user1NeighborCounts = Neighbor.objects.filter(Q(user1=instance.user1) | Q(user2=instance.user1)).count()
            user2NeighborCounts = Neighbor.objects.filter(Q(user1=instance.user2) | Q(user2=instance.user2)).count()
            if user1NeighborCounts >= 1:
                UserBadge.objects.get_or_create(
                    user=instance.user1,
                    badge=Badge.objects.get(id='neighbor_1st')
                )
            if user1NeighborCounts >= 10:
                UserBadge.objects.get_or_create(
                    user=instance.user1,
                    badge=Badge.objects.get(id='neighbor_10th')
                )
            if user1NeighborCounts >= 30:
                UserBadge.objects.get_or_create(
                    user=instance.user1,
                    badge=Badge.objects.get(id='neighbor_30th')
                )
            if user1NeighborCounts >= 50:
                UserBadge.objects.get_or_create(
                    user=instance.user1,
                    badge=Badge.objects.get(id='neighbor_50th')
                )
            if user1NeighborCounts >= 100:
                UserBadge.objects.get_or_create(
                    user=instance.user1,
                    badge=Badge.objects.get(id='neighbor_100th')
                )
            if user2NeighborCounts >= 1:
                UserBadge.objects.get_or_create(
                    user=instance.user2,
                    badge=Badge.objects.get(id='neighbor_1st')
                )
            if user2NeighborCounts >= 10:
                UserBadge.objects.get_or_create(
                    user=instance.user2,
                    badge=Badge.objects.get(id='neighbor_10th')
                )
            if user2NeighborCounts >= 30:
                UserBadge.objects.get_or_create(
                    user=instance.user2,
                    badge=Badge.objects.get(id='neighbor_30th')
                )
            if user2NeighborCounts >= 50:
                UserBadge.objects.get_or_create(
                    user=instance.user2,
                    badge=Badge.objects.get(id='neighbor_50th')
                )
            if user2NeighborCounts >= 100:
                UserBadge.objects.get_or_create(
                    user=instance.user2,
                    badge=Badge.objects.get(id='neighbor_100th')
                )
                
        transaction.on_commit(notify)


# 유저태그 모델에 뭔가 추가되면 실행됨.
@receiver(m2m_changed, sender=Diary.user_tags.through)
def create_tagged_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    """일기에서 태그된 유저에게 알림을 보내는 함수"""
    if action == "post_add":  # ManyToManyField에 새로운 값이 추가될 때만 실행
        def notify():
            for user_id in pk_set:  # 태그된 유저들의 ID 목록
                user = model.objects.get(pk=user_id)  # User 모델의 객체 가져오기
                new_notification = Notification.objects.create(
                    user=user,
                    type="TAG",
                    message=f"@{instance.writer.nickname}님이 당신을 태그했습니다."
                )
                Notification_TAG.objects.create(
                    notification=new_notification,
                    tagged_diary=instance
                )

        # 트랜잭션이 완전히 커밋된 후 실행되도록 설정
        transaction.on_commit(notify)

# 일기 모델에 뭔가 저장되면 실행됨.
@receiver(post_save, sender=Diary)
def create_Diary_signal(sender, instance, created, **kwargs):
    """일기 수 관련 배지 지급"""
    if created:  # 새로운 일기가 생성된 경우에만 실행
        def notify():
            writer = instance.writer
            diaryCount = Diary.objects.filter(writer=instance.writer).count()
            
            if diaryCount >= 1:
                UserBadge.objects.get_or_create(
                    user=writer,
                    badge=Badge.objects.get(id='diary_1st')
                )
            if diaryCount >= 10:
                UserBadge.objects.get_or_create(
                    user=writer,
                    badge=Badge.objects.get(id='diary_10th')
                )
            if diaryCount >= 30:
                UserBadge.objects.get_or_create(
                    user=writer,
                    badge=Badge.objects.get(id='diary_30th')
                )
            if diaryCount >= 50:
                UserBadge.objects.get_or_create(
                    user=writer,
                    badge=Badge.objects.get(id='diary_50th')
                )
            if diaryCount >= 100:
                UserBadge.objects.get_or_create(
                    user=writer,
                    badge=Badge.objects.get(id='diary_100th')
                )
                    
            if(has_written_7_days_consecutively(writer)):
                UserBadge.objects.get_or_create(
                    user=writer,
                    badge=Badge.objects.get(id='diary_7days')
                )
        transaction.on_commit(notify)

# util함수
def has_written_7_days_consecutively(user):
    """유저가 7일 연속으로 일기를 작성했는지 확인"""
    # 현재 날짜 기준으로 최근 7일 동안 작성한 날짜 가져오기 (중복 제거)
    diary_dates = (
        Diary.objects
        .filter(writer=user)
        .values('created_at__date')  # 날짜별 그룹화
        .order_by('-created_at__date') # 최신 날짜부터 정렬
    )

    # 중복 제거된 날짜 리스트 생성
    date_list = [entry['created_at__date'] for entry in diary_dates]

    # 연속된 7일이 있는지 확인
    if len(date_list) < 7:
        return False  # 작성한 날짜가 7일 미만이면 False
    
    for i in range(6):
        if (date_list[i] - date_list[i + 1]) != timedelta(days=1):
            return False  # 연속되지 않은 날짜가 있으면 False 반환

    return True  # 모든 날짜가 연속된 경우 True 반환
