from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Media, Tag, Comment, Like, PostView
from django.utils import timezone


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, default='', required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_at = serializers.DateTimeField(default=timezone.now, read_only=True)
    description = serializers.CharField(default="", max_length=500)
    tags = serializers.ManyRelatedField(queryset=Tag.objects.all(), required=False)
    slug = serializers.SlugField(max_length=100, required=False)
    media = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), many=True, required=False)
    class Meta:
        model = Post
        fields = ['title', 'user', 'created_at', 'description', 'tags', 'slug']

    def validate_media_size(self, values):
        for value in values:
            media_type = value.content_type
            if media_type == 'image/jpeg' or media_type == 'image/png':
                if value.size > 5*1024*1024:
                    raise serializers.ValidationError(f'Размер изображения {value} слишком большой (> 5мб).')
            if media_type == 'video/mp4' and value.size > 100*1024*1024:
                raise serializers.ValidationError(f'Размер видео {value} слишком большой (> 100мб).')

    def validate_media(self, values):
        allowed_types = ['image/jpeg', 'image/png', 'video/mp4']
        for value in values:
            if value not in allowed_types:
                raise serializers.ValidationError(f'Недопустимый тип медиа. {value})')
            if value.content_type == 'video/mp4' and len(values) > 1:
                raise serializers.ValidationError('добавление более 1 video не разрешено')
            elif value.content_type in {'image/jpeg', 'image/png'} and len(values) > 30:
                raise serializers.ValidationError('добавление более 30 image не разрешено')



    def create(self, validated_data):
        user = validated_data['user']
        media_files = validated_data['media']
        self.validate_media(media_files)
        self.validate_media_size(media_files)
        post = Post.objects.create(user=user, **validated_data)

        for media in media_files:
            mediafile = MediaSerializer(media, post=post)
            mediafile.save()
        return post




