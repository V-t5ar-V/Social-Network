from django.template.context_processors import media
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Media, Tag, Comment, Like, Post_View
from django.utils import timezone


class MediaSerializer(serializers.Serializer):
    file = serializers.FileField()
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    class Meta:
        model = Media
        fields = '__all__'

    def validate_media_size(self, values):
        for value in values:
            media_type = value.content_type
            if media_type == 'image/jpeg' or media_type == 'image/png':
                if value.size > 5 * 1024 * 1024:
                    raise serializers.ValidationError(f'Размер изображения {value} слишком большой (> 5мб).')
            if media_type == 'video/mp4' and value.size > 100 * 1024 * 1024:
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
        self.validate_media_size(validated_data.get('media', None))
        self.validate_media(validated_data.get('media', None))
        Media.objects.create(**validated_data)



class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, default='', required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_at = serializers.DateTimeField(default=timezone.now, read_only=True)
    description = serializers.CharField(default="", max_length=500)
    tags = serializers.ListField(child=serializers.SlugField(max_length=20), default=[])
    slug = serializers.SlugField(max_length=100, required=False)
    media = serializers.ListField(child=serializers.FileField(), default=[])
    class Meta:
        model = Post
        fields = ['title', 'user', 'created_at', 'description', 'tags', 'slug']

    def validate_video(self, value):
        max_video_size = 150 * 1024 * 1024

        if value.size > max_video_size:
            raise serializers.ValidationError('Слишком большое видео')
        return value

    def validate_image(self, value):
        max_image_size = 5 * 1024 * 1024

        if value.size > max_image_size:
            raise serializers.ValidationError('Слишком большое изображение')
        return value


    def validate_media_files(self, values):
        allowed_types = ['image/jpeg', 'image/png', 'video/mp4']
        media_types_list = list(map(lambda elem: elem.content_type, values))


        if len(values) > 30:
            raise serializers.ValidationError('Слишком много медиафайлов')
        if 'video/mp4' in media_types_list and len(values) > 1:
            raise serializers.ValidationError('Разрешено только 1 видео')


        for media_type in media_types_list:
            if media_type not in allowed_types:
                raise serializers.ValidationError('Недопустимый тип медиа.')


        for value in values:
            if value.content_type in {'image/jpeg', 'image/png'}:
                self.validate_image(value)
            elif value.content_type == 'video/mp4':
                self.validate_video(value)
        return values




    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        media_files = validated_data.pop('media', [])
        print(media_files)
        self.validate_media_files(media_files)

        post = Post.objects.create(**validated_data)
        for file in media_files:
            Media.objects.create(post=post, file=file)
        post.save()
        tags_objects = []
        if tags:
            for tag_name in tags:
                tag_obj, is_created = Tag.objects.get_or_create(tag=tag_name)
                if is_created:
                    tag_obj.save()
                tags_objects.append(tag_obj)
            post.tags.set(tags_objects)

        return post




