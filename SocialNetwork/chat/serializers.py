from .models import *
from rest_framework import serializers
from django.utils import timezone
from django.db import transaction

class ChatSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=40)
    description = serializers.CharField(max_length=500, allow_blank=True)
    icon = serializers.ImageField(required=False)

    class Meta:
        fields = ('id', 'name', 'description', 'icon')

    def to_representation(self, instance):
        request = self.context.get('request')
        view = self.context.get('view')
        icon = instance.icon.url if instance.icon else None
        icon_url = request.build_absolute_uri(icon) if icon else None

        if view and hasattr(view, 'action'):
            if view.action == 'list':
                data = {
                    'id': instance.id,
                    'name': instance.name,
                    'icon': icon_url,
                }
            else:
                data = {
                    'id': instance.id,
                    'name': instance.name,
                    'description': instance.description,
                    'icon': icon_url,
                }
        else:
            data = {
                'name': instance.name,
            }
        return data


    def validate(self, data):
        icon = data.get('icon', None)
        if icon is not None:
            allowed_types = ('image/png', 'image/jpeg')
            icon_max_size = 1024 * 1024 * 5
            if icon.content_type not in allowed_types:
                raise serializers.ValidationError('Недопустимый тип медиа')
            elif icon.size > icon_max_size:
                raise serializers.ValidationError('Слишком большое изображение')
        return data


    def create(self, validated_data):
        user = validated_data.pop('user')
        print(validated_data.get('icon', None))
        chat = Chat.objects.create(**validated_data)
        ChatMember.objects.create(member=user, chat=chat, is_admin=True)
        return chat


    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ChatMemberSerializer(serializers.Serializer):
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all())
    member = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    joined_at = serializers.DateTimeField(read_only=True, default=timezone.now)
    is_admin = serializers.BooleanField(default=False)


    class Meta:
        fields = ('chat', 'member', 'joined_at', 'is_admin')

    def to_representation(self, instance):
        request = self.context.get('request')
        view = self.context.get('view')
        data = {
            'id': instance.pk,
            "chat": instance.chat.pk,
            "member": instance.member.username,
            "joined_at": instance.joined_at,
            "is_admin": instance.is_admin,
        }
        return data

    def create(self, validated_data):
        validated_data.pop('created_at', None)
        chat = validated_data.pop('chat')
        member = validated_data.pop('member')
        chat_member_obj, created = ChatMember.objects.get_or_create(chat=chat, member=member)

        if not created:
            raise serializers.ValidationError({'title': 'Такой участник чата уже есть.',
                                               'chat':chat.pk,
                                               'member':member.username,
                                               'joined_at':chat_member_obj.joined_at,
                                               'is_admin':chat_member_obj.is_admin})

        return chat_member_obj

    def update(self, instance, validated_data):
        is_admin = validated_data.get('is_admin', False)
        instance.is_admin = is_admin
        instance.save()
        return instance



class ChatContentSerializer(serializers.Serializer):
    def to_representation(self, instance):
        request = self.context.get('request')
        data = {
            'id': instance.pk,
            'chat': instance.chat_id,
            'user': instance.user_id,
            'username': instance.user.username,
            'sent_at': instance.sent_at,
            'created_at': instance.sent_at,
            'parent': instance.parent_id,
        }

        if isinstance(instance, Message):
            data.update({
                'content_type': 'message',
                'content': instance.text,
                'text': instance.text,
                'status': instance.status,
            })
            return data

        image_url = instance.sticker.image.url if instance.sticker.image else None
        if request and image_url:
            image_url = request.build_absolute_uri(image_url)

        data.update({
            'content_type': 'sticker',
            'content': image_url,
            'sticker': instance.sticker_id,
            'image': image_url,
        })
        return data


class ChatMessageCreateSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    sticker = serializers.PrimaryKeyRelatedField(queryset=Sticker.objects.all(), required=False, allow_null=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), required=False, allow_null=True)

    def validate(self, data):
        text = data.get('text', '')
        sticker = data.get('sticker')

        if not text and sticker is None:
            raise serializers.ValidationError({'title': 'Нужно отправить текст, стикер или оба сразу.'})

        parent = data.get('parent')
        chat = self.context.get('chat')
        if parent and chat and parent.chat_id != chat.pk:
            raise serializers.ValidationError({'parent': 'Ответить можно только на сообщение из этого же чата.'})

        return data

    @transaction.atomic
    def create(self, validated_data):
        chat = self.context['chat']
        user = self.context['request'].user
        text = validated_data.get('text', '')
        sticker = validated_data.get('sticker')
        parent = validated_data.get('parent')

        created_content = []
        if text:
            created_content.append(Message.objects.create(
                chat=chat,
                user=user,
                text=text,
                parent=parent,
            ))

        if sticker is not None:
            created_content.append(StickerMessage.objects.create(
                chat=chat,
                user=user,
                sticker=sticker,
                parent=parent,
            ))

        return created_content

# class MessageSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all(), read_only=True)
#     created_at = serializers.DateTimeField()
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), read_only=True)
#     text = serializers.CharField()
#     parent = serializers.IntegerField()

class StickerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.ImageField()
    keywords = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        fields = ('id', 'author', 'image', 'keywords')

    def validate(self, data):
        image = data.get('image', None)
        if image is not None:
            allowed_types = ('image/png', 'image/jpeg')
            icon_max_size = 1024 * 1024 * 3
            if image.content_type not in allowed_types:
                raise serializers.ValidationError('Недопустимый тип медиа')
            elif image.size > icon_max_size:
                raise serializers.ValidationError('Слишком большое изображение')
        return data

    def create(self, validated_data):
        keywords = validated_data.pop('keywords', [])
        sticker = Sticker.objects.create(**validated_data)

        for keyword in keywords:
            word, _ = Keyword.objects.get_or_create(keyword=keyword)
            sticker.keywords.add(word)

        return sticker

    def to_representation(self, instance):
        request = self.context.get('request')
        image_url = instance.image.url if instance.image else None
        if request and image_url:
            image_url = request.build_absolute_uri(image_url)

        return {
            'id': instance.pk,
            'author': instance.author_id,
            'image': image_url,
            'keywords': list(instance.keywords.values_list('keyword', flat=True)),
        }



