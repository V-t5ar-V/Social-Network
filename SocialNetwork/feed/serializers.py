from rest_framework import serializers
from .models import Post, Media, Tag, Comment, Like, Post_View
from django.utils import timezone
from django.contrib.auth.models import User


class MediaSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    class Meta:
        model = Media
        fields = '__all__'




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





    def to_representation(self, instance):
        request = self.context.get('request')
        media_files = []
        for media_obj in instance.media.all():
            file_url = media_obj.file.url if media_obj.file else None
            if request is not None and file_url is not None:
                file_url = request.build_absolute_uri(file_url)
            media_files.append(file_url)

        data = {
            'title': instance.title,
            'created_at': instance.created_at,
            'description': instance.description,
            'tags': [tag.tag for tag in instance.tags.all()],
            'slug': instance.slug,
            'media': media_files,
            'likes': instance.likes.count(),
            'comments': instance.comments.count(),
        }
        return data

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

        if len(values) > 30:
            raise serializers.ValidationError('Слишком много медиафайлов')

        media_types_list = list(map(lambda elem: elem.content_type, values))

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
        self.validate_media_files(media_files)

        post = Post.objects.create(**validated_data)
        for file in media_files:
            Media.objects.create(post=post, file=file)
        tags_objects = []
        if tags:
            for tag_name in tags:
                tag_obj, is_created = Tag.objects.get_or_create(tag=tag_name)
                if is_created:
                    tag_obj.save()
                tags_objects.append(tag_obj)
            post.tags.set(tags_objects)

        return post



class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text = serializers.CharField(max_length=200)
    created_at = serializers.DateTimeField(default=timezone.now, read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'text', 'user', 'created_at', 'parent', 'post']

    def create(self, validated_data):
        parent = validated_data.get('parent', None)
        if parent:
            if parent.post != validated_data['post']:
                raise serializers.ValidationError('Нельзя писать под постом дочерний комментарий, который написан под другим постом.')
        comment = Comment.objects.create(**validated_data)
        return comment

class LikeSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    created_at = serializers.DateTimeField(default=timezone.now, read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at', 'post']

    def to_representation(self, instance):

        data = {
            'slug': instance.post.slug,
            'like_id': instance.pk
        }

        return data

    def validate_like(self, user, post):
        queryset = Like.objects.filter(user=user, post=post)
        post_user = post.user

        if queryset.exists():
            raise serializers.ValidationError('Лайк уже существует.')

        if user != post_user:

            if user in post_user.profile.blocked_users.all():
                raise serializers.ValidationError('Лайк недоступен.')

            if post_user.profile.is_private and user not in post_user.followers.all():
                raise serializers.ValidationError('Только подписчики могут создать лайк.')

        return True

    def create(self, validated_data):
        self.validate_like(validated_data['user'], validated_data['post'])
        like = Like.objects.create(**validated_data)
        return like



