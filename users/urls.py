from .views import UserViewSet, ProfileViewSet, SubscriptionViewSet

from django.urls import path

urlpatterns = [
    path('register/', UserViewSet.as_view({
        'post': 'create',
    }), name='register'),
    path('edit-user/', UserViewSet.as_view({
        'patch': 'partial_update',
    })),


    path('profiles/edit-profile/', ProfileViewSet.as_view({
        'patch': 'partial_update',
    })),
    path('profiles/detail/<slug:slug>/',ProfileViewSet.as_view({
        'get': 'retrieve',
    }) ,name='profile'),
    path('profiles/delete-me/', ProfileViewSet.as_view({
        'delete': 'destroy',
    })),

    path('profiles/detail/<slug:slug>/following/', SubscriptionViewSet.as_view({
        'get': 'get_following',
    }), name='following'),
    path('profiles/detail/<slug:slug>/followers/', SubscriptionViewSet.as_view({
        'get': 'get_followers',
    }), name='followers'),


    path('profiles/requests/following/', SubscriptionViewSet.as_view({
        'get': 'got_following_requests',
    })),
    path('profiles/requests/followers/', SubscriptionViewSet.as_view({
        'get': 'get_follower_requests',
    })),

    path('subscriptions/<slug:slug>/follow/', ProfileViewSet.as_view({
        'post': 'follow',
    }), name='create_subscription'),

    path('subscriptions/<slug:slug>/accept/', ProfileViewSet.as_view({
        'patch': 'accept_subscription'
    }), name='accept_subscription'),
    path('subscriptions/<slug:slug>/reject/', ProfileViewSet.as_view({
        'patch': 'reject_subscription'
    }), name='reject_subscription'),

    path('subscriptions/<slug:slug>/unfollow/', ProfileViewSet.as_view({
        'delete': 'unfollow'
    }), name='delete_subscription'),


    path('profiles/<slug:slug>/block/', ProfileViewSet.as_view({
        'patch': 'block_user',
    }), name='block_user'),
    path('profiles/<slug:slug>/unblock/', ProfileViewSet.as_view({
        'patch': 'unblock_user',
    }), name='unblock_user'),


    # path('profiles/<slug:slug>/qr_code', noview(),name='QR_code'),
]
