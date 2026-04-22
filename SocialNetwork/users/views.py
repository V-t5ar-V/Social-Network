from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, ProfileSerializer, SubscriptionSerializer
from rest_framework.response import Response
from .models import Profile, Subscription
from rest_framework.generics import get_object_or_404
from django.utils.text import slugify
from rest_framework.decorators import action


# Create your views here.

class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionSerializer

    @action(methods=['get'], detail=False)
    def get_following(self, request, slug=None):
        profile_queryset = Profile.objects.all()
        profile = get_object_or_404(profile_queryset, slug=slug)
        if profile.is_private:
            if not profile.user.follower.filter(follower=request.user).exists():
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

    # def create(self, request):
    #     data = request.data
    #     user = request.user
    #     serializer = self.serializer_class(data=data, context={'request': request})
    #     if serializer.is_valid():
    #         serializer.save(user=user)
    #         return Response(
    #             serializer.data,
    #             status=status.HTTP_201_CREATED
    #         )
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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






class UserRegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def get(self, request):
        return Response({'title': f'метод не разрешен, {request.data}'})

    def post(self, request):                        # UNSTABLE
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request):
        pass




# class CheckTagAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     class_model = Profile
#
#     def post(self, request):
#         data = request.data
#         tag = data.get('tag') or data.get('slug')
#         if not tag:
#             return Response({'title': 'РџРµСЂРµРґР°Р№С‚Рµ tag РёР»Рё slug.'}, status=status.HTTP_400_BAD_REQUEST)
#         slug = slugify(tag)
#         if not slug:
#             return Response({'title': 'РќР° РўР•Р“ РґРѕР»Р¶РЅС‹ Р±С‹С‚СЊ Р±СѓРєРІС‹ РёР»Рё С†РёС„СЂС‹.'}, status=status.HTTP_400_BAD_REQUEST)
#         slug_exists = self.class_model.objects.filter(slug=slug).exists()
#         if slug_exists:
#             return Response({'is_free': False}, status=status.HTTP_200_OK)
#         return Response({'is_free': True}, status=status.HTTP_200_OK)
#
#
#
