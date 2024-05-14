import uuid as uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from accounts.utils import set_otp_expiration_time, set_password_reset_expiration_time


class ApplicationUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee')
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, null=True, blank=True
    )
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    email = models.EmailField(
        _('email address'), null=True, blank=True, unique=True,
        error_messages={'unique': _('A user with that email already exists.')},
    )
    is_email_verified = models.BooleanField(_('email verified'), default=False)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(
        _("date joined"),
        default=timezone.now
    )
    phone = PhoneNumberField(
        _("Phone"),
        null=True, blank=True,
        unique=True,
        error_messages={"unique": _("A user with that phone already exists.")}
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f'{self.id} - {self.username}'


class UserOTP(models.Model):
    user = models.ForeignKey(ApplicationUser, on_delete=models.CASCADE)
    otp = models.PositiveIntegerField(_('OTP'), null=True, blank=True)
    expiration_time = models.DateTimeField()
    is_verified = models.BooleanField(
        default=0,
        help_text=_(
            "If email is verified then used for login."
        ),
    )

    def save(self, *args, **kwargs):
        self.expiration_time = set_otp_expiration_time()
        return super().save()

    def __str__(self):
        return f'{self.id} : {self.user.username} - {self.otp}'


class PasswordResetId(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True)
    user = models.ForeignKey(ApplicationUser, on_delete=models.CASCADE)
    expiration_time = models.DateTimeField(default=set_password_reset_expiration_time)

    class Meta:
        verbose_name = 'Password reset id'
