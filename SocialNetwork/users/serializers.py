from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Profile, Subscription
from django.utils import timezone

class SubscriptionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    follower = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    subscription_status = serializers.ChoiceField(choices=['PENDING', 'ACCEPTED', 'REJECTED'], required=False)
    created_at = serializers.HiddenField(default=timezone.now())
    sent_at = serializers.HiddenField(default=timezone.now())
    class Meta:
        model = Subscription
        fields = ('id', 'following', 'follower', 'subscription_status', 'created_at', 'sent_at')

    def to_representation(self, instance):
        data = {
            'id': instance.pk,
            'following': instance.following.username,
            'follower': instance.follower.username,
            'subscription_status': instance.subscription_status,
        }

        return data

    def validate(self, attrs):
        if attrs["following"] == attrs["follower"]:
            raise serializers.ValidationError({"title":"Нельзя подписаться на самого себя"})
        return attrs
    def validate_subscription(self, instance, following, follower, created):

        if not created:
            if instance.subscription_status == 'PENDING':
                raise serializers.ValidationError({"title" : "Подписка уже в ожидании."})

            elif instance.subscription_status == 'ACCEPTED':
                raise serializers.ValidationError({"title": "Подписка уже принята."})


    def create(self, validated_data):
        follower = validated_data['follower']
        following = validated_data['following']

        subscription, created = Subscription.objects.get_or_create(following=following, follower=follower)

        self.validate_subscription(instance=subscription, created=created, following=following, follower=follower)

        subscription_status = "PENDING" if following.profile.is_private else "ACCEPTED"

        subscription.subscription_status = subscription_status
        if not created:
            subscription.sent_at = timezone.now()

        subscription.save()

        return subscription





    def update(self, instance, validated_data):
        if 'subscription_status' not in validated_data:
            raise serializers.ValidationError('Доступно только изменение статуса подписки.')
        if  validated_data['subscription_status'] == 'PENDING':
            raise serializers.ValidationError('Нельзя назначить такой статус подписки.')
        if instance.subscription_status != 'PENDING':
            raise serializers.ValidationError('Нельзя изменить статус подписки.')
        instance.subscription_status = validated_data['subscription_status']
        instance.save()
        return instance






class ProfileSerializer(serializers.Serializer):                                            #UNSTABLE
    id = serializers.IntegerField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault(), required=False)
    is_private = serializers.BooleanField(default=False, allow_null=True)
    blocked_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    target_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, write_only=True)
    action = serializers.ChoiceField(choices=['block', 'unblock'], required=False, write_only=True)
    bio = serializers.CharField(max_length=750, required=False, allow_blank=True)
    profile_pic = serializers.FileField(required=False, allow_null=True)
    is_online = serializers.BooleanField(default=False)
    slug = serializers.SlugField(max_length=30, required=False)
    name = serializers.CharField(max_length=30, required=False)

    class Meta:
        model = Profile
        fields = ('id', 'user','is_private', 'blocked_users', 'bio', 'profile_pic', 'is_online', 'slug', 'name')


    def to_representation(self, instance):
        request = self.context.get('request')
        blocked_users = []
        for blocked_user in instance.blocked_users.all():
            blocked_users.append(blocked_user.username)

        pfp = instance.profile_pic.url if instance.profile_pic else None
        pfp_ulr = request.build_absolute_uri(pfp) if pfp else None
        data = {
            'username': instance.slug,
            'is_private': instance.is_private,
            'bio': instance.bio,
            'profile_pic': pfp_ulr,
            'name': instance.name,
        }
        if request.user == instance.user:
            data['blocked_users'] = blocked_users if request.user == instance.user else None
        return data

    def validate_profile_pic(self, pic):
        pfp_max_size = 5 * 1024 * 1024
        allowed_types = ['image/png', 'image/jpeg']


        if pic.content_type not in allowed_types:
            raise serializers.ValidationError('Недопустимый тип меди, разрешены только png и jpg.')

        if pic.size > pfp_max_size:
            raise serializers.ValidationError('Слишком большое изображение (> 5 Мб).')

        pass

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

    def update_blacklist(self, instance, target, act):
        if target == instance.user:
            raise serializers.ValidationError({'target_user': 'Нельзя заблокировать самого себя.'})
        if act == 'block' and target:
            if target in instance.blocked_users.all():
                raise serializers.ValidationError({'target_user': 'Пользователь уже заблокирован.'})
            instance.blocked_users.add(target)
        elif act == 'unblock' and target:
            if target not in instance.blocked_users.all():
                raise serializers.ValidationError({'target_user': 'Пользователь вне списка заблокированных'})
            instance.blocked_users.remove(target)

    def update(self, instance, validated_data):
        validated_data.pop('is_online', None)
        validated_data.pop('blocked_users', None)
        target = validated_data.pop('target_user', None)
        act = validated_data.pop('action', None)


        for field, value in validated_data.items():
            setattr(instance, field, value)


        instance.save()
        if target and act:
            self.update_blacklist(instance=instance,
                                  target=target,
                                  act=act)

        return instance


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, max_length=20)
    profile = ProfileSerializer(required=False)
    email = serializers.EmailField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'profile')

    def validate_values(self, validated_data):
        email = validated_data.get('email', None)
        username = validated_data.get('username', None)
        if email:
            email_exists = User.objects.filter(email=email).exists()
            if email_exists:
                raise serializers.ValidationError({'email': 'Пользователь с такой почтой уже существует.'})


    def create(self, validated_data):                                                           # UNSTABLE
        profile_data = validated_data.pop('profile', None)
        if profile_data is None:
            profile_data = {'name': 'NoNameUser'}
        self.validate_values(validated_data)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        Profile.objects.create(user=user, name=profile_data['name'])
        return user

    def update(self, instance, validated_data):
        self.validate_values(validated_data)
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', None)
        if username:
            instance.username = username
            instance.profile.slug = username
            instance.profile.save()
        if email:
            instance.email = email
        instance.save()
        return instance



