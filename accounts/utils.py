import random

from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from twilio.rest import Client


def set_password_reset_expiration_time():
    return timezone.now() + timezone.timedelta(minutes=15)


def set_otp_expiration_time():
    return timezone.now() + timezone.timedelta(minutes=5)


def generate_otp(length=4):
    otp = random.randint(1000, 9999)
    print('OTP :', otp)
    return otp


def send_otp(user, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    body = f'OTP is {otp}.'
    message = client.messages.create(body=body, from_=settings.TWILIO_PHONE_NUMBER, to=f'{user.phone}')
    return JsonResponse({'status': 'Message sent successfully'})


def send_email(subject, message, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
        fail_silently=True,
    )
