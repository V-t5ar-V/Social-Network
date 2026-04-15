from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_private = models.BooleanField(default=False)
    blocked_users = models.ManyToManyField('self', related_name='blocked_users', null=True, blank=True, related_query_name='blocked_user')
    user_tag = models.CharField(max_length=20, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    is_online = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user_tag)
        if not self.user_tag:
            self.user_tag = slugify(self.user.username + self.user.id)

class Subscription(models.Model):
    following = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='following')
    follower = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='follower')
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('following', 'follower')