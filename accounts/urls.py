from django.urls import include, path
from rest_framework.routers import SimpleRouter

from accounts.views import RegistrationViewSet, AccountAuthViewSet, AccountViewSet

router = SimpleRouter()

router.register('registration', RegistrationViewSet, basename='registration')
router.register('auth', AccountAuthViewSet, basename='auth')
router.register('', AccountViewSet, basename='accounts')


app_name = 'accounts'

urlpatterns = [
    path('', include(router.urls)),
]
