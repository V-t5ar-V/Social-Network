from django.contrib.messages.storage.cookie import MessageSerializer
from django.core.paginator import Paginator
from rest_framework import viewsets, status, permissions, pagination

from .serializers import *
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action

User = get_user_model()
# Create your views here.

class MessagePagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_size = 30

class ChatViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination

    def list(self, request):
        queryset = Chat.objects.filter(members__user=request.user)

        if queryset.exists():
            serializer = ChatSerializer(queryset, many=True, context={'request': request, 'view': self})

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'title': 'Нет чатов'}, status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk)

        if not chat.members.filter(member=request.user).exists():
            return Response({'title': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChatSerializer(chat, context={'request': request, 'view': self})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = ChatSerializer(data=request.data, context={'request': request, 'view': self})

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk)
        if not chat.members.filter(member=request.user, is_admin=True).exists():
            return Response({'title': 'Редактирование чата запрещено.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChatSerializer(chat, data=request.data, partial=True, context={'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk)
        if not chat.members.filter(member=request.user, is_admin=True).exists():
            return Response({'title': 'Удаление чата запрещено.'}, status=status.HTTP_403_FORBIDDEN)

        chat.delete()
        return Response({'title': 'Чат удален.'}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=True)
    def members(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk)
        members = chat.members.all().order_by('-is_admin')
        if not members.filter(member=request.user).exists():
            return Response({'title': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChatMemberSerializer(members, many=True, context={'request': request, 'view': self})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def messages(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk)
        if not chat.members.filter(member=request.user, is_admin=True).exists():
            return Response({'title': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        messages = chat.messages.all()
        stickers = chat.stickers.all()

        chat_content = messages.union(stickers).order_by('-sent_at')



        paginator = self.pagination_class()
        page = paginator.paginate_queryset(chat_content, request, view=self)

        if page is not None:
            serializer = ChatMemberSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        return Response({'title': 'В чате нет сообщении.'}, status=status.HTTP_204_NO_CONTENT)




class ChatMemberViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def create(self, request):
        chat = get_object_or_404(Chat, pk=request.data['chat'])
        member = get_object_or_404(User, username=request.data['member'])
        print(chat, member)

        if not chat.members.filter(member=request.user, is_admin=True).exists():
            return Response({'title': 'У вас недостаточно прав на добавление участников'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChatMemberSerializer(data={'chat': chat.pk, 'member': member.pk}, context={'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        member_obj = get_object_or_404(ChatMember, pk=pk)
        chat = member_obj.chat
        if member_obj.member != request.user:
            if chat.members.filter(member=request.user, is_admin=True).exists():
                if member_obj.is_admin:
                    return Response({'Нельзя удалить админов чата.'})
                member_obj.delete()
                if not chat.members.filter(is_admin=True).exists():
                    chat.delete()
                return Response({'title': 'Участник удален.'})
            return Response({'title': 'У вас недосточно прав на удаление участников'}, status=status.HTTP_403_FORBIDDEN)
        member_obj.delete()
        return Response({'title': 'Вы покинули чат.'}, status=status.HTTP_200_OK)

    def partial_update(self, request, pk):
        member = get_object_or_404(ChatMember, pk=pk)
        if not member.chat.members.filter(member=request.user, is_admin=True).exists():
            return Response({'title': 'У вас недостаточно прав на обновление участников чата'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChatMemberSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class StickerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = StickerSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        stickers = Sticker.objects.all().order_by('-created_at')
        serializer = StickerSerializer(stickers, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['list'], detail=True)
    def search_by_keyword(self, request, slug=None):
        stickers = Sticker.objects.filter(keywords__keyword=slug).order_by('-created_at')
        if stickers.exists():
            serializer = StickerSerializer(stickers, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'title':'По запросу ничего не найдено'}, status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk):
        sticker = get_object_or_404(Sticker, pk=pk)
        serializer = StickerSerializer(sticker, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        sticker = get_object_or_404(Sticker, pk=pk)
        if sticker.author.user != request.user:
            return Response({'title': 'Удалить обьект может только автор.'}, status=status.HTTP_403_FORBIDDEN)
        sticker.delete()
        return Response({'title': 'Стикер удален.'}, status=status.HTTP_204_NO_CONTENT)

