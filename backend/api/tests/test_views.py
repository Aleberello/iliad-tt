import random
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APITestCase
from ..models import Product, Order


class ProductViewSetTestCase(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Product', price=10.0)
        # Create 200 random products
        self.products = []
        for i in range(200):
            price = round(random.uniform(0, 500), 2)
            product = Product.objects.create(name=f'Test Product {i+1}', price=price)
            self.products.append(product)
        self.url = reverse('product-list')

    def test_create_product(self):
        data = {'name': 'New Product', 'price': 20.0}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 202)

    def test_list_products(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        page_size = api_settings.PAGE_SIZE # Retrive pagination size from settings
        
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), page_size) # Check page number size result        
        self.assertEqual(response.data['count'], 201) # Check total size result

    def test_update_product(self):
        data = {'name': 'Updated Product', 'price': 15.0}
        response = self.client.put(reverse('product-detail', args=[self.product.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')

    def test_patch_product(self):
        url = reverse('product-detail', args=[self.product.id])

        updated_data = {
            'name': 'Updated Product Name',
            'price': Decimal(299.99)
        }
        
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product Name')
        self.assertAlmostEqual(self.product.price, Decimal(299.99))

    def test_soft_delete_product(self):
        response = self.client.delete(reverse('product-detail', args=[self.product.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.product.refresh_from_db()
        self.assertIsNotNone(self.product.deleted_at)  # Assuming there's a deleted_at field for soft delete

    def test_restore_product(self):
        delete_url = reverse('product-detail', args=[self.product.id])

        # Soft delete
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.product.refresh_from_db()
        self.assertIsNotNone(self.product.deleted_at)

        # Restore
        restore_url = reverse('product-restore', args=[self.product.id])
        restore_response = self.client.post(restore_url)
        self.assertEqual(restore_response.status_code, status.HTTP_204_NO_CONTENT)
        self.product.refresh_from_db()
        self.assertIsNone(self.product.deleted_at)


class OrderViewSetTest(APITestCase):
    def setUp(self):
        # Create 10 random products
        self.products = []
        for i in range(10):
            price = round(random.uniform(0, 500), 2)
            product = Product.objects.create(name=f'Test Product {i+1}', price=price)
            self.products.append(product)
        
        # Create 100 random orders
        self.orders = []
        for i in range(100):
            order = Order.objects.create(name=f'Order {i}', description=f'Description {i}', date='2024-01-01')
            order.products.add(self.products[i % 10])
            self.orders.append(order)

    def test_list_orders(self):
        url = reverse('order-list')
        response = self.client.get(url)

        page_size = api_settings.PAGE_SIZE # Retrive pagination size from settings

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), page_size) # Check page number size result
        self.assertEqual(response.data['count'], 100) # Check total size result

    def test_list_orders_excludes_soft_deleted(self):
        order = self.orders[0]
        url = reverse('order-detail', args=[order.id])
        # Delete an order
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())

        # Retrive order list and check if deleted order exists
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_ids = [order['id'] for order in response.data['results']]
        self.assertNotIn(order.id, order_ids)

    def test_create_order(self):
            url = reverse('order-list')
            data = {
                'name': 'New Order',
                'description': 'New Description',
                'date': '2024-01-01',
                'product_ids': [self.products[0].id]
            }
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Order.objects.count(), 101)

    def test_create_order_without_product(self):
        url = reverse('order-list')
        data = {
            'name': 'Invalid Order',
            'description': 'Invalid order description',
            'date': '2024-01-01',
            'product_ids': []  # No product associated
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_order(self):
        order = self.orders[0]
        url = reverse('order-detail', args=[order.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)

    def test_retrieve_order_with_soft_deleted_products(self):
        # Create and delete a product
        product = self.products[0]
        order = Order.objects.create(name=f'Order with deleted product',
                                     description=f'Description order with delete', date='2024-01-01')
        order.products.add(product)
        product.delete()

        # Retrive order details and check that deleted product exists
        url = reverse('order-detail', args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products', response.data)
        self.assertEqual(len(response.data['products']), 1)
        self.assertEqual(response.data['products'][0]['id'], product.id)

    def test_update_order(self):
        order = self.orders[0]
        url = reverse('order-detail', args=[order.id])
        data = {
            'name': 'Updated Order',
            'description': 'Updated Description',
            'date': '2024-01-01',
            'product_ids': [self.products[1].id]
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.name, 'Updated Order')

    def test_patch_order(self):
        order = self.orders[0]
        url = reverse('order-detail', args=[order.id])
        data = {
            'description': 'Partially Updated Description'
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.description, 'Partially Updated Description')

    def test_delete_order(self):
        order = self.orders[0]
        url = reverse('order-detail', args=[order.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    def test_restore_order(self):
        # Create and delete an order
        order = self.orders[0]
        url_delete = reverse('order-detail', args=[order.id])
        self.client.delete(url_delete) 

        # Restore and check order
        url_restore = reverse('order-restore', args=[order.id])
        response = self.client.post(url_restore)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Order.objects.filter(id=order.id, deleted_at__isnull=True).exists())

    def test_filter_orders_by_date(self):
        # Create order with different dates
        order1 = Order.objects.create(name='Order 1', description='First order', date='2023-01-01')
        order2 = Order.objects.create(name='Order 2', description='Second order', date='2023-01-02')
        order3 = Order.objects.create(name='Order 3', description='Third order', date='2023-01-03')

        # Filter orders by date and check
        url = reverse('order-list') + '?date__gte=2023-01-01&date__lte=2023-01-02'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_ids = [order['id'] for order in response.data['results']]
        self.assertIn(order1.id, order_ids)
        self.assertIn(order2.id, order_ids)
        self.assertNotIn(order3.id, order_ids)


    def test_search_orders_by_name(self):
        Order.objects.create(name='Special Order', description='A special order for testing', date='2023-01-01')
        Order.objects.create(name='Regular Order', description='A regular order', date='2023-01-01')
        
        # Search order by string and check
        url = reverse('order-list') + '?search=Special'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_ids = [order['id'] for order in response.data['results']]
        self.assertEqual(len(order_ids), 1)  # Assicurati di ottenere solo un risultato
        self.assertIn('Special Order', [order['name'] for order in response.data['results']])
