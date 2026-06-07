from django.urls import path
from .views import PostViewSet, CommentViewSet, LikeViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [

    path('posts/',PostViewSet.as_view({ # + +
        'post': 'create',
        'get': 'list',
    }), name='posts'),
    path('posts/<slug:slug>/', PostViewSet.as_view({ # +
        'delete': 'destroy',
        'get': 'retrieve',
    }), name='posts_detail'),


    path('posts/<slug:slug>/like/', PostViewSet.as_view({
        'post': 'like',
    })),
    path('posts/<slug:slug>/delete_like/', PostViewSet.as_view({
        'delete': 'del_like',
    })),


    path('posts/<slug:slug>/comments/', PostViewSet.as_view({
        'post': 'to_comment',
        'get': 'comments',
    }), name='comments_list'),


    path('comments/<int:pk>/', CommentViewSet.as_view({
        "delete": "destroy",
    }), name='comments'),
#     path('posts/<slug:slug>/views/', noview, name='number_of_views'),
    path('profiles/<slug:slug>/posts/', PostViewSet.as_view({
        'get': 'profile_posts_list'
    }), name='posts_list'),
]