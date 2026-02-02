from django.db import models
from django.db.models import Q, F

# Create your models here.

## There is a cool thing that if i dont change it there will be a kind of issue that A -> B and B -> A would be kind of treated differently
class Friendship(models.Model):
    id = models.BigAutoField(primary_key=True)
    friend1 = models.ForeignKey('friends_user.Friends_user', on_delete=models.CASCADE, related_name="friend1")
    friend2 = models.ForeignKey('friends_user.Friends_user', on_delete=models.CASCADE, related_name="friend2")
    sender = models.ForeignKey('friends_user,Friends_user', on_delete=models.CASCADE, related_name="request_sender")
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
            models.UniqueConstraint(
                fields=["from_friend", "to_friend"],
                name="unique_requests"
            ),
            models.CheckConstraint(
                condition=~Q(from_friend=F("to_friend")),
                name="prevent_self_friendship"
            )
        ]
