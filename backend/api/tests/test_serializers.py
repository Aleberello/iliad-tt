from django.test import TestCase
from ..models import Product, Order
from ..serializers import ProductSerializer, OrderSerializer


class ProductSerializerTestCase(TestCase):
    def setUp(self):
        self.valid_data = {
            'name': 'Test Product',
            'price': 10.0
        }
        self.invalid_data_negative_price = {
            'name': 'Invalid Product',
            'price': -5.0
        }

    def test_valid_serializer(self):
        serializer = ProductSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.name, self.valid_data['name'])
        self.assertEqual(product.price, self.valid_data['price'])

    def test_invalid_price(self):
        serializer = ProductSerializer(data=self.invalid_data_negative_price)
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)
        self.assertEqual(
            serializer.errors['price'][0], "Price cannot be negative.")

    def test_product_fields(self):
        serializer = ProductSerializer()
        self.assertIn('name', serializer.fields)
        self.assertIn('price', serializer.fields)
        self.assertIn('created_at', serializer.fields)
        self.assertIn('updated_at', serializer.fields)


class OrderSerializerTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', price=10.0)
        self.valid_order_data = {
            'name': 'Test Order',
            'description': 'Test Description',
            'date': '2024-01-01',
            'product_ids': [self.product.id]
        }
        self.invalid_order_data_no_products = {
            'name': 'Test Order',
            'description': 'Test Description',
            'date': '2024-01-01',
            'product_ids': []
        }

    def test_order_creation_with_products(self):
        serializer = OrderSerializer(data=self.valid_order_data)
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        self.assertEqual(order.products.count(), 1)
        self.assertEqual(order.products.first().name, self.product.name)

    def test_order_creation_without_products(self):
        serializer = OrderSerializer(data=self.invalid_order_data_no_products)
        self.assertFalse(serializer.is_valid())
        self.assertIn('product_ids', serializer.errors)
        self.assertEqual(
            serializer.errors['product_ids'][0], "Order must contain at least one product.")

    def test_order_fields(self):
        serializer = OrderSerializer()
        self.assertIn('name', serializer.fields)
        self.assertIn('description', serializer.fields)
        self.assertIn('date', serializer.fields)
        self.assertIn('products', serializer.fields)
        self.assertIn('product_ids', serializer.fields)

    def test_update_order_with_products(self):
        order = Order.objects.create(
            name='Initial Order', description='Initial Description', date='2024-01-01')
        order.products.set([self.product])

        new_product = Product.objects.create(name='New Product', price=20.0)
        updated_data = {
            'name': 'Updated Order',
            'description': 'Updated Description',
            'date': '2024-02-01',
            'product_ids': [self.product.id, new_product.id]
        }

        serializer = OrderSerializer(instance=order, data=updated_data)
        self.assertTrue(serializer.is_valid())
        updated_order = serializer.save()
        self.assertEqual(updated_order.products.count(), 2)
