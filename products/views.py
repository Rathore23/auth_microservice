from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsReadOnly, IsManagerOrAdmin, IsOwner, IsAdmin


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        print('method :', self.action)
        if self.action == 'list':
            permission_classes = [IsReadOnly]
        elif self.action == 'create':
            permission_classes = [IsManagerOrAdmin]
        elif self.action in ['partial_update', 'destroy']:
            permission_classes = [IsOwner | IsAdmin]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
