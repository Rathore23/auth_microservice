from django.urls import include, path
from rest_framework.routers import SimpleRouter

from products.views import ProductViewSet

router = SimpleRouter()

router.register('', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
