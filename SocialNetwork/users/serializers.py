from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Subscription

class ProfileSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_private = serializers.BooleanField(default=False, allow_null=True)
    blocked_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    user_tag = serializers.CharField(max_length=20)
    bio = serializers.CharField(max_length=750, required=False, allow_null=True, allow_blank=True)
    profile_pic = serializers.FileField(required=False, allow_null=True)
    is_online = serializers.BooleanField(default=False, read_only=True)
    slug = serializers.SlugField(allow_null=True, read_only=True)

    class Meta:
        model = Profile
        fields = ('user','is_private', 'blocked_users', 'user_tag', 'bio', 'profile_pic', 'is_online', 'slug')


    def create(self, validated_data):
        profile = Profile.objects.create(
            user=validated_data['user'],
            user_tag=validated_data['user_tag'],
        )
        return profile



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

