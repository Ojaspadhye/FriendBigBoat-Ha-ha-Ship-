from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager

class FriendsUserManager(BaseUserManager):
    def create_user(self, username, emailid, phone_no, password=None):
        if not username or not emailid or not phone_no:
            raise ValueError("All fields required")
        user = self.model(username=username, emailid=emailid, phone_no=phone_no)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Friends_user(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    emailid = models.EmailField(max_length=200, unique=True)
    phone_no = models.CharField(max_length=15, unique=True)
    pfp = models.ImageField(upload_to='user_pfp/', blank=True, null=True)
    info = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['emailid', 'phone_no']

    objects = FriendsUserManager()

    def set_password(self, raw_password):
        return super().set_password(raw_password)
    
    def check_password(self, raw_password):
        return super().check_password(raw_password)

    def __str__(self):
        return self.username
