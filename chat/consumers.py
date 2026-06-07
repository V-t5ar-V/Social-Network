import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from .models import (
    Message,
    Chat,
    StickerMessage,
    Sticker,
)
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.utils import timezone

User = get_user_model()

class TextMessageSerializer(serializers.Serializer):
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    text = serializers.CharField(required=True)
    sent_at = serializers.DateTimeField(required=False, default=timezone.now)
    parent = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), required=False, allow_null=True)
    class Meta:
        model = Message
        fields = ('chat', 'user', 'text', 'sent_at', 'parent')

    def to_representation(self, instance):
        data = {
            "chat": instance.chat.pk,
            "user": instance.user.username,
            "text": instance.text,
            "sent_at": instance.sent_at,
            "parent": instance.parent
        }
        return data

    def validate(self, data):
        try:
            parent_pk = data.get('parent', None)
            if parent_pk is not None:
                parent = Message.objects.get(pk=parent_pk)
                if parent.chat != data.get('chat'):
                    raise serializers.ValidationError("Нельзя ответить сообщению из другого чата")
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Такого сообщения не существует.")

        return data

    def create(self, data):
        text_message = Message.objects.create(**data)
        return text_message

class StickerMessageSerializer(serializers.Serializer):
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    sticker = serializers.PrimaryKeyRelatedField(queryset=Sticker.objects.all())
    sent_at = serializers.DateTimeField(required=False, default=timezone.now)
    parent = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), required=False, allow_null=True)
    class Meta:
        model = StickerMessage
        fields = ('chat', 'user', 'sticker', 'sent_at', 'parent')

    def validate(self, data):
        try:
            parent_pk = data.get('parent', None)
            if parent_pk is not None:
                parent = Message.objects.get(pk=parent_pk)
                if parent.chat != data.get('chat'):
                    raise serializers.ValidationError("Нельзя ответить сообщению из другого чата")
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Такого сообщения не существует.")

        return data

    def to_representation(self, instance):
        data = {
            "chat": instance.chat.pk,
            "user": instance.user.username,
            "sticker": instance.sticker.pk,
            "sent_at": instance.sent_at,
            "parent": instance.parent
        }
        return data

    def create(self, data):
        sticker_message = StickerMessage.objects.create(**data)
        return sticker_message



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
        try:
            data = json.loads(text_data)
        except json.decoder.JSONDecodeError as e:
            await self.send(text_data=json.dumps({"error": e}))
            return



        try:
            content_type = data.get('type', None)
            content = data.get('content', None)
            parent = data.get('parent', None)

            if content_type == 'text':
                print("text")
                text = content.strip()
                serializer = TextMessageSerializer(data={
                    'chat': self.chat_pk,
                    'user':self.user.pk,
                    'text': text,
                    'parent': parent
                })

            elif content_type == 'sticker':
                print("sticker")
                sticker = content
                serializer = StickerMessageSerializer(data={
                    'chat': self.chat_pk,
                    'user':self.user.pk,
                    'sticker': sticker,
                    'parent': parent
                })
            else:
                raise ValidationError("Укажите тип сообщения. (text/sticker)")

            await database_sync_to_async(serializer.is_valid)(raise_exception=True)
            await database_sync_to_async(serializer.save)()

        except ValidationError as e:
            await self.send(json.dumps({
                "type": "error",
                "detail": e.detail if isinstance(e.detail, str) else str(e.detail),
            }))

        else:
            await self.channel_layer.group_send(self.group_name, {
                "type": "chat_message",
                "text": serializer.data
            })


    async def chat_message(self, event):
        print(event)
        message = event['text']
        print(message)
        await self.send(text_data=json.dumps(
            message
        , ensure_ascii=False, default=str))


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
