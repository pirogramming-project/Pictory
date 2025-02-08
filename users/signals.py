from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Neighbor, NeighborRequest, Notification, Notification_TAG
from diaries.models import Diary


# 이웃 요청 모델에 뭔가 저장되면 실행됨.
@receiver(post_save, sender=NeighborRequest)
def create_NewFriendRequest_notification(sender, instance, created, **kwargs):
    """이웃 요청이 생성되면 알림을 생성하는 함수"""
    if created:  # 새로운 요청이 생성된 경우에만 실행
        Notification.objects.create(
            user=instance.receiver,
            type="NFR",
            message=f"@{instance.sender.nickname}님이 이웃을 요청했습니다."
        )
        
        
# 친구관계 모델에 뭔가 추가되면 실행됨.
@receiver(post_save, sender=Neighbor)
def create_FriendRequestAccepted_notification(sender, instance, created, **kwargs):
    """친구가 생기면 알림을 생성하는 함수"""
    if created:
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


# 유저태그 모델에 뭔가 추가되면 실행됨.
@receiver(m2m_changed, sender=Diary.user_tags.through)
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
