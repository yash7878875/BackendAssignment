import datetime
import os
import shutil
from .serializers import *
from rest_framework.response import Response
import filetype
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed
import jwt
from BackendAssignment.settings import SECRET_KEY
from likes_comments.models import *
from posts.paginations import CustomPagination
from .utils import *

# Create your views here.


class CreatPostView(generics.GenericAPIView):
    """
    Creat Post
    """
    serializer_class = PostSerializers
    permission_classes = [IsAuthenticated, AllowAny]

    def post(self, request, *args, **kwargs):

        try:
            import uuid
            multiid = uuid.uuid4()

            token = request.headers['Authorization']
            tk = token.replace("Bearer ", "")
            if not token:
                raise AuthenticationFailed('Unauthenticated!')

            try:
                payload = jwt.decode(tk, SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Unauthenticated!')

            user = User.objects.filter(
                id=payload['user_id'], is_active=True).last()
            if not user:
                return Response({"status": False, 'message': "User not Found"}, status=status.HTTP_404_NOT_FOUND)

            category = Category.objects.filter(
                id=request.data['category'], is_active=True).last()
            if not category:
                return Response({"status": False, 'message': "Category not Found"}, status=status.HTTP_404_NOT_FOUND)

            caption = request.data['caption']
            tool = request.data['tool']
            types = request.data['type']
            date = datetime.date.today()
            created_on = date

            if types == "image":
                image = request.FILES.getlist('file')
                for images in image:
                    y = (str(images))
                    a = y.__contains__('.png') or y.__contains__(
                        '.jpg') or y.__contains__('.jpeg') or y.__contains__('.gif')
                    if not a:
                        return Response({"status": False, 'message': "You can send only Image File"}, status=status.HTTP_201_CREATED)
                comp_images = []
                for c_img in image:
                    comp_image = compressImage(images=c_img)
                    comp_images.append(comp_image)
                s3_urls = upload_s3(comp_images, user)
                final_images = []
                for images in s3_urls:
                    final_images.append(images)
                Post.objects.update_or_create(
                    user=user, category=category, images=final_images, type="image" if len(image) == 1 else "images", caption=caption, tool=tool, multiid=multiid, created_on=created_on)
                return Response({"status": True, 'message': "Your Post Created successfully"}, status=status.HTTP_201_CREATED)
            elif types == "video":
                videos = request.FILES.getlist('file')
                comp_videos = []
                for video_file in videos:
                    video_name = video_file.name
                    if not video_name.endswith(('.mp4', '.avi', '.mov')):
                        return Response({"status": False, 'message': "You can only send video files"}, status=status.HTTP_201_CREATED)
                    comp_videos.append(
                        {'name': video_name, 'content_type': video_file.content_type, "video": video_file})
                s3_urls = upload_s3_video_audio(comp_videos, user)
                final_videos = []
                for video_dict in s3_urls:
                    final_videos.append(video_dict)
                    print(final_videos, type(final_videos))
                Post.objects.update_or_create(
                    user=user, category=category, images=final_videos, type=types, caption=caption, tool=tool, multiid=multiid, created_on=created_on)
                return Response({"status": True, 'message': "Your Post Created successfully"}, status=status.HTTP_201_CREATED)

            elif types == "audio":

                audios = request.FILES.getlist('file')
                comp_audios = []
                for audio_file in audios:
                    audio_name = audio_file.name
                    if not audio_name.endswith(('.mp3', '.wav', '.m4a', '.flac')):
                        return Response({"status": False, 'message': "You can only send audio files"}, status=status.HTTP_201_CREATED)
                    comp_audios.append(
                        {'name': audio_name, 'content_type': audio_file.content_type, "audio": audio_file})
                s3_urls = upload_s3_video_audio(comp_audios, user)
                final_audios = []
                for audio_dict in s3_urls:
                    final_audios.append(audio_dict)
                Post.objects.update_or_create(
                    user=user, category=category, images=final_audios, type=types, caption=caption, tool=tool, multiid=multiid, created_on=created_on)
                return Response({"status": True, 'message': "Your Post Created successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": False, 'message': "Please Provide valid Formate"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"status": False, 'message': "something went wrong", }, status=status.HTTP_400_BAD_REQUEST)


class EditPostByUser(generics.GenericAPIView):
    """
    Edit Post By Login User
    """
    serializer_class = EditPostByUserializers
    permission_classes = [IsAuthenticated, AllowAny]

    def post(self, request):
        try:
            tool = request.data.get("tool", None)
            category = request.data.get("category", None)
            caption = request.data.get("caption", None)
            multiid = request.data.get("multiid", None)
            category_id = Category.objects.filter(pk=category).last()
            if not category:
                return Response({"status": False, 'message': "Category not found"}, status=status.HTTP_404_NOT_FOUND)
            user_post = Post.objects.get(multiid=multiid)
            if user_post is not None:
                if (caption is None) or (tool is None):
                    return Response({"status": False, 'message': "Caption or Tool are none"}, status=status.HTTP_404_NOT_FOUND)
                user_post.caption = caption
                user_post.tool = tool
                user_post.category = category_id
                user_post.save()
                return Response({"status": True, 'message': "Post updated successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": False, 'message': "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class DeletePostAPI(generics.GenericAPIView):
    """
    Delete Post
    """
    serializer_class = DeletePostSerializers
    permission_classes = [IsAuthenticated, AllowAny]

    def post(self, request):

        try:
            id = request.data['id']
            deletepost = Post.objects.filter(pk=id).values().last()
            getmultipost = Post.objects.filter(
                multiid=deletepost['multiid']).values()
            for i, index in enumerate(getmultipost):
                images = Post.objects.get(pk=index['id'])
                images.delete()
            return Response({"status": True, 'message': "Post Deleted!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class GetAllPostView(generics.ListCreateAPIView):
    """
    Gel All Post
    """
    serializer_class = GetAllPostSerializers
    permission_classes = [IsAuthenticated, AllowAny]
    # pagination_class = CustomPagination

    def get(self, request):

        user = Post.objects.all().values().union()
        data = []

        for x, index in enumerate(user):
            postsUser = User.objects.filter(
                id=index['user_id']).values('id', 'first_name', 'username', 'profile_image').last()
            user[x]['creator'] = postsUser
            if x == 0 or index['multiid'] != user[x-1]['multiid']:
                posts = Post.objects.filter(
                    multiid=index['multiid'],).values('images').union()
                user[x]['img'] = posts

                postsLikes = Like.objects.filter(
                    user_post=index['id'], like=True).count()
                postsDisLikes = Like.objects.filter(
                    user_post=index['id'], like=False).count()
                postsComment = Comments.objects.filter(
                    user_post=index['id'], is_active=True).count()
                user[x]['likes'] = postsLikes
                user[x]['dislikes'] = postsDisLikes
                user[x]['comments'] = postsComment
                user[x]['content_type'] = index['type']
                # del user[x]['multiid']
                del user[x]['user_id']
                del user[x]['type']
                del user[x]['category_id']
                del user[x]['is_active']
                del user[x]['images']
                data.append(index)
        from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
        count = request.GET.get('count', 4)
        p = Paginator(data, count)
        page = request.GET.get('page', 1)
        try:
            post_list = p.page(page)
        except PageNotAnInteger:
            post_list = p.page(1)
        except EmptyPage:
            post_list = p.page(p.num_pages)
        return Response({"status": True, 'message': "Post Found", "data": post_list.object_list}, status=status.HTTP_200_OK)


class GetPostById(generics.GenericAPIView):
    """
    Gel Post By Id
    """
    permission_classes = [IsAuthenticated, AllowAny]

    def post(self, request, *args, **kwargs):

        try:
            getpost = Post.objects.filter(
                id=request.data['id']).values().last()
            getmultipost = Post.objects.filter(
                multiid=getpost['multiid']).values('images')
            if (getpost == None):
                return Response({"status": False, 'message': "post not found"}, status=status.HTTP_400_BAD_REQUEST)

            postsLikes = Like.objects.filter(
                user_post=getpost['id'], like=True).count()
            postsDisLikes = Like.objects.filter(
                user_post=getpost['id'], like=False).count()
            postsComment = Comments.objects.filter(
                user_post=getpost['id'], is_active=True).count()
            comments = Comments.objects.filter(
                user_post=getpost['id'], is_active=True).values()

            getpost['images'] = getmultipost
            getpost['total_likes'] = postsLikes
            getpost['total_disLikes'] = postsDisLikes
            getpost['total_comment'] = postsComment

            from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
            count = request.GET.get('count', 4)
            p = Paginator(comments, count)
            page = request.GET.get('page', 1)
            try:
                post_list = p.page(page)
            except PageNotAnInteger:
                post_list = p.page(1)
            except EmptyPage:
                post_list = p.page(p.num_pages)

            getpost['comments'] = post_list.object_list
            return Response({"status": True, 'message': "Post Found", 'data': getpost}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, 'message': "something went wrong", 'data': getpost}, status=status.HTTP_400_BAD_REQUEST)


class GetPostByCategoryAPI(generics.GenericAPIView):
    """
    Get Post By Category
    """
    serializer_class = GetPostSerializers
    permission_classes = [IsAuthenticated, AllowAny]

    def post(self, request):

        try:
            id = request.data['id']
            getpostbycategory = Post.objects.filter(
                category_id=id, is_active=True).values()
            if getpostbycategory:
                data = []
                for i, index in enumerate(getpostbycategory):
                    if i == 0 or index['multiid'] != getpostbycategory[i-1]['multiid']:
                        getmultipost = Post.objects.filter(
                            multiid=index['multiid']).values('images')
                        index['images'] = getmultipost
                        data.append(index)

                return Response({"status": True, 'message': "Post Found", 'data': data}, status=status.HTTP_201_CREATED)
            return Response({"status": False, 'message': "Post not Found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class GetPostByTypeAPI(generics.GenericAPIView):
    """
    Get Post By Category
    """
    serializer_class = GetPostSerializers
    permission_classes = [IsAuthenticated, AllowAny]

    def post(self, request):

        try:
            type = request.data['type']
            getpostbytype = Post.objects.filter(
                type__contains=type, is_active=True).values()
            if getpostbytype:
                data = []
                for i, index in enumerate(getpostbytype):
                    if i == 0 or index['multiid'] != getpostbytype[i-1]['multiid']:
                        getmultipost = Post.objects.filter(
                            multiid=index['multiid']).values('images')
                        index['images'] = getmultipost
                        data.append(index)

                return Response({"status": True, 'message': "Post Found", 'data': data}, status=status.HTTP_201_CREATED)
            return Response({"status": False, 'message': "Post not Found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class GetPostByUserAPI(generics.GenericAPIView):
    """
    Get Post By User
    """
    permission_classes = [IsAuthenticated, AllowAny]

    def get(self, request):

        try:
            token = request.headers['Authorization']
            tk = token.replace("Bearer ", "")
            if not token:
                raise AuthenticationFailed('Unauthenticated!')

            try:
                payload = jwt.decode(tk, SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Unauthenticated!')
            getpostbycategory = Post.objects.filter(
                user_id=payload['user_id'], is_active=True).values()
            data = []
            for i, index in enumerate(getpostbycategory):
                if i == 0 or index['multiid'] != getpostbycategory[i-1]['multiid']:
                    getmultipost = Post.objects.filter(
                        multiid=index['multiid']).values('images')
                    index['images'] = getmultipost
                    data.append(index)

            return Response({"status": True, 'message': "Post Found", 'data': data}, status=status.HTTP_200_OK)
        except:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class SearchPostByCategoryAPI(generics.GenericAPIView):
    """
    Get Category By Name
    """
    serializer_class = SearchPostByCategorySerializer

    def post(self, request):

        try:
            name = request.data['name']
            getcategory = Category.objects.filter(
                name=name, is_active=True).last()
            if getcategory:
                getpost = Post.objects.filter(
                    category_id=getcategory.pk, is_active=True).values()
                if getpost:
                    data = []
                    for i, index in enumerate(getpost):
                        if i == 0 or index['multiid'] != getpost[i-1]['multiid']:
                            getmultipost = Post.objects.filter(
                                multiid=index['multiid']).values('images')
                            index['images'] = getmultipost
                            data.append(index)
                    return Response({"status": True, 'message': "Post Found", 'data': data}, status=status.HTTP_201_CREATED)
                return Response({"status": False, 'message': "Post Not Found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"status": False, 'message': "Category Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_404_NOT_FOUND)
