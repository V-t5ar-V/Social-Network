import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from .models import (
    Message,
    Chat,
)

User = get_user_model()

class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        token = self.scope['query_string'].decode().split('token=')[-1]
        self.user = await self.get_user(token)

        if self.user is None:
            await self.close()
            return
        self.chat_pk = self.scope['url_route']['kwargs']['chat_pk']
        is_member = await self.is_chat_member(self.chat_pk, self.user)
        if not is_member:
            await self.close()
            return
        self.group_name = f"chat_{self.chat_pk}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        text = data.get('text', '').strip()
        if not text:
            await self.send(text_data=json.dumps({
                'error': 'Send text.'
            }))
            return

        message = await self.save_message(text)
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat.message',
            'message': message.text,
            'username': self.user.username,
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'text': event['message'],
        }))

    @database_sync_to_async
    def save_message(self, text):
        chat = Chat.objects.get(pk=self.chat_pk)
        return Message.objects.create(chat=chat, text=text, user=self.user, status=1)

    @database_sync_to_async
    def is_chat_member(self, chat_pk, user):
        return Chat.objects.filter(pk=chat_pk, members__member=user).exists()

    @database_sync_to_async
    def get_user(self, token):
        try:
            data = AccessToken(token)
            return User.objects.get(id=data['user_id'])
        except Exception:
            return None
