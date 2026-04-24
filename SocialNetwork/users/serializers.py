from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import Profile, Subscription

class SubscriptionSerializer(serializers.Serializer):
    following = serializers.CharField(max_length=30)
    follower = serializers.CharField(read_only=True)
    is_accepted = serializers.BooleanField(default=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('id, following', 'follower', 'is_accepted', 'created_at')

    def create(self, validated_data):
        me = validated_data['user'].profile
        print(me)
        following_profile = Profile.objects.filter(slug=validated_data['following']).select_related('user').first()
        if following_profile is None:
            raise serializers.ValidationError({'following': 'Профиль не найден.'})

        if following_profile == me:
            raise serializers.ValidationError({'following': 'Нельзя подписаться на самого себя.'})

        if me.blocked_users.filter(pk=following_profile.user_id).exists() or following_profile.blocked_users.filter(
                pk=me.user_id).exists():
            raise serializers.ValidationError({'following': 'Подписка недоступна.'})

        matching_subscription = Subscription.objects.filter(
            following=following_profile.user,
            follower=validated_data['user'],
        )
        if matching_subscription.exists():
            raise serializers.ValidationError({'following': 'Подписка уже существует.'})

        subscription = Subscription.objects.create(
            following=following_profile.user,
            follower=validated_data['user'],
            is_accepted=not following_profile.is_private,
        )
        return subscription


    def update(self, instance, validated_data):
        if 'is_accepted' in validated_data:
            if validated_data['is_accepted']:
                instance.following = validated_data.get('is_accepted', instance.is_accepted)
                return instance
            instance.is_accepted = False
            instance.delete()
            return instance
        return serializers.ValidationError('можно только принимать или отклонить запрос')





class ProfileSerializer(serializers.Serializer):                                            #UNSTABLE
    user = serializers.HiddenField(default=serializers.CurrentUserDefault(), required=False)
    is_private = serializers.BooleanField(default=False, allow_null=True)
    blocked_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False,write_only=True)
    unblocked_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    bio = serializers.CharField(max_length=750, required=False, allow_blank=True)
    profile_pic = serializers.FileField(required=False, allow_null=True)
    is_online = serializers.BooleanField(default=False)
    slug = serializers.SlugField(max_length=30, required=False)
    name = serializers.CharField(max_length=30, required=False)

    class Meta:
        model = Profile
        fields = ('user','is_private', 'blocked_users', 'bio', 'profile_pic', 'is_online', 'slug', 'name')


    def create(self, validated_data):
        blocked_users = validated_data.pop('blocked_users', [])
        profile = Profile.objects.create(
            user=validated_data['user'],
            slug=validated_data['user'].username,
            is_private=validated_data.get('is_private', False),
            bio=validated_data.get('bio'),
            profile_pic=validated_data.get('profile_pic'),
        )
        if blocked_users:
            profile.blocked_users.set(blocked_users)
        return profile

    # def validate_slug(self, value):
    #     slug = slugify(value)
    #     if not slug:
    #         raise serializers.ValidationError('На ТЕГ должны быть буквы или цифры.')
    #     slugs = Profile.objects.filter(slug=slug)
    #     if self.instance is not None:
    #         slugs = slugs.exclude(slug=self.instance.slug)
    #     if slugs.exists():
    #         raise serializers.ValidationError('Тег такой есть уже существует.')
    #     return slug

    def update(self, instance, validated_data):
        validated_data.pop('user', None)
        validated_data.pop('is_online', None)
        username = validated_data.pop('username', None)
        blocked_users = validated_data.pop('blocked_users', None)
        unblocked_users = validated_data.pop('unblocked_users', None)
        if username:
            instance.user.username = username
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        if blocked_users is not None:
            instance.blocked_users.add(*blocked_users)

        if unblocked_users is not None:
            instance.blocked_users.remove(*unblocked_users)

        return instance


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile = ProfileSerializer(required=False)
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'profile')

    def create(self, validated_data):                                                           # UNSTABLE
        profile_data = validated_data.pop('profile')
        # profile = ProfileSerializer(data=profile_data, context=self.context)
        # profile.is_valid(raise_exception=True)
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        Profile.objects.create(user=user, name=profile_data['name'])
        return user

    def update(self, instance, validated_data):
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', None)
        if username:
            instance.username = username
        if email:
            instance.email = email
        instance.save()
        return instance



