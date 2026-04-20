from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_private = models.BooleanField(default=False)
    blocked_users = models.ManyToManyField(User, blank=True, related_query_name='blocked_user')
    created_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    is_online = models.BooleanField(default=False)
    slug = models.SlugField(max_length=30, primary_key=True, editable=True)
    def __str__(self):
        return f'{self.slug}, name={self.user.username}'

class Subscription(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('following', 'follower')
