from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    private = models.BooleanField(default=False)
    blocked_users = models.ManyToManyField('self', related_name='blocked_users', null=True, blank=True, related_query_name='blocked_user')
    user_tag = models.CharField(max_length=20, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField()
    profile_pic = models.ImageField(upload_to='profile_pics')
    is_online = models.BooleanField(default=False)

class Subscription(models.Model):
    following = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='following')
    follower = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='follower')
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('following', 'follower')