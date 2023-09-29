from rest_framework import generics, status
from BackendAssignment.settings import SECRET_KEY
from users.emails import send_otp_via_email
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.contrib.auth import authenticate
from django.utils import timezone
from users.paginations import CustomPagination
from posts.utils import *

# Create your views here.


class RegisterView(generics.GenericAPIView):
    """
    User Register
    """
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def post(self, request):

        serilizer = self.get_serializer(
            data=self.request.data, context={'request': request})
        if serilizer.is_valid(raise_exception=True):
            username = request.data.get("username", None)
            first_name = request.data.get("first_name", None)
            last_name = request.data.get("last_name", None)
            date_of_birth = request.data.get("date_of_birth", None)
            password = request.data.get("password", None)
            password = make_password(password)
            email = request.data.get("email", None)
            country = request.data.get("country", None)
            profile_image = request.FILES.getlist('profile_image')
            user, objects = User.objects.update_or_create(username=username,
                                                          first_name=first_name,
                                                          last_name=last_name,
                                                          date_of_birth=date_of_birth,
                                                          password=password,
                                                          email=email,
                                                          country=country)
            comp_images = []
            for c_img in profile_image:
                comp_image = compressImage(images=c_img)
                comp_images.append(comp_image)

            s3_urls = upload_s3(comp_images, user)
            user.profile_image = s3_urls[0]
            user.save()
            send_otp_via_email(user.email, False)
        return Response({"status": True, 'message': "Registered successfully, please check email"}, status=status.HTTP_201_CREATED)


class UserEmailVerifyOTP(generics.GenericAPIView):
    """
    User Email Verify OTP
    """
    serializer_class = VerifyAccountSerializer
    serializer_class = VerifyAccountSerializer

    def post(self, requs):

        try:
            data = requs.data
            serializers = VerifyAccountSerializer(data=data)
            if serializers.is_valid(raise_exception=True):

                email = serializers.data['email']
                otp = serializers.data['otp']

                user = User.objects.filter(email=email, is_active=True).last()
                if user:
                    if user.otp == otp:
                        user.is_verified = True
                        user.save()
                        return Response({"status": True, 'message': 'Account Verified Successfully', 'data': serializers.data}, status=status.HTTP_200_OK)
                    else:
                        return Response({"status": False, 'massege': 'Invalid OTP'}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({"status": False, 'massege': 'User not Found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": False,
                'massege': 'somthings went wrong',
                'errors': serializers.errors,
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """
    User Login
    """
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):

        data = request.data
        username = data.get("username", "")
        password = data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            serializer_class = self.get_serializer(data=request.data)
            if serializer_class.is_valid(raise_exception=True):
                if not user.is_verified:
                    return Response({"status": False, 'message': "Please Verify Your Account"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    user_data = {"user_id": user.id,
                                 "email": user.email, "tokens": user.tokens}
                    user.last_login = timezone.now()
                    user.save()
                    return Response({"status": True, 'message': "valid_credentials", 'data': user_data}, status=status.HTTP_200_OK)
        return Response({"status": False, 'message': "login_invalid_credentials"}, status=status.HTTP_400_BAD_REQUEST)


class UserView(generics.GenericAPIView):
    """
    User Data By Id
    """
    permission_classes = [IsAuthenticated, AllowAny]

    def get(self, request):

        username = self.request.query_params.get('username')
        id = self.request.query_params.get('id')
        try:
            if id:
                user = User.objects.filter(
                    id=id, is_active=True).first()
            else:
                user = User.objects.filter(
                    username=username, is_active=True).first()
            if user == None:
                return Response({'status': False, 'message': "No User Found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = RegisterSerializer(user)
            return Response({'status': True, 'message': "User Found", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': False, 'message': "something went wrong"}, status=status.HTTP_401_UNAUTHORIZED)


class AllUserView(generics.ListCreateAPIView):
    """
    All User Data
    """
    serializer_class = GetSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated, AllowAny]

    def get(self, request):
        try:
            user = User.objects.filter(is_active=True).values().union()
            from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
            count = request.GET.get('count', 4)
            p = Paginator(user, count)
            page = request.GET.get('page', 1)
            try:
                post_list = p.page(page)
            except PageNotAnInteger:
                post_list = p.page(1)
            except EmptyPage:
                post_list = p.page(p.num_pages)
            for i in post_list.object_list:
                del i['password']
            return Response({"status": True, 'message': "User Found", "data": post_list.object_list}, status=status.HTTP_200_OK)
        except:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class UserEdit(generics.GenericAPIView):
    """
    Edit User
    """
    permission_classes = [IsAuthenticated, AllowAny]
    serializer_class = UserEditSerializer

    def post(self, request):
        try:
            tk = request.headers['Authorization']
            token = tk.replace("Bearer ", "")
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            date_of_birth = request.data['date_of_birth']
            profile_image = request.FILES.getlist('profile_image')
            if not token:
                raise AuthenticationFailed('Unauthenticated!')
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Unauthenticated!')
            user = User.objects.filter(
                id=payload['user_id'], is_active=True).first()
            comp_images = []
            for c_img in profile_image:
                comp_image = compressImage(images=c_img)
                comp_images.append(comp_image)
            s3_urls = upload_s3(comp_images, user)

            if user is None:
                raise AuthenticationFailed('User not found!')
            else:
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                if date_of_birth:
                    user.date_of_birth = date_of_birth
                if profile_image:
                    user.profile_image.delete()
                    user.profile_image = s3_urls[0]
                    user.save()
                user.save()
            return Response({
                "status": True,
                "message": "Your Profile Updated Successfully!",
            }, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPI(generics.GenericAPIView):
    """
    Changer User Password
    """
    permission_classes = [IsAuthenticated, AllowAny]
    serializer_class = ChangePasswordSerializer

    def post(self, request):

        tk = request.headers['Authorization']
        token = tk.replace("Bearer ", "")
        oldpassword = request.data['password']
        newpassword = request.data['newpassword']
        if not oldpassword or not newpassword:
            return Response({
                "status": False,
                "message": "Old Password and New Password Should not be Empty",
            }, status=status.HTTP_204_NO_CONTENT)
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        user = User.objects.filter(
            id=payload['user_id'], is_active=True).first()
        if user.check_password(oldpassword):
            user.set_password(newpassword)
            user.save()
            return Response({
                "status": True,
                "message": "Successfully Password Change",
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": False,
                "message": "Your Old Password Dos't Match!",
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


class ForgotPasswordAPI(generics.GenericAPIView):
    """
    Forgot User Password
    """
    permission_classes = [IsAuthenticated, AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):

        tk = request.headers['Authorization']
        token = tk.replace("Bearer ", "")
        newpassword = request.data['newpassword']
        if not newpassword:
            return Response({
                "status": False,
                "message": "New Password Should not be Empty",
            }, status=status.HTTP_204_NO_CONTENT)
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        user = User.objects.filter(
            id=payload['user_id'], is_active=True).first()
        if user:
            if request.data['otp'] != user.forgot_otp:
                return Response({
                    "status": False,
                    "message": "Please Provide Valid OTP",
                }, status=status.HTTP_404_NOT_FOUND)
            user.set_password(newpassword)
            user.save()
            return Response({
                "status": True,
                "message": "Successfully Password Change",
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": False,
                "message": "No User Found!",
            }, status=status.HTTP_404_NOT_FOUND)


class DeleteUserAPI(generics.GenericAPIView):
    """
    Delete Post
    """
    serializer_class = DeleteUsererializers
    permission_classes = [IsAuthenticated, AllowAny]

    def post(self, request):

        try:
            id = request.data['id']
            user = User.objects.filter(id=id, is_active=True).last()
            if user:
                user.is_active = False
                user.save()
                return Response({"status": True, 'message': "User Deleted!"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": False, 'message': "User Not Deleted!"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"status": False, 'message': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class ForgotOtpAPI(generics.GenericAPIView):
    """
    Forgot Otp Creation
    """
    serializer_class = ForgotOTPSerializer

    def post(self, request):

        send_otp_via_email(request.data['email'], True)
        return Response({"status": True, 'message': "Otp Sent Successfully For Forgot Password, please check email"}, status=status.HTTP_201_CREATED)
