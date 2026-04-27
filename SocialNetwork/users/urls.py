from .views import UserViewSet, ProfileViewSet, SubscriptionViewSet

from django.urls import path



urlpatterns = [
    path('register/', UserViewSet.as_view({
        'post': 'create',
    }), name='register'),
    path('edit_user/', UserViewSet.as_view({
        'patch': 'partial_update',
    })),
    path('check-username/<slug:slug>', UserViewSet.as_view({
        'get': 'check_username',
    }), name='check_username'),
    path('profiles/edit_my_profile/', ProfileViewSet.as_view({
        'patch': 'partial_update',
    })),
    path('profiles/detail/<slug:slug>/',ProfileViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy',
    }) ,name='profile'),
    path('profiles/detail/<slug:slug>/following/', SubscriptionViewSet.as_view({
        'get': 'get_following',
    }), name='following'),
    path('profiles/detail/<slug:slug>/followers/', SubscriptionViewSet.as_view({
        'get': 'get_followers',
    }), name='followers'),
    path('subscriptions/', SubscriptionViewSet.as_view({
        'post': 'create',
    }), name='create_subscription'),
    path('subscriptions/<int:pk>/accept/', SubscriptionViewSet.as_view({
        'patch': 'accept'
    }), name='accept_subscription'),
    path('subscriptions/<int:pk>/reject/', SubscriptionViewSet.as_view({
        'patch': 'reject'
    }), name='reject_subscription'),
    path('subscriptions/<int:pk>/', SubscriptionViewSet.as_view({
        'delete': 'destroy'
    }), name='delete_subscription'),


    path('blacklist/add/<slug:slug>/', ProfileViewSet.as_view({
        'patch': 'block_user',
    }), name='block_user'),
    path('blacklist/remove/<slug:slug>/', ProfileViewSet.as_view({
        'patch': 'unblock_user',
    }), name='unblock_user'),


    # path('profiles/<slug:slug>/qr_code', noview(),name='QR_code'),
    # path('profiles/<slug:slug>/posts/', noview(), name='posts_list'),
]
