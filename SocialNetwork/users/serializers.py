from django.db.models.expressions import result
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import Profile, Subscription

class SubscriptionSerializer(serializers.Serializer):
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    is_accepted = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('following', 'follower', 'is_accepted', 'created_at')

    def create(self, validated_data):
        following = validated_data.get('following')
        queryset = Subscription.objects.filter(following=following, follower=validated_data['user']) ######################
        if queryset.exists():
            serializers.ValidationError('нельзя подписаться одного пользователя дважды')
        subscription_result = False
        if validated_data['following'].profile.is_private:
            subscription_result = False
        subscription = Subscription.objects.create(
            following=validated_data['following'],
            follower=validated_data['user'],
            is_accepted=subscription_result,
        )
        return subscription

    def update(self, instance, validated_data, pk):
        if 'is_accepted' in validated_data:
            if validated_data['is_accepted']:
                instance.following = validated_data.get('is_accepted', instance.is_accepted)
                return instance
            instance.is_accepted = False
            instance.delete()
            return instance
        return serializers.ValidationError('можно только принимать либо отклонять запрос')





class ProfileSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_private = serializers.BooleanField(default=False, allow_null=True)
    blocked_users = serializers.PrimaryKeyRelatedField(many=True, queryset=Profile.objects.all(), required=False)
    bio = serializers.CharField(max_length=750, required=False, allow_null=True, allow_blank=True)
    profile_pic = serializers.FileField(required=False, allow_null=True)
    is_online = serializers.BooleanField(default=False)
    slug = serializers.SlugField(max_length=30)

    class Meta:
        model = Profile
        fields = ('user','is_private', 'blocked_users', 'bio', 'profile_pic', 'is_online', 'slug')


    def create(self, validated_data):
        profile = Profile.objects.create(
            user=validated_data['user'],
            slug=validated_data['slug'],
            is_private=validated_data.get('is_private', False),
            bio=validated_data.get('bio'),
            profile_pic=validated_data.get('profile_pic'),
        )
        return profile

    def validate_user_slug(self, value): ################################
        slug = slugify(value)
        if not slug:
            raise serializers.ValidationError('На ТЕГ должны быть буквы или цифры.')
        slugs = Profile.objects.filter(slug=slug)
        if slugs.exists():
            raise serializers.ValidationError('Тег такой есть уже существует.')
        return value

    def update(self, instance, validated_data): ####################
        validated_data.pop('user', None)
        validated_data.pop('is_online', None)

        if "slug" in validated_data:
            if self.validate_user_slug(validated_data['slug']):
                instance.slug = validated_data.get('slug', instance.slug)

            validated_data.pop('slug')
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return True


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

