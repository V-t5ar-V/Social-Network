from .views import UserRegisterAPIView, ProfileViewSet, CheckTagAPIView, SubscriptionViewSet

from django.urls import path



urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='register'),
    path('check-tag/', CheckTagAPIView.as_view(), name='check_tag'),
    path('profiles/', ProfileViewSet.as_view({'post':'create'}),name='create_profile'),
    path('profiles/detail/<slug:slug>/',ProfileViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }) ,name='profile'),
    path('profiles/detail/<slug:slug>/following/', SubscriptionViewSet.as_view({
        'get': 'following',
    }), name='following'),
    path('profiles/detail/<slug:slug>/followers/', SubscriptionViewSet.as_view({
        'get': 'follower',
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





    # path('profiles/<slug:slug>/qr_code', noview(),name='QR_code'),
    # path('profiles/<slug:slug>/blacklist', noview(), name='blocked_users'),
    # path('profiles/<slug:slug>/blacklist/<slug:slug>', noview(), name='remove_blacklisted_user'),
    # path('profiles/<slug:slug>/posts/', noview(), name='posts_list'),
]
