from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from accounts.models import ApplicationUser, UserOTP
from accounts.utils import generate_otp, send_email, send_otp


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationUser
        fields = (
            'id', 'email', 'phone', 'password', 'first_name',
            'last_name', 'date_joined', 'username', 'role',
        )
        extra_kwargs = {
            'password': {
                'write_only': True, 'validators': [validate_password]
            },
            'role': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'phone': {'required': True, 'allow_blank': False},
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'username': {'required': True, 'allow_blank': False},
        }
        read_only_fields = ('date_joined', 'id')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        user.set_password(password)
        user.save(update_fields=['password'])

        try:
            otp = generate_otp()
            UserOTP.objects.create(user=user, otp=otp)

            subject = "Email Verification"
            message = (
                f"Hello {user.first_name},"
                f"\n\nFor Email verification OTP is {otp}."
                f"\n\nRegards,"
                f"\n Auth Microservice Team"
            )
            recipient_list = [user.email]

            send_email(
                subject=subject, message=message, recipient_list=recipient_list
            )

        except Exception as e:
            print('Error in registration:', e)

        return user


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, allow_blank=False, allow_null=False
    )

    def validate(self, attrs):
        try:
            user = ApplicationUser.objects.get(email=attrs.get('email'))
        except Exception as e:
            raise serializers.ValidationError(_('Enter email is not correct.'))

        if user and user.is_email_verified:
            raise serializers.ValidationError(_('Already email is verified.'))

        validated_data = super().validate(attrs)
        validated_data['user'] = user
        validated_data['otp'] = generate_otp()
        return validated_data

    def save(self, **kwargs):
        validate_data = self.validated_data
        user = validate_data.get('user', None)
        otp = validate_data.get('otp', None)

        try:
            UserOTP.objects.create(user=user, otp=otp)

            subject = "Email Verification"
            message = (
                f"Hello {user.first_name},"
                f"\n\nFor Email verification OTP is {otp}."
                f"\n\nRegards,"
                f"\n Auth Microservice Team"
            )
            recipient_list = [user.email]
            send_email(
                subject=subject, message=message, recipient_list=recipient_list
            )
        except Exception as e:
            raise serializers.ValidationError(f'{e}')

        return user


class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.IntegerField(required=True)
    email = serializers.EmailField(
        required=True, allow_null=False, allow_blank=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            user = ApplicationUser.objects.get(email=email)
        except ApplicationUser.DoesNotExist:
            raise serializers.ValidationError(_('Email does not exist.'))

        user_otp = UserOTP.objects.filter(user=user).last()

        if not user_otp:
            raise serializers.ValidationError(_('OTP does not exist for this user.'))

        if user_otp.is_verified:
            raise serializers.ValidationError(_('Email is already verified.'))

        if user_otp.expiration_time < timezone.now():
            raise serializers.ValidationError(_('OTP has expired.'))

        if otp != user_otp.otp:
            raise serializers.ValidationError(_('OTP is invalid!'))

        user_otp.is_verified = True
        user_otp.save()

        return attrs


class SendOTPSerializer(serializers.Serializer):
    phone = PhoneNumberField(required=True, allow_blank=False)

    def validate(self, attrs):
        try:
            user = ApplicationUser.objects.get(phone=attrs.get('phone'))
        except Exception as e:
            raise serializers.ValidationError(_('Enter phone number is not correct.'))

        attrs['user'] = user
        attrs['otp'] = generate_otp()
        return attrs

    def save(self, **kwargs):
        validate_data = self.validated_data
        user = validate_data.get('user', None)
        otp = validate_data.get('otp', None)

        try:
            UserOTP.objects.create(user=user, otp=otp)
        except Exception as e:
            raise serializers.ValidationError(f'{e}')

        # Send Sms by Twillio
        try:
            send_otp(user=user, otp=otp)
        except Exception as e:
            print(f'{e}')
        return otp


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = PhoneNumberField(required=False)
    password = serializers.CharField(required=False)
    otp = serializers.IntegerField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        email = attrs.get('email')
        password = attrs.get('password')
        phone = attrs.get('phone')
        otp = attrs.get('otp')

        if not 'email' and not 'phone':
            raise serializers.ValidationError(_('Either email or phone is required.'))

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError(_('User account is disabled.'))
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError("Invalid email or password.")

        if phone and otp:
            try:
                user = ApplicationUser.objects.get(phone=phone)
            except ApplicationUser.DoesNotExist:
                raise serializers.ValidationError(_('User does not exist.'))

            user_otp = UserOTP.objects.filter(user=user).last()

            if user_otp:
                if user_otp.otp != otp:
                    raise serializers.ValidationError('Invalid OTP.')

                if user_otp.expiration_time < timezone.now():
                    raise serializers.ValidationError(_('OTP has expired.'))

                if user_otp.is_verified:
                    raise serializers.ValidationError(_(''))

                user_otp.delete()
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError("Invalid OTP or OTP expired.")

        raise serializers.ValidationError("Invalid combination of credentials.")


class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationUser
        fields = (
            'id', 'email', 'phone', 'first_name',
            'last_name', 'date_joined', 'username',
            'password', 'role',
        )
        extra_kwargs = {
            'password': {
                'write_only': True, 'validators': [validate_password]
            },
        }
        read_only_fields = ('date_joined', 'id', 'username', 'email', 'role')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
