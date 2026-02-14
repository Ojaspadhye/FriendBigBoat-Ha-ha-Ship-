import json
from django.db import transaction
from django.utils import timezone
from friendships.models import Messages
import redis



redis_client = redis.Redis(host="redis-13769.c245.us-east-1-3.ec2.cloud.redislabs.com", port=13769, db=0)

def db_channel_message_dump(channel):
    redis_key = f"chat:{channel.id}"
    raw_messages = redis_client.lrange(redis_key, 0, -1)

    if not raw_messages:
        return 0

    messages_to_create = []

    for raw in raw_messages:
        data = json.loads(raw.decode("utf-8"))
        messages_to_create.append(
            Messages(
                sender_id=data["sender"],
                receiver_id=data["receiver"],
                channel=channel,
                content=data["content"],
                timestamp=data.get("timestamp", timezone.now())
            )
        )

    with transaction.atomic():
        Messages.objects.bulk_create(messages_to_create)
        redis_client.delete(redis_key)

    return len(messages_to_create)

