from django.db.models.expressions import result
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Subscription
import random


def generate_tag_if_exists(user_tag):
    tags = Profile.objects.values('user_tag')
    if user_tag in tags:
        while True:
            print(2)
            amount = random.randint(1, 10)
            random_numbers = random.sample(user_tag, amount)
            number = ''.join(random_numbers)
            tag_result = user_tag + number
            if not (result in user_tag):
                break
            print(1)
    else:
        tag_result = user_tag
    return tag_result

class ProfileSerializer(serializers.Serializer):
    is_online = serializers.BooleanField(default=False, read_only=True)
    is_private = serializers.BooleanField(default=False, read_only=True)
    user_tag = serializers.CharField(max_length=20)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Profile
        fields = ('user','is_private', 'blocked_users', 'user_tag', 'bio', 'profile_pic', 'is_online', 'slug')

    def create(self, validated_data):

        user_tag = generate_tag_if_exists(validated_data['user_tag'])
        profile = Profile.objects.create(
            user=validated_data['user'],
            user_tag=user_tag,
        )
        return profile

    def update(self, instance, validated_data):
        pass

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

