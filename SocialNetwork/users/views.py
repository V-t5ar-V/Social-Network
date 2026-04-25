from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from .serializers import UserSerializer, ProfileSerializer, SubscriptionSerializer
from rest_framework.response import Response
from .models import Profile, Subscription
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import action


# Create your views here.

class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionSerializer

    @action(methods=['get'], detail=False)
    def get_following(self, request, slug=None):
        queryset = Subscription.objects.all()
        profile_queryset = Profile.objects.all()
        profile = get_object_or_404(profile_queryset, slug=slug)
        if profile.is_private:
            followers = queryset.filter(follower=request.user)
            if not followers.exists():
                return Response({'title': 'только подписчики могут посмотреть список подписок'}, status=status.HTTP_403_FORBIDDEN)
        user = profile.user
        queryset = Subscription.objects.filter(follower=user)
        if not queryset.exists():
            return Response({'title': 'нед подписок'}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_followers(self, request, slug=None):
        profile_queryset = Profile.objects.all()
        profile = get_object_or_404(profile_queryset, slug=slug)
        if profile.is_private:
            if not profile.user.follower.filter(follower=request.user).exists():
                return Response({'title': 'только подписчики могут посмотреть список подписчиков'}, status=status.HTTP_403_FORBIDDEN)
        user = profile.user
        queryset = Subscription.objects.filter(following=user)
        if not queryset.exists():
            return Response({'title': 'нед подписчиков'}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data
        user = request.user
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def accept(self, request, pk=None):
        queryset = Subscription.objects.all()
        subscription = get_object_or_404(queryset, pk=pk)
        if request.user != subscription.following:
            return Response({'title': 'принять запрос можно только получатель запроса'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(subscription, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def reject(self, request, pk=None):
        queryset = Subscription.objects.all()
        subscription = get_object_or_404(queryset, pk=pk)
        if request.user != subscription.following:
            return Response({'title': 'принять запрос можно только получатель запроса'}, status=status.HTTP_403_FORBIDDEN)
        subscription.delete()
        return Response({'title': 'успешно отклонено'}, status=status.HTTP_204_NO_CONTENT)

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
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, slug=slug)

        serializer = self.serializer_class(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, user=request.user)
        serializer = self.serializer_class(
            profile,
            data=request.data,
            context={'request': request},

            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, slug=None):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, slug=slug)
        if profile.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        user = profile.user
        user.delete()
        return Response({"title": "профиль удален"}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['patch'], detail=True)
    def block_user(self, request, slug=None):
        blocked_user = get_object_or_404(User, username=slug)
        profile = Profile.objects.get(user=request.user)
        serializer = self.serializer_class(
            profile,
            data={'blocked_users': [blocked_user.id]},
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"title": "Пользователь заюлокирован."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def unblock_user(self, request, slug=None):
        unblocked_user = get_object_or_404(User, username=slug)
        profile = Profile.objects.get(user=request.user)
        serializer = self.serializer_class(
            profile,

            data={'unblocked_users': unblocked_user},
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"title": "Пользователь разблокирован."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostAllowAny(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return request.user and request.user.is_authenticated


class UserViewSet(viewsets.ViewSet):
    lookup_field = 'username'
    permission_classes = [PostAllowAny]

    def post(self, request):                        # UNSTABLE
        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CheckUsernamePIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    class_model = User

    def post(self, request):
        data = request.data
        username = data.get('username', None)
        if not username:
            return Response({'title': 'Имя пользователя обязательно.'}, status=status.HTTP_400_BAD_REQUEST)
        username_exists = self.class_model.objects.filter(username=username).exists()
        if username_exists:
            return Response({'is_free': False}, status=status.HTTP_200_OK)
        return Response({'is_free': True}, status=status.HTTP_200_OK)



