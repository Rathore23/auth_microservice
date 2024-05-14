from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import PermissionDenied

from accounts.models import UserOTP


class CustomModelBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, phone=None, password=None, **kwargs):
        if not email and not phone:
            return None

        UserModel = get_user_model()

        email_query_dict = {'email__iexact': email}
        phone_query_dict = {'phone': phone}

        try:
            query_filter = Q()
            if email:
                query_filter |= Q(**email_query_dict)
            if phone:
                query_filter |= Q(**phone_query_dict)

            user = UserModel.objects.get(query_filter)

            if not user.is_active:
                raise PermissionDenied(_("User is not active."))

        except UserModel.DoesNotExist:
            return None
        except Exception:
            return None
        else:
            if email and user.check_password(password):
                return user
            if phone:
                user_otp = UserOTP.objects.filter(
                    user=user,
                )

        return None
