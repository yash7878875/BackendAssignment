from django.conf import settings
from django.urls import path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    path('creat-post/', CreatPostView.as_view(), name='creat-post'),
    path('get-all-post/', GetAllPostView.as_view(), name='get-all-post'),
    path('get-post-by-id/', GetPostById.as_view(), name='get-post-by-id'),
    path('edit-post-by-user/', EditPostByUser.as_view(), name='edit-post-by-user'),
    path('delete-post/', DeletePostAPI.as_view(), name='delete-post'),
    path('get-post-by-category/', GetPostByCategoryAPI.as_view(),
         name='get-post-by-category'),
    path('get-post-by-type/', GetPostByTypeAPI.as_view(),
         name='get-post-by-type'),
    path('get-post-by-user/', GetPostByUserAPI.as_view(), name='get-post-by-user'),
    path('search-post-by-category/', SearchPostByCategoryAPI.as_view(),
         name='search-post-by-category'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
