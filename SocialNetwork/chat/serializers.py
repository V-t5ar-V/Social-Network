from .models import *
from rest_framework import serializers
from django.utils import timezone

class ChatSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=40)
    description = serializers.CharField(max_length=500)
    icon = serializers.ImageField()

    class Meta:
        fields = ('id', 'name', 'description', 'icon')

    def to_representation(self, instance):
        request = self.context.get('request')
        view = self.context.get('view')

        if view and hasattr(view, 'action'):
            if view.action == 'list':
                data = {
                    'id': instance.id,
                    'name': instance.name,
                    'icon': instance.icon,
                }
            else:
                data = {
                    'id': instance.id,
                    'name': instance.name,
                    'description': instance.description,
                    'icon': instance.icon,
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
            elif icon.sixe > icon_max_size:
                raise serializers.ValidationError('Слишком большое изображение')
        return data


    def create(self, validated_data):
        chat = Chat.objects.create(**validated_data)
        ChatMember.objects.create(user=validated_data['user'], chat=chat.pk, is_admin=True)
        return chat


    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ChatMemberSerializer(serializers.Serializer):
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all(), read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), read_only=True)
    joined_at = serializers.DateTimeField(read_only=True, default=timezone.now)
    is_admin = serializers.BooleanField(default=False)

    class Meta:
        fields = ('chat', 'user', 'joined_at', 'is_admin')

    def create(self, validated_data):
        validated_data.pop('created_at', None)

        return ChatMember.objects.create(**validated_data)

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

# class MessageSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all(), read_only=True)
#     created_at = serializers.DateTimeField()
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), read_only=True)
#     text = serializers.CharField()

class StickerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), read_only=True)
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



