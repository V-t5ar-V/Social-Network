from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, ProfileSerializer, SubscriptionSerializer
from rest_framework.response import Response
from .models import Profile, Subscription
from rest_framework.generics import get_object_or_404


# Create your views here.

class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def create(self, request):
        data = request.data
        user = request.user
        serializer = self.serializer_class(data=data, context={'request': request})
        if request.data.get("following") == request.user.id:
            return Response({'title': 'нельзя подписаться на самого себя'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        slug = request.query_params.get('slug')
        profile = get_object_or_404(Profile, slug=slug)
        user = profile.user
        queryset = Subscription.objects.filter(following=user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        queryset = Subscription.objects.all()
        data = request.data
        subscription = get_object_or_404(queryset, pk=pk)

        if subscription.following != request.user:
            return Response(
                {'title': 'статус подписки пожет изменить только получатель'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.serializer_class(
            subscription,
            data=data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            if not serializer.validated_data.get('is_accepted'):
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def create(self, request):
        data = request.data
        user = request.user
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, slug=None):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, slug=slug)

        serializer = self.serializer_class(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, slug=None):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, slug=slug)
        if profile.user != request.user:
            return Response({'title': 'Нельзя редактировать чужой профиль'}, status=status.HTTP_403_FORBIDDEN)
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






class UserRegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def get(self, request):
        return Response({'title': f'метод не разрешен, {request.data}'})

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CheckTagAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    class_model = Profile

    def post(self, request):
        data = request.data
        tag_exists = self.class_model.objects.filter(user_tag=data['tag']).exists()
        if tag_exists:
            return Response({'is_free': False}, status=status.HTTP_200_OK)
        return Response({'is_free': True}, status=status.HTTP_200_OK)



