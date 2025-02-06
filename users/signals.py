from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NeighborRequest, Notification


# 이웃 요청 모델에 뭔가 저장되면 실행됨.
@receiver(post_save, sender=NeighborRequest)
def create_diary_notification(sender, instance, created, **kwargs):
    """이웃 요청이 생성되면 알림을 생성하는 함수"""
    if created:  # 새로운 요청이 생성된 경우에만 실행
        Notification.objects.create(
            user=instance.receiver,
            type="NFR",
            message=f"{instance.sender.nickname}님이 이웃을 요청했습니다."
        )
