from .views import UserRegisterAPIView, ProfileViewSet, CheckTagAPIView, SubscriptionViewSet

from django.urls import path



urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='register'),
    path('check-tag/', CheckTagAPIView.as_view(), name='check_tag'),
    path('profiles/', ProfileViewSet.as_view({'post':'create'}),name='create_profile'),
    path('profiles/detail/<slug:slug>/',ProfileViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        # 'patch': 'partial_update',
        # 'delete': 'destroy'
    }) ,name='profile'),
    path('subscriptions/', SubscriptionViewSet.as_view({
        'post': 'create',
    }), name='subscriptions'),
    path('subscriptions/<slug:slug>/', SubscriptionViewSet.as_view({
        'get':'list',
        'patch':'partial_update',
        'delete': 'destroy'
    }), name='subscriptions_edit'),
    # path('profiles/<slug:slug>/qr_code', noview(),name='QR_code'),
    # path('profiles/<slug:slug>/blacklist', noview(), name='blocked_users'),
    # path('profiles/<slug:slug>/blacklist/<slug:slug>', noview(), name='remove_blacklisted_user'),
    # path('profiles/<slug:slug>/subscription_requests', noview(), name='subscription_requests_list'),
    # path('profiles/<slug:slug>/subscription_requests/<int:pk>', noview(), name='subscription_requests_list'),
    # path('profiles/<slug:slug>/subscribers/', noview(), name='subscribers_list'),
    # path('profiles/<slug:slug>/subscribers/<int:pk>', noview(), name='subscribers_list'),
    # path('profiles/<slug:slug>/posts/', noview(), name='posts_list'),
]
