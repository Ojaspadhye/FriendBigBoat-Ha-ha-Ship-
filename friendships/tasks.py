from celery import shared_task
from .models import Friendship
from services.messages import db_channel_message_dump

@shared_task
def flush_all_channels():
    friendships = Friendship.objects.all()
    total = 0
    for f in friendships:
        total += db_channel_message_dump(f)
    return total