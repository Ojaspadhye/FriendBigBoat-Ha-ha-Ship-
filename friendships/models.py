from django.db import models
from django.db.models import Q, F

# Create your models here.


class Friendship(models.Model):
    id = models.BigAutoField(primary_key=True)
    from_friend = models.ForeignKey('friends_user.Friends_user', on_delete=models.CASCADE, related_name="from_friend")
    to_friend = models.ForeignKey('friends_user.Friends_user', on_delete=models.CASCADE, related_name="to_friend")
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
