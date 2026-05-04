from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import get_object_or_404
from django.utils.text import slugify

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1

class PostViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def list(self, request):
        queryset = Post.objects.all().order_by('-created_at')

        # page = StandardResultsSetPagination(queryset)
        # if page is not None:
        #     serializer = PostSerializer(page)
        if queryset:
            serializer = self.serializer_class(queryset, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)


    def create(self, request):
        user = request.user
        raw_tags = request.data.get('tags', '')

        if isinstance(raw_tags, str):
            tags = [tag.strip() for tag in raw_tags.split(',') if tag.strip()]
        else:
            tags = raw_tags

        data = request.data.copy()
        data.setlist('tags', tags)

        serializer = self.serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, slug=None):
        pass

    def destroy(self, request, slug=None):
        pass

class CommentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer


    def list(self, request, slug=None):
        queryset = Post.objects.all()
        post = get_object_or_404(queryset, slug=slug)
        profile = post.user.profile
        user = request.user

        if profile.is_private:
            followers = post.user.follower.all()
            if user not in followers:
                return Response('Доступ запрещен.', status=status.HTTP_403_FORBIDDEN)

        if user in profile.blocked_users.all():
            return Response('Доступ запрещен.', status=status.HTTP_403_FORBIDDEN)

        comments = post.comments.all()
        if comments:
            serializer = self.serializer_class(comments, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, slug=None):
        queryset = Post.objects.all()
        post = get_object_or_404(queryset, slug=slug)
        request.data['post'] = post.pk

        user = request.user

        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        queryset = Comment.objects.all()
        comment = get_object_or_404(queryset, pk=pk)
        if comment.user != request.user:
            return Response({'title': 'нельзя удалить чужой комментарии'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
