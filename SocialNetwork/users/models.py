from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=30, default='NoName')
    is_private = models.BooleanField(default=False)
    blocked_users = models.ManyToManyField(User, blank=True, related_query_name='blocked_user')
    created_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    is_online = models.BooleanField(default=False)
    slug = models.SlugField(max_length=30, unique=True, editable=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.slug}, name={self.user.username}'

class Subscription(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    subscription_status_choices = (('PENDING', 'pending'), ('ACCEPTED', 'accepted'), ('REJECTED', 'rejected'))
    subscription_status = models.CharField(max_length=10, choices=subscription_status_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    # class Meta:
    #     unique_together = ('following', 'follower')
    def __str__(self):
        return f'{self.pk}, following - {self.following}, follower - {self.follower}, is_accepted - {self.subscription_status}'
