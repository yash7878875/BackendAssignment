from django.shortcuts import render

# Create your views here.
from rest_framework import generics

from categorys.paginations import CustomPagination
from posts.utils import compressImage, upload_s3
from .serializers import *
from BackendAssignment.settings import SECRET_KEY
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
import jwt
# from paginations import CustomPagination

# Create your views here.


class CreatCategoryAPI(generics.GenericAPIView):
    """
    Creat Category
    """
    serializer_class = CategorySerializer
    # permission_classes = [IsAuthenticated, IsAdminUser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        category_image = request.FILES.getlist('category_image')
        category = CategorySerializer(data=request.data)
        if category.is_valid(raise_exception=True):
            comp_images = []
            for c_img in category_image:
                comp_image = compressImage(images=c_img)
                comp_images.append(comp_image)
            s3_urls = upload_s3(comp_images, None)
            category_data = category.save()
            category_data.category_image = s3_urls[0]
            category_data.save()
            return Response({"status": True, 'message': "Your Category Created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": False, 'message': "Yore Category Not Created!"}, status=status.HTTP_404_NOT_FOUND)


class GetAllCategoryAPI(generics.ListCreateAPIView):
    """
     Get All Category
    """
    serializer_class = CategorySerializer
    pagination_class = CustomPagination

    # permission_classes = [IsAuthenticated,AllowAny]
    def get(self, request):
        try:
            category = Category.objects.filter(is_active=True).values().union()
            from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
            count = request.GET.get('count', 4)
            p = Paginator(category, count)
            page = request.GET.get('page', 1)
            try:
                post_list = p.page(page)
            except PageNotAnInteger:
                post_list = p.page(1)
            except EmptyPage:
                post_list = p.page(p.num_pages)
            return Response({"status": True, 'message': "Category Found", "data": post_list.object_list}, status=status.HTTP_200_OK)
        except:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class EditCategoryAPI(generics.GenericAPIView):
    """
    Edit Category
    """
    serializer_class = EditCategorySerializer
    # permission_classes = [IsAuthenticated,AllowAny]

    def put(self, request):

        try:
            data = request.data
            category_image = request.FILES.getlist('category_image')
            category = Category.objects.filter(id=data['id']).last()
            if category:
                if data.get('name'):
                    try:
                        category.name = data['name']
                        category.save()
                    except:
                        return Response({"status": False, 'message': "Category Name Already Exists"}, status=status.HTTP_409_CONFLICT)
                if category_image:
                    comp_images = []
                    for c_img in category_image:
                        comp_image = compressImage(images=c_img)
                        comp_images.append(comp_image)
                    s3_urls = upload_s3(comp_images, None)
                    category.category_image = s3_urls[0]
                    category.save()

                return Response({"status": True, 'message': "Category Updated successfully"}, status=status.HTTP_201_CREATED)
            return Response({"status": False, 'message': "Category not Found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteCategoryAPI(generics.GenericAPIView):
    """
    Delete Category
    """
    # permission_classes = [IsAuthenticated,AllowAny]
    serializer_class = DeleteCategorySerializer

    def post(self, request):

        try:
            name = request.data.get('name')

            category = Category.objects.filter(name=name).last()
            if category:
                category.category_image.delete()
                category.delete()
                return Response({"status": True, 'message': "Category Deleted successfully"}, status=status.HTTP_201_CREATED)
            return Response({"status": False, 'message': "Category not Found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)



class GetCategoryByNameAPI(generics.GenericAPIView):
    """
    Get Category By Name
    """
    # permission_classes = [IsAuthenticated,AllowAny]
    serializer_class = GetCategoryByNameSerializer

    def post(self, request):

        try:
            data = request.data
            if not data:
                return Response({"status": False, 'message': "Category Name Field is Mandatory"}, status=status.HTTP_404_NOT_FOUND)
            category = Category.objects.filter(
                name=data['name'], is_active=True).values().last()
            if category:
                return Response({"status": True, 'message': "Category Found", 'data': category}, status=status.HTTP_201_CREATED)
            return Response({"status": False, 'message': "Category not Found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
