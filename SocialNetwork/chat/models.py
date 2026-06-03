from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.

class Chat(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    icon = models.ImageField(upload_to='media/', null=True, blank=True)

    def __str__(self):
        return f"chat_{self.pk}-{self.name}"

class ChatMember(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='members')
    member = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='chats')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    class Meta:
        unique_together = ('chat', 'member')

    def __str__(self):
        return f"чат: {self.chat.name}_{self.chat.pk} - {self.member.username}"

class Message(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    message_statuses = [
        (1,'sent'),
        (2, 'delivered'),
        (3, 'read'),
    ]
    status = models.IntegerField(choices=message_statuses, default=1)

    def __str__(self):
        return f"{self.chat.name} - {self.user.username}, pk: {self.pk}"

class StickerMessage(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='stickers')
    sticker = models.ForeignKey('Sticker', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('Message', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.chat.name} - {self.user.username}, pk: {self.pk}"

class Sticker(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, default=1, related_name='stickers')
    image = models.ImageField(upload_to='media/')
    keywords = models.ManyToManyField('Keyword', related_name='keywords')

    def __str__(self):
        return f"{self.author.name} - {self.pk}"

class Keyword(models.Model):
    keyword = models.CharField(max_length=30, primary_key=True)

    def __str__(self):
        return self.keyword