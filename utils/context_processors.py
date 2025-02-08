from users.models import Notification

def notification(request):
    if request.user.is_authenticated:
        current_user = request.user
        new_notification = Notification.objects.filter(user=current_user, is_read=False)    # 새 알림들 QuerySet
        new_notification_count = new_notification.count()   # 새 알림 개수
    else:
        new_notification = None
        new_notification_count = 0
        
    return {
        'new_notification': new_notification,
        'new_notification_count': new_notification_count,
        }
