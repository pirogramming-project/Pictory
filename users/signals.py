from django.db.models.signals import post_save, m2m_changed
from django.db import transaction
from django.dispatch import receiver
from .models import Neighbor, NeighborRequest, Notification, Notification_NFR, Notification_TAG, Badge, UserBadge
from diaries.models import Diary
from django.db.models import Q



# 이웃 요청 모델에 뭔가 저장되면 실행됨.
@receiver(post_save, sender=NeighborRequest)
@transaction.atomic
def create_NewFriendRequest_notification(sender, instance, created, **kwargs):
    """이웃 요청이 생성되면 알림을 생성하는 함수"""
    if created:  # 새로운 요청이 생성된 경우에만 실행
        new_notification = Notification.objects.create(
            user=instance.receiver,
            type="NFR",
            message=f"@{instance.sender.nickname}님이 이웃을 요청했습니다."
        )
        Notification_NFR.objects.create(
            notification=new_notification,
            from_user=instance.sender
        )
        
# 친구관계 모델에 뭔가 추가되면 실행됨.
@receiver(post_save, sender=Neighbor)
@transaction.atomic
def create_FriendRequestAccepted_notification(sender, instance, created, **kwargs):
    """친구가 생기면 알림을 생성하는 함수"""
    if created:
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
        if user1NeighborCounts == 1:
            UserBadge.objects.get_or_create(
                user=instance.user1,
                badge=Badge.objects.get(id='neighbor_1st')
            )
        elif user1NeighborCounts == 10:
                UserBadge.objects.get_or_create(
                user=instance.user1,
                badge=Badge.objects.get(id='neighbor_10th')
            )
        elif user1NeighborCounts == 30:
                UserBadge.objects.get_or_create(
                user=instance.user1,
                badge=Badge.objects.get(id='neighbor_30th')
            )
        elif user1NeighborCounts == 50:
                UserBadge.objects.get_or_create(
                user=instance.user1,
                badge=Badge.objects.get(id='neighbor_50th')
            )
        elif user1NeighborCounts == 100:
                UserBadge.objects.get_or_create(
                user=instance.user1,
                badge=Badge.objects.get(id='neighbor_100th')
            )
        if user2NeighborCounts == 1:
            UserBadge.objects.get_or_create(
                user=instance.user1,
                badge=Badge.objects.get(id='neighbor_1st')
            )
        elif user2NeighborCounts == 10:
                UserBadge.objects.get_or_create(
                user=instance.user1,
                badge=Badge.objects.get(id='neighbor_10th')
            )
        elif user2NeighborCounts == 30:
                UserBadge.objects.get_or_create(
                user=instance.user1,
                badge=Badge.objects.get(id='neighbor_30th')
            )
        elif user2NeighborCounts == 50:
                UserBadge.objects.get_or_create(
                user=instance.user1,
                badge=Badge.objects.get(id='neighbor_50th')
            )
        elif user2NeighborCounts == 100:
                UserBadge.objects.get_or_create(
                user=instance.user1,
                badge=Badge.objects.get(id='neighbor_100th')
            )


# 유저태그 모델에 뭔가 추가되면 실행됨.
@receiver(m2m_changed, sender=Diary.user_tags.through)
@transaction.atomic
def create_tagged_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    """일기에서 태그된 유저에게 알림을 보내는 함수"""
    if action == "post_add":  # ManyToManyField에 새로운 값이 추가될 때만 실행
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


# 일기 모델에 뭔가 저장되면 실행됨.
@receiver(post_save, sender=Diary)
@transaction.atomic
def create_Diary_signal(sender, instance, created, **kwargs):
    """일기 수 관련 배지 지급"""
    if created:  # 새로운 일기가 생성된 경우에만 실행
        writer = instance.writer
        diaryCount = Diary.objects.filter(writer=instance.writer).count()
        
        if diaryCount == 1:
            UserBadge.objects.get_or_create(
                user=writer,
                badge=Badge.objects.get(id='diary_1st')
            )
        elif diaryCount == 10:
                UserBadge.objects.get_or_create(
                user=writer,
                badge=Badge.objects.get(id='diary_10th')
            )
        elif diaryCount == 30:
                UserBadge.objects.get_or_create(
                user=writer,
                badge=Badge.objects.get(id='diary_30th')
            )
        elif diaryCount == 50:
                UserBadge.objects.get_or_create(
                user=writer,
                badge=Badge.objects.get(id='diary_50th')
            )
        elif diaryCount == 100:
                UserBadge.objects.get_or_create(
                user=writer,
                badge=Badge.objects.get(id='diary_100th')
            )
