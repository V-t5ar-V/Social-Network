import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

from django.utils import timezone

User = get_user_model()

class ProfileConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        token = self.scope['query_string'].decode().split('token=')[-1]
        self.user = await self.get_user(token)

        if self.user is None:
            await self.close()
            return
        user = self.user

        def set_online(user):
            user.profile.is_online = True
            user.profile.save()
        await database_sync_to_async(set_online)(user)
        await self.accept()

    async def disconnect(self, close_code):
        user = self.user
        def set_online(user):
            user.profile.is_online = False
            user.profile.save()
        await database_sync_to_async(set_online)(user)
        await self.close()

    @database_sync_to_async
    def get_user(self, token):
        try:
            data = AccessToken(token)
            return User.objects.get(id=data['user_id'])
        except Exception:
            return None