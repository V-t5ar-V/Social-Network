from rest_framework.decorators import action
from django.contrib.admin.templatetags.admin_list import pagination
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, LikeSerializer


class PostViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination
    def list(self, request):
        queryset = Post.objects.all().order_by('-created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is not None:
            serializer = PostSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


    def create(self, request):
        user = request.user

        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, slug=None):
        post = get_object_or_404(Post, slug=slug)
        user = request.user
        if post.user != request.user:
            post_profile = post.user.profile
            if request.user in post_profile.blocked_users.all():
                return Response({'title': 'Просмотр недоступен'}, status=status.HTTP_403_FORBIDDEN)
            elif post_profile.is_private:
                if not post.user.followers.filter(follower=user, subscription_status='ACCEPTED').exists():
                    return Response({'title': 'Профиль приватный'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug=None):
        pass

    @action(methods=['list'], detail=True)
    def comments(self, request, slug=None):
        post = get_object_or_404(Post, slug=slug)
        profile = post.user.profile
        user = request.user
        if user != post.user:
            if profile.is_private:
                if not post.user.followers.filter(follower=user, subscription_status='ACCEPTED').exists():
                    return Response({'title':'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)

        if user in profile.blocked_users.all():
            return Response({'title':'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)

        comments = post.comments.all()
        if comments:
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True)
    def to_comment(self, request, slug=None):
        post = get_object_or_404(Post, slug=slug)
        post_user = post.user
        request.data['post'] = post.pk

        user = request.user
        if post_user != user:

            if user in post_user.profile.blocked_users.all():
                return Response({'title': 'Вы не можете прокомментировать пост.'}, status=status.HTTP_403_FORBIDDEN)

            if post_user.profile.is_private:
                if not post.user.followers.filter(follower=user, subscription_status='ACCEPTED').exists():
                    return Response({'title': 'Только подписчики могут комментировать'}, status=status.HTTP_403_FORBIDDEN)


        serializer = CommentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(methods=['create'], detail=True)
    def like(self, request, slug=None):
        post = get_object_or_404(Post, slug=slug)
        user = request.user
        profile = post.user.profile
        if user != post.user:
            if profile.is_private:
                if not post.user.followers.filter(follower=user, subscription_status='ACCEPTED').exists():
                    return Response({'title': 'Нельзя поставить лайк.'}, status=status.HTTP_403_FORBIDDEN)
        if user in profile.blocked_users.all():
            return Response({'title': 'Нельзя поставить лайк.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = LikeSerializer(data={
            'post': post.pk,
        },
            context={'request': request}
        )


        serializer.is_valid(raise_exception=True)

        serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['destroy'], detail=True)
    def del_like(self, request, slug=None):
        post = get_object_or_404(Post, slug=slug)
        like = post.likes.all().filter(user=request.user)
        if like.exists():
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'title': 'Вы не ставили лайка посту'}, status=status.HTTP_404_NOT_FOUND)

    def profile_posts_list(self, request, slug=None):
        user = request.user
        profile = get_object_or_404(User, username=slug).profile
        if user != profile.user:
            if user in profile.blocked_users.all():
                return Response({'title': 'Просмотр профиля недоступен.'}, status=status.HTTP_403_FORBIDDEN)
            if profile.is_private and not profile.user.followers.filter(follower=user, subscription_status='ACCEPTED').exists():
                return Response({'title': 'Посты доступны только подписчикам.'}, status=status.HTTP_403_FORBIDDEN)

        posts = profile.user.posts
        serializer = PostSerializer(posts, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def destroy(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.user != request.user:
            return Response({'title': 'нельзя удалить чужой комментарии'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LikeSerializer