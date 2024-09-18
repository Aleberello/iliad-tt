from django.test import TestCase
from django.utils import timezone
from ..models import Product, Order


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', price=10.00)

    def test_retrives_all_products(self):
        self.product.delete()
        all_products = Product.all_objects.all()
        self.assertEqual(all_products.count(), 1)

    def test_retrieves_only_not_deleted_products(self):
        self.product.delete()
        active_products = Product.objects.all()
        self.assertEqual(active_products.count(), 0)

    def test_soft_delete(self):
        self.product.delete()
        self.assertIsNotNone(self.product.deleted_at)
        self.assertTrue(self.product.is_deleted())

    def test_restore(self):
        self.product.delete()
        self.product.restore()
        self.assertIsNone(self.product.deleted_at)
        self.assertFalse(self.product.is_deleted())

    def test_created_at_initialization(self):
        self.assertIsNotNone(self.product.created_at)
        self.assertEqual(self.product.created_at.date(), timezone.now().date())

    def test_updated_at_changes_on_save(self):
        original_updated_at = self.product.updated_at
        self.product.name = 'Updated Product'
        self.product.save()
        self.assertNotEqual(original_updated_at, self.product.updated_at)

    def test_updated_at_not_changed_on_no_save(self):
        original_updated_at = self.product.updated_at
        self.product.refresh_from_db()
        self.assertEqual(original_updated_at, self.product.updated_at)


class OrderModelTest(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name='Test Product 1', price=10.00)
        self.product2 = Product.objects.create(name='Test Product 2', price=20.00)

    def test_create_order_and_retrive(self):
        order = Order.objects.create(
            name='Test Order',
            description='This is a test order',
            date=timezone.now().date()
        )
        order.products.add(self.product1)
        self.assertEqual(order.name, 'Test Order')
        self.assertEqual(order.description, 'This is a test order')
        self.assertEqual(order.products.count(), 1)

    def test_order_to_str(self):
        order = Order.objects.create(
            name='Order 1',
            description='Description 1',
            date=timezone.now().date()
        )
        order.products.add(self.product1)
        self.assertEqual(str(order), 'Order num: Order 1')
        
    def test_soft_delete(self):
        order = Order.objects.create(
            name='Order to Delete',
            description='This order will be deleted',
            date=timezone.now().date()
        )
        order.products.add(self.product1)
        order.delete()
        self.assertTrue(order.is_deleted())
        self.assertEqual(Order.objects.count(), 0)  # Should not be retrievable

    def test_restore_order(self):
        order = Order.objects.create(
            name='Order to Restore',
            description='This order will be restored',
            date=timezone.now().date()
        )
        order.products.add(self.product1)
        order.delete()
        order.restore()
        self.assertFalse(order.is_deleted())
        self.assertEqual(Order.objects.count(), 1)  # Should be retrievable again

    def test_update_order(self):
        order = Order.objects.create(
            name='Order to Update',
            description='This order will be updated',
            date=timezone.now().date()
        )
        order.products.add(self.product2)
        order.name = 'Updated Order'
        self.assertEqual(order.name, 'Updated Order')
