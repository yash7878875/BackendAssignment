from rest_framework import serializers
from .models import *


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ["users", "user_post", "comment"]

# class LikeSerializer(serializers.ModelSerializer):
#     users = serializers.IntegerField()
#     user_post = serializers.IntegerField()
#     class Meta:
#         model = Like
#         fields = ["users", "user_post"]


class PostLikeSerializer(serializers.Serializer):
    class Meta:
        model = Like
        fields = ["users", "user_post"]


class PostDisLikeSerializer(serializers.Serializer):
    class Meta:
        model = Like
        fields = ["users", "user_post"]


class GetAllCommentByPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        fields = ['id']


class DeleteCommenterializers(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        fields = ['id']
