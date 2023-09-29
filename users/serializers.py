from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password', 'date_of_birth', 'profile_image', 'country')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(RegisterSerializer, self).create(validated_data)


class GetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'password', 'date_of_birth', 'profile_image', 'country')


class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(
        max_length=128, write_only=True, style={"input_type": "password"}
    )

    class Meta:
        fields = ['username', 'password']


class UserEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'date_of_birth', 'profile_image']


class ForgotOTPSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email']


class ChangePasswordSerializer(serializers.ModelSerializer):
    newpassword = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['password', 'newpassword']
        extra_kwargs = {
            'newpassword': {'write_only': True}
        }


class ForgotPasswordSerializer(serializers.ModelSerializer):
    newpassword = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password', 'newpassword']
        extra_kwargs = {
            'newpassword': {'write_only': True}
        }


class DeleteUsererializers(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        fields = ['id']
