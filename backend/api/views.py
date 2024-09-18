from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from .models import Order, Product
from .serializers import OrderSerializer, ProductSerializer


class BaseViewSet(viewsets.ModelViewSet):
    """
    A base viewset to handle soft delete and restore.
    """

    def destroy(self, request, *args, **kwarg):
        instance = self.get_object()
        instance.delete()  # Soft delete
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        try:
            instance = self.get_queryset().model.all_objects.get(pk=pk, deleted_at__isnull=False)
            instance.restore()  # Restore soft delete
            return Response(status=status.HTTP_204_NO_CONTENT)
        except self.get_queryset().model.DoesNotExist:
            raise NotFound("Item not found or not deleted.")


class ProductViewSet(BaseViewSet):
    """
    A viewset for viewing and editing store products.
    """
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer


class OrderViewSet(BaseViewSet):
    """
    A viewset for viewing and editing store orders, supports filter, ordering and search for list request.
    """
    queryset = Order.objects.all().order_by('-date')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'date': ['gte', 'lte'],
    }
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'date']

    def get_queryset(self):
        # Override queryset to load orders with relative products (even the deleted ones)
        return super().get_queryset().prefetch_related(
            models.Prefetch('products', queryset=Product.all_objects.all())
        )
