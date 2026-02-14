from django.db import models
from django.db.models import Q, F

# Create your models here.

## There is a cool thing that if i dont change it there will be a kind of issue that A -> B and B -> A would be kind of treated differently
class Friendship(models.Model):
    id = models.BigAutoField(primary_key=True)
    friend1 = models.ForeignKey('friends_user.Friends_user', on_delete=models.CASCADE, related_name="friendship_as_friend1")
    friend2 = models.ForeignKey('friends_user.Friends_user', on_delete=models.CASCADE, related_name="friendship_as_friend2")
    sender = models.ForeignKey('friends_user.Friends_user', on_delete=models.CASCADE, related_name="friendship_as_sender")
        
    status_choices = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('BLOCKED', 'Blocked'),
        ('REJECT', 'Reject')
    ]
    status = models.CharField(blank=False, choices=status_choices)
    
    from_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["friend1", "friend2"], name="unique_requests"),
            models.CheckConstraint(condition=~Q(friend1=F("friend2")), name="prevent_self_friendship")
        ]


class Messages(models.Model):
    id = models.BigAutoField(primary_key=True)
    channel = models.ForeignKey('Friendship', on_delete=models.CASCADE, related_name="messages")
    content = models.CharField(max_length=200)
    sender = models.ForeignKey('friends_user.Friends_user', on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey('friends_user.Friends_user', on_delete=models.CASCADE, related_name="received_messages")
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~Q(sender=F("receiver")), name="prevent_self_message")
        ]
