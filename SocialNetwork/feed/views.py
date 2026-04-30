from rest_framework import viewsets, permissions, status
from .serializers import PostSerializer
from rest_framework.response import Response
from .models import Post, Media, Tag, Comment, Like, Post_View
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
        user = request.user

        tags = request.data['tags']
        tags = tags.split(',')
        data = dict(request.data)
        data['tags'] = tags
        data['title'] = data['title'][0]
        data['description'] = data['description'][0]
        print(data)



        serializer = self.serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, slug=None):
        pass

    def partial_update(self, request, slug=None):
        pass

    def destroy(self, request, slug=None):
        pass
