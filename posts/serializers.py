from rest_framework import serializers
from .models import *


class PostSerializers(serializers.Serializer):
    images = serializers.ListField(
                child=serializers.FileField(max_length=100000,
                                         allow_empty_file=False,
                                        use_url=True ))

    class Meta:
        model = Post
        fields = ['id', 'images', 'created_on',
                  'tool', 'category', 'caption']


class EditPostByUserializers(serializers.Serializer):
    class Meta:
        model = Post
        fields = ['tool', 'category', 'caption']


class DeletePostSerializers(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        fields = ['id']


class GetPostSerializers(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        fields = ['id']


class GetAllPostSerializers(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Post
        fields = '__all__'


class SearchPostByCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name',]


