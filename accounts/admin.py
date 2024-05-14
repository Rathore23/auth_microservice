from django.contrib import admin

from accounts.models import ApplicationUser, UserOTP

# Register your models here.
admin.site.register(ApplicationUser)
admin.site.register(UserOTP)
