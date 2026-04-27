from django.urls import path
urlpatterns = [
    path('posts/', noview, name='posts_list'),
#     path('posts/<slug:slug>', noview, name='posts_detail'),
#     path('posts/<slug:slug>/comments/', noview, name='comments_list'),
#     path('comments/<int:pk>/', noview, name='comments'),
#     path('posts/<slug:slug>/likes/', noview, name='likes'),
#     path('likes/<int:pk>', noview, name='delete_like'),
#     path('posts/<slug:slug>/views/', noview, name='number_of_views'),
#     path('profiles/<slug:slug>/posts/', noview(), name='posts_list'),
]