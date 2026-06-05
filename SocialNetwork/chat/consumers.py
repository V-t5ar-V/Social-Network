import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from .models import (
    Message,
    # StickerMessage,
    Chat,
    # ChatMember,
    User
)

class ChatConsumer(AsyncJsonWebsocketConsumer):

    @database_sync_to_async
    async def connect(self):
        token = self.scope['query_string'].decode().split('token=')[-1]
        self.user = await self.get_user(token)

        if self.user is None:
            await self.close()
            return
        self.chat_pk = self.scope['url_route']['kwargs']['chat_pk']
        chat = Chat.objects.get(pk=self.chat_pk)
        if chat.members.filter(user=self.user).exists():
            await self.close()
        self.group_name = f"chat_{self.chat_pk}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = await self.save_message(data['text'])
        await self.channel_layer.group_send(self.group_name, {
            'type': 'message',
            'message': message.text,
            'username': self.user.username
        })
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'text': event['message']
        }))

    @database_sync_to_async
    async def save_message(self, text):
        chat = Chat.objects.get(pk=self.chat_pk)
        parent = None
        return Message.objects.create(chat=chat, text=text, user=self.user, parent=parent, status='sent')

    @database_sync_to_async
    async def get_user(self, token):
        try:
            data = AccessToken(token)
            return User.objects.get(id=data['user_id'])
        except:
            return None

