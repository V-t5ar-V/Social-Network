from .models import *
from rest_framework import serializers
from django.utils import timezone

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
        ChatMember.objects.create(user=user, chat=chat, is_admin=True)
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
    id = serializers.IntegerField()
    user = serializers.IntegerField()
    chat = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    content = serializers.CharField()
    content_type = serializers.CharField()
    parent = serializers.IntegerField(allow_null=True)

# class MessageSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all(), read_only=True)
#     created_at = serializers.DateTimeField()
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), read_only=True)
#     text = serializers.CharField()
#     parent = serializers.IntegerField()

class StickerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
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
            elif image.sixe > icon_max_size:
                raise serializers.ValidationError('Слишком большое изображение')
        return data

    def create(self, validated_data):
        keywords = []
        for keyword in validated_data.get('keywords', []):
            word, _ = Keyword.objects.get_or_create(keyword=keyword)
            keywords.append(word.pk)

        validated_data.pop('keywords', None)

        sticker = Sticker.objects.create(**validated_data, keywords=keywords)

        return sticker



