from .views import ChatViewSet, ChatMemberViewSet, StickerViewSet
from django.urls import path

urlpatterns = [
    path('chats/', ChatViewSet.as_view({
        'get': 'list'
    }), name='chat_list'),
    path('chats/<int:pk>', ChatViewSet.as_view({
        'get': 'retrieve',
        'put': 'partial_update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='chat_detail'),
    path('chats/<int:pk>/members', ChatViewSet.as_view({
        'get': 'list'
    }), name='chat_members_list'),
    path('members/', ChatMemberViewSet.as_view({
        'post': 'create'
    }), name='delete_member'),
    path('members/<int:pk>', ChatMemberViewSet.as_view({
        'delete': 'destroy',
        'patch': 'partial_update'
    })),
    path('chats/<int:pk>/messages/', ChatViewSet.as_view({
        'get': 'list',
    }), name='message_list'),
    path('/sticker_catalog/', StickerViewSet.as_view({
        'get': 'list',
    }), name='sticker_list'),
    path('/sticker_catalog/search/<slug:slug>/', StickerViewSet.as_view({
        'get': 'search_by_keyword',
    }), name='sticker_list'),
    path('/stickers_catalog/detail/<int:pk>', StickerViewSet.as_view({
        'get': 'detail',
        'delete': 'destroy',
    }), name='sticker_detail'),
    # path('messages/<int:pk>', MessageViewSet.as_view({
    #     'delete': 'destroy',
    #     'patch': 'partial_update'
    # }), name='edit/delete message'),
]