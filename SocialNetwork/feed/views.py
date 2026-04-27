from rest_framework import viewsets, permissions, status
from .serializers import PostSerializer
from rest_framework.response import Response
from .models import Post, Media, Tag, Comment, Like, PostView
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import action

# Create your views here.

class PostViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def list(self, request):
        pass

    def create(self, request):
        data = request.data
        user = request.user

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass
