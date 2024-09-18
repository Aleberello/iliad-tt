from rest_framework import serializers
from .models import Product, Order


class BaseSerializer(serializers.ModelSerializer):
    """
    Abstract base serializer inherited by other serializers.
    Contains base fields: id, created_at, updated_at, deleted_at and is_deleted
    with logics for soft delete and restore mechanism.
    """
    class Meta:
        abstract = True
        fields = ['id',  'created_at', 'updated_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['created_at', 'updated_at', 'is_deleted', 'deleted_at']
        write_only_fields = []


class ProductSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Product
        fields = BaseSerializer.Meta.fields + ['name', 'price']

    def validate_price(self, value):
        """
        Validator for product price, cannot be negative.
        """
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value


class OrderSerializer(BaseSerializer):
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        many=True,
        write_only=True
    )

    class Meta(BaseSerializer.Meta):
        model = Order
        fields = BaseSerializer.Meta.fields + \
            ['name', 'description', 'date', 'products', 'product_ids']
        write_only_fields = BaseSerializer.Meta.write_only_fields + \
            ['product_ids']

    def validate_product_ids(self, value):
        """
        Validator for order products, need at least one product for order.
        """
        if not value:
            raise serializers.ValidationError(
                "Order must contain at least one product.")
        return value

    def create(self, validated_data):
        """
        Override create method to accept only active product by id.
        """
        product_ids = validated_data.pop('product_ids')
        order = Order.objects.create(**validated_data)
        order.products.set(product_ids)
        return order

    def update(self, instance, validated_data):
        """
        Override update method to accept only active product by id.
        """
        product_ids = validated_data.pop('product_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if product_ids is not None:
            instance.products.set(product_ids)
        instance.save()
        return instance
