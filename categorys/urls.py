from django.conf import settings
from django.urls import path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    path('creat-category/', CreatCategoryAPI.as_view(), name='creat-category'),
    path('get-all-category/', GetAllCategoryAPI.as_view(), name='get-all-category'),
    path('edit-category/', EditCategoryAPI.as_view(), name='edit-category'),
    path('delete-category/', DeleteCategoryAPI.as_view(), name='delete-category'),
    path('get-category-by-name/', GetCategoryByNameAPI.as_view(),
         name='get-category-by-name'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
