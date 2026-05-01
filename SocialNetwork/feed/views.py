from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .serializers import PostSerializer


class PostViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def list(self, request):
        pass

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

    def partial_update(self, request, slug=None):
        pass

    def destroy(self, request, slug=None):
        pass
