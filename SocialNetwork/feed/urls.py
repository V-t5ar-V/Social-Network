from django.urls import path
from .views import PostViewSet, CommentViewSet, LikeViewSet

urlpatterns = [
    path('posts/',PostViewSet.as_view({
        'post': 'create',
        'get': 'list',
    }), name='posts'),
#     path('posts/<slug:slug>', noview, name='posts_detail'),
    path('posts/<slug:slug>/comments/', CommentViewSet.as_view({
        'post': 'create',
        'get': 'list',
    }), name='comments_list'),
    path('comments/<int:pk>/', CommentViewSet.as_view({
        "delete": "destroy",
    }), name='comments'),
    path('posts/<slug:slug>/like/', LikeViewSet.as_view({
        'post': 'create',
    })),
    path('posts/<slug:slug>/delete_like/', LikeViewSet.as_view({
        'delete': 'destroy',
    }))
#     path('posts/<slug:slug>/likes/', noview, name='likes'),
#     path('likes/<int:pk>', noview, name='delete_like'),
#     path('posts/<slug:slug>/views/', noview, name='number_of_views'),
#     path('profiles/<slug:slug>/posts/', noview(), name='posts_list'),
]