from .views import UserRegister, ProfileViewSet

from django.urls import path



urlpatterns = [
    path('register/', UserRegister.as_view(), name='register'),
    path('profiles/', ProfileViewSet.as_view({'post':'create'}),name='create_profile'),
    # path('profiles/<slug:slug>/',noview(),name='profile'),
    # path('profiles?<slug:slug>/qr_code', noview(),name='QR_code'),
    # path('profiles/<slug:slug>/blacklist', noview(), name='blocked_users'),
    # path('profiles/<slug:slug>/blacklist/<slug:slug>', noview(), name='remove_blacklisted_user'),
    # path('profiles/<slug:slug>/subscriptions/', noview(), name='subscriptions'),
    # path('profiles/<slug:slug>/subscription_requests', noview(), name='subscription_requests_list'),
    # path('profiles/<slug:slug>/subscription_requests/<int:pk>', noview(), name='subscription_requests_list'),
    # path('profiles/<slug:slug>/subscribers/', noview(), name='subscribers_list'),
    # path('profiles/<slug:slug>/subscribers/<int:pk>', noview(), name='subscribers_list'),
    # path('profiles/<slug:slug>/posts/', noview(), name='posts_list'),
]
