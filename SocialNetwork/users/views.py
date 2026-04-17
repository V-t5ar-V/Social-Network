from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, ProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Profile
from rest_framework.generics import get_object_or_404


# Create your views here.

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

    def retrieve(self, slug=None):
        queryset = Profile.objects.all()
        profile = get_object_or_404(queryset, slug=slug)
        serializer = self.serializer_class(profile)
        return Response(serializer.data)




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
            return Response({'is_free': False})
        return Response({'is_free': True})



