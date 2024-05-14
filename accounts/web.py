from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from accounts.forms import ForgotPasswordForm
from accounts.models import PasswordResetId

User = get_user_model()


def password_reset_change_password(request, password_reset_id):
    password_reset_obj = get_object_or_404(
        PasswordResetId,
        pk=password_reset_id,
        expiration_time__gt=timezone.now()
    )

    if request.method == 'POST':
        forgot_password = ForgotPasswordForm(request.POST)
        if forgot_password.is_valid():
            user = User.objects.get(pk=password_reset_obj.user.id)
            user.set_password(forgot_password.cleaned_data['password'])
            user.save()
            password_reset_obj.delete()
            return redirect('/forgot-password-success/')
    return render(request, 'accounts/forgot-password.html')


def password_reset_success(request):
    return render(request, 'accounts/forgot-password-success.html')
