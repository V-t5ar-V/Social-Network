from rest_framework import viewsets, permissions, status
from .serializers import UserSerializer, ProfileSerializer, SubscriptionSerializer
from rest_framework.response import Response
from .models import Profile, Subscription
from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.decorators import action


# Create your views here.

class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_follower_requests(self, request):
        queryset = Subscription.objects.filter(following=request.user, subscription_status='PENDING').order_by('-sent_at')
        if not queryset.exists():
            return Response(data={'title':'Вы не получали запросов на подписку'}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def got_following_requests(self,request):
        queryset = Subscription.objects.filter(follower=request.user, subscription_status='PENDING').order_by('-sent_at')
        if queryset.exists():
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data={'title': 'Нет не принятых запросов на подписку'}, status=status.HTTP_204_NO_CONTENT)


    @action(methods=['get'], detail=False)
    def get_following(self, request, slug=None): #########################
        user = get_object_or_404(User.objects.all(), username=slug)
        profile = user.profile

        if user != request.user:
            if profile.is_private and request.user not in profile.user.following.all():
                return Response({'title': 'Только подписчики могу посмотреть список подписок.'},
                                status=status.HTTP_403_FORBIDDEN)
            if request.user in profile.blocked_users.all():
                return Response({'title': 'Просмотр списка подписчиков недоступен.'},
                                status=status.HTTP_403_FORBIDDEN)

        queryset = Subscription.objects.filter(follower=user, subscription_status='ACCEPTED').order_by('-created_at')

        if not queryset.exists():
            return Response({'title': 'Нет подписок.'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(methods=['get'], detail=False)
    def get_followers(self, request, slug=None):
        user = get_object_or_404(User.objects.all(), username=slug)
        profile = user.profile

        if user != request.user:
            if profile.is_private and request.user not in profile.user.following.all():
                return Response({'title': 'Только подписчики могу посмотреть список подписок.'},
                                status=status.HTTP_403_FORBIDDEN)

        queryset = Subscription.objects.filter(following=user, subscription_status='ACCEPTED').order_by('-created_at')

        if not queryset.exists():
            return Response({'title': 'Нет подписок.'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, slug=None):
        following = get_object_or_404(User, username=slug)
        serializer = self.serializer_class(data=
                                                {'following': following.pk,
                                                 'follower': request.user.pk
                                                 },
                                           context=
                                                {'request': request}
                                           )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True)
    def accept(self, request, pk=None):
        queryset = Subscription.objects.all()
        subscription = get_object_or_404(queryset, pk=pk)
        if request.user != subscription.following:
            return Response({'title': 'Принять запрос может только получатель запроса.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(subscription, data={'subscription_status': 'ACCEPTED'}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True)
    def reject(self, request, pk=None):
        queryset = Subscription.objects.all()
        subscription = get_object_or_404(queryset, pk=pk)
        if request.user != subscription.following:
            return Response({'title': 'Отклонить запрос можно только получатель запроса.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(subscription, data={'subscription_status': 'REJECTED'}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'title': 'успешно отклонено'}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        queryset = Subscription.objects.all()
        subscription = get_object_or_404(queryset, pk=pk)
        if request.user in [subscription.following, subscription.follower]:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'title': 'удалить подписку могут только following и follower'}, status=status.HTTP_403_FORBIDDEN)









class ProfileViewSet(viewsets.ViewSet):
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer


    def retrieve(self, request, slug=None):
        user_queryset = User.objects.all()
        user = get_object_or_404(user_queryset, username=slug)
        if request.user != user:
            if user.profile.is_private and request.user not in user.followers.all():
                return Response({'title': 'Профиль приватный.'}, status=status.HTTP_403_FORBIDDEN) ##################
        if request.user in user.profile.blocked_users.all():
            return Response({'title':'Профиль недоступен'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(user.profile, context={'request': request})
        data = dict(serializer.data)
        return Response(data=data, status=status.HTTP_200_OK)

    def partial_update(self, request):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, user=request.user)
        serializer = self.serializer_class(
            profile,
            data=request.data,
            context={'request': request},

            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request):
        user = request.user
        user.delete()
        return Response({"title": "Учетная запись удалена."}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['patch'], detail=True)
    def block_user(self, request, slug=None):
        blocked_user = get_object_or_404(User, username=slug)
        profile = Profile.objects.get(user=request.user)
        if blocked_user == request.user:
            return Response(
                {"target_user": "Нельзя заблокировать самого себя."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(
            profile,
            data={'target_user': blocked_user.pk,
                  'action': 'block'
                  },
            context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        following_queryset = Subscription.objects.filter(following=blocked_user, follower=request.user)
        follower_queryset = Subscription.objects.filter(following=request.user, follower=blocked_user)
        if follower_queryset.exists():
            follower_queryset.first().delete()
        if following_queryset.exists():
            following_queryset.first().delete()

        return Response({"title": "Пользователь заблокирован."}, status=status.HTTP_200_OK)


    @action(methods=['patch'], detail=True)
    def unblock_user(self, request, slug=None):
        unblocked_user = get_object_or_404(User, username=slug)
        profile = Profile.objects.get(user=request.user)

        serializer = self.serializer_class(
            profile,

            data={'target_user': unblocked_user.pk,
                  'action': 'unblock'
                  },
            context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"title": "Пользователь разблокирован."}, status=status.HTTP_200_OK)


class PostAllowAny(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return request.user and request.user.is_authenticated


class UserViewSet(viewsets.ViewSet):
    lookup_field = 'username'
    permission_classes = [PostAllowAny]

    def create(self, request):
        serializer = UserSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
