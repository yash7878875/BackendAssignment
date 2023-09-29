from django.urls import path
from .views import *

urlpatterns = [
    path('post-comment/', CommentAPIView.as_view(), name='post-comment'),
    path('delete-comment/<str:id>',
         DeleteCommentAPIView.as_view(), name='delete-comment'),
    path('get-all-comment-by-post/', GetAllCommentByPostAPIView.as_view(),
         name='get-all-comment-by-post'),
    path('post-like/', AddLike.as_view(), name='post-like'),
]
