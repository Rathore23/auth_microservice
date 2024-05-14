from django.contrib.sites.shortcuts import get_current_site
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import ApplicationUser, PasswordResetId
from accounts.permissions import IsSelf
from accounts.serializers import (
    RegistrationSerializer,
    OTPSerializer,
    OTPVerifySerializer,
    SendOTPSerializer,
    LoginSerializer,
    AccountsSerializer
)
from accounts.utils import send_email


class RegistrationViewSet(viewsets.ViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'OTP send successfully.'}, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False,
            url_path='resent-otp', url_name='resend_otp')
    def resend_otp(self, request, *args, **kwargs):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'OTP resend successfully.'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, serializer_class=OTPVerifySerializer,
            url_path='otp-verify', url_name='otp_verify')
    def otp_verify(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = ApplicationUser.objects.get(email=validated_data['email'])
        user.is_email_verified = True
        user.save()
        return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False,
            permission_classes=[permissions.AllowAny, ],
            url_path='reset-password-email', url_name='reset_password_email')
    def reset_password_email(self, request, *args, **kwargs):
        user_email = request.data.get('email')
        if not user_email:
            raise serializers.ValidationError("Email field is required.")

        user = ApplicationUser.objects.filter(email__iexact=user_email).first()
        if not user:
            raise NotFound("User doesn't exists.")

        password_reset_obj = PasswordResetId.objects.create(user=user)

        current_site = get_current_site(request)
        reset_url = f"http://{current_site.domain}/forgot-password/{password_reset_obj.id}/"

        try:
            subject = "Reset Password"
            message = (
                f"Hello {user.first_name},"
                f"\n\n{reset_url}."
                f"\n\nRegards,"
                f"\n Auth Microservice Team"
            )
            recipient_list = [user.email]

            send_email(
                subject=subject,
                message=message,
                recipient_list=recipient_list
            )
        except Exception as e:
            print('Error in reset_password_email :', e)

        return Response({'detail': "Email has been sent."}, status=status.HTTP_200_OK)


class AccountAuthViewSet(viewsets.ViewSet):

    @action(methods=['post'], detail=False,
            permission_classes=[permissions.AllowAny, ],
            url_name='send_otp', url_path='send-otp')
    def send_otp(self, request, *args, **kwargs):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        otp = serializer.validated_data.get('otp')
        return Response(data={'otp': otp}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False,
            permission_classes=[permissions.AllowAny, ],
            url_name='login', url_path='login')
    def login(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')

        user_details = AccountsSerializer(instance=user).data
        # Create Token using JWT
        refresh = RefreshToken.for_user(user)
        user_details["refresh"] = str(refresh),
        user_details["access"] = str(refresh.access_token),

        return Response(user_details, status=status.HTTP_200_OK)

    @action(methods=['delete'], detail=False,
            permission_classes=[permissions.IsAuthenticated, ],
            url_name="logout", url_path="logout")
    def logout(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        try:
            RefreshToken(str(refresh_token)).blacklist()
        except TokenError:
            raise serializers.ValidationError(f'{TokenError}')
        return Response(status=status.HTTP_205_RESET_CONTENT)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = ApplicationUser.objects.all().order_by('-date_joined')
    serializer_class = AccountsSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelf]
    http_method_names = ['get', 'patch', 'delete', ]
