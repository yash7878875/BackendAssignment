from rest_framework import serializers
from .models import *


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'created_on', 'category_image']

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance


class EditCategorySerializer(serializers.ModelSerializer):
    id_s = serializers.IntegerField()

    class Meta:
        model = Category
        fields = ['id_s', 'name', 'category_image']


class DeleteCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id_s', 'name', 'category_image']


class GetCategoryByNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']
