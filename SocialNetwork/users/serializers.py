from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import Profile, Subscription

class ProfileSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_private = serializers.BooleanField(default=False, allow_null=True)
    blocked_users = serializers.PrimaryKeyRelatedField(many=True, queryset=Profile.objects.all(), required=False)
    user_tag = serializers.CharField(max_length=20)
    bio = serializers.CharField(max_length=750, required=False, allow_null=True, allow_blank=True)
    profile_pic = serializers.FileField(required=False, allow_null=True)
    is_online = serializers.BooleanField(default=False, read_only=True)
    slug = serializers.SlugField(allow_null=True, read_only=True)

    class Meta:
        model = Profile
        fields = ('user','is_private', 'blocked_users', 'user_tag', 'bio', 'profile_pic', 'is_online', 'slug')


    def create(self, validated_data):
        blocked_users = validated_data.pop('blocked_users', [])
        profile = Profile.objects.create(
            user=validated_data['user'],
            user_tag=validated_data['user_tag'],
            is_private=validated_data.get('is_private', False),
            bio=validated_data.get('bio'),
            profile_pic=validated_data.get('profile_pic'),
        )
        if blocked_users:
            profile.blocked_users.set(blocked_users)
        return profile

    def update(self, instance, validated_data):
        validated_data.pop('user', None)
        blocked_users = validated_data.pop('blocked_users', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if blocked_users is not None:
            instance.blocked_users.set(blocked_users)
        return instance

    def validate_user_tag(self, value):
        slug = slugify(value)
        if not slug:
            raise serializers.ValidationError('На ТЕГ должны быть буквы или цифры.')
        profiles = Profile.objects.filter(user_tag=value)
        slugs = Profile.objects.filter(slug=slug)
        if self.instance is not None:
            profiles = profiles.exclude(user_tag=self.instance.user_tag)
            slugs = slugs.exclude(user_tag=self.instance.user_tag)
        if profiles.exists():
            raise serializers.ValidationError('Тег такой есть уже существует.')
        if slugs.exists():
            raise serializers.ValidationError('Тег такой есть уже существует.')
        return value

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

