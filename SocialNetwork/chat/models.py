from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.

class Chat(models.Model):
    chat_name = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    icon = models.ImageField(upload_to='media/', null=True, blank=True)

class ChatMember(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='chats')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    class Meta:
        unique_together = ('chat', 'user')

class Message(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    message_statuses = [
        (1,'sent'),
        (2, 'delivered'),
        (3, 'read'),
    ]
    status = models.IntegerField(choices=message_statuses, default=1)

class StickerMessage(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='stickers')
    sticker = models.ForeignKey('Sticker', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

class Sticker(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, default=1, related_name='stickers')
    image = models.ImageField(upload_to='media/')
    keywords = models.ManyToManyField('Keyword', related_name='keywords')

class Keyword(models.Model):
    keyword = models.CharField(max_length=30, primary_key=True)