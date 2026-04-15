from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, ProfileSerializer
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

class ProfileViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ProfileSerializer

    def create(self, request):
        data = request.data
        user = request.user
        serializer = self.serializer_class(data=data, user=user)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegister(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def get(self):
        return Response({'title': 'метод не разрешен'})

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




