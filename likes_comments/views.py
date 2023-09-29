from django.shortcuts import render
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status

# Create your views here.


class CommentAPIView(generics.GenericAPIView):
    """
    add Comment to the post
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            pk = serializer.data['users']
            comment = Comments.objects.filter(users_id=pk).count()
            return Response({"status": True, 'message': "User Commented Successfully", "count of comments": comment}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteCommentAPIView(generics.GenericAPIView):

    """
    Delete Comment
    """
    serializer_class = DeleteCommenterializers
    permission_classes = [IsAuthenticated, AllowAny]

    def delete(self, request,  *args, **kwargs):

        try:
            comment = Comments.objects.filter(
                id=kwargs['id'], is_active=True).last()
            if comment != None:
                comment.is_active = False
                comment.save()
                return Response({"status": True, 'message': "comment Deleted!"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": False, 'message': "comment Not Found!"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    """
    add Comment to the post
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            pk = serializer.data['users']
            comment = Comments.objects.filter(users_id=pk).count()
            return Response({"status": True, 'message': "User Commented Successfully", "count of comments": comment}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAllCommentByPostAPIView(generics.GenericAPIView):
    """
    add Get All Comment By Post to the post
    """

    serializer_class = GetAllCommentByPostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        id = request.data['id']
        getcomment = Comments.objects.filter(
            user_post=id, is_active=True).values()
        if not getcomment:
            return Response({"status": False, 'message': "No Comment Found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"status": True, 'message': "Comment Found", "data": getcomment}, status=status.HTTP_200_OK)


class AddLike(generics.GenericAPIView):
    """
    add like to the post
    """
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        users = request.data['users']
        user_post = request.data['user_post']
        try:
            likes = Like.objects.filter(
                users=users, user_post=user_post).last()
            totalLike = Like.objects.filter(user_post=user_post, like=True)
            totalDissLike = Like.objects.filter(
                user_post=user_post, like=False)
            if likes == None:
                Like.objects.create(
                    users_id=users, user_post_id=user_post, like=True)
                return Response({'status': True, 'message': "Like Successfully Done", "total_likes": len(totalLike), "is_liked": True}, status=status.HTTP_201_CREATED)

            elif likes.like:
                likes.like = False
                likes.save()
                return Response({'status': True, 'message': "DisLike Successfully Done", "total_disLikes": len(totalDissLike), "is_disliked": True}, status=status.HTTP_201_CREATED)
            else:
                likes.like = True
                likes.save()
                return Response({'status': True, 'message': "Like Successfully Done", "total_likes": len(totalLike), "is_liked": True}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'status': False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
