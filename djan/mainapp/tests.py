from django.test import TestCase, Client
from mainapp.models import *
from unittest.mock import patch, MagicMock
from django.apps import apps
from django.urls import reverse


# JEDNOSTKOWE

class CartModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='TEST_user', password='12345678D')
        self.cart = Cart.objects.create(user=self.user)

        self.supplier = Supplier.objects.create(supplier_name='TEST_supplier')
        self.category = ProductCategory.objects.create(category_name="Electronics", slug="electronics")

        self.product_market = MarketProduct.objects.create(
            product_name='TEST_product', 
            product_price=24.99, 
            supplier=self.supplier
        )
        self.product1 = WarehouseProduct.objects.create(
            product_name='TEST_product_1',
            product_price=50.00,
            product_quantity=100,
            product_market=self.product_market,
            product_category=self.category
        )

    def test_total_value_single_product(self):
        CartProduct.objects.create(
            cart=self.cart,
            product=self.product1,
            product_price=self.product1.product_price,
            product_quantity=1
        )
        self.assertEqual(float(self.cart.total_value()), 33.99)

    def test_total_value_multiple_products(self):
        CartProduct.objects.create(
            cart=self.cart,
            product=self.product1,
            product_price=self.product1.product_price,
            product_quantity=2
        )
        self.assertEqual(float(self.cart.total_value()), 67.98)

    def test_total_value_empty_cart(self):
        self.assertEqual(self.cart.total_value(), 0.00)

    def test_total_value_with_discount(self):
        self.product1.product_discount = 10
        self.product1.refresh_price() 

        CartProduct.objects.create(
            cart=self.cart,
            product=self.product1,
            product_price=self.product1.product_price_discounted,
            product_quantity=1
        )
        expected_value = self.product1.product_price_discounted * 1
        self.assertEqual(self.cart.total_value(), expected_value)

# FUNKCJONALNE

class ProductListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.supplier = Supplier.objects.create(supplier_name='TEST_supplier')
        self.category = ProductCategory.objects.create(category_name="Electronics", slug="electronics")

        self.product_market = MarketProduct.objects.create(
            product_name='TEST_product', 
            product_price=24.99, 
            supplier=self.supplier
        )
        self.product1 = WarehouseProduct.objects.create(
            product_name='TEST_product_1',
            product_price=50.00,
            product_quantity=100,
            product_market=self.product_market,
            product_category=self.category
        )
    
    def test_product_list(self):
        # response = self.client.get('127.0.0.1:8000/electronics/test-product/')
        response = self.client.get(reverse('product_detail', args=['electronics', 'test-product']))

        self.assertEqual(response.status_code, 200)
        self.assertIn('Product A', response.content.decode())

# AKCEPTACYJNE

class UserRegistrationAcceptanceTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_registration_and_login(self):
        response = self.client.post('/register/', {'username': 'newuser', 'password': 'securepassword'})
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/login/', {'username': 'newuser', 'password': 'securepassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome, newuser', response.content.decode())

# ARCHITEKTURY

class ArchitectureTest(TestCase):
    def test_installed_apps(self):
        required_apps = ['mainapp']
        for app in required_apps:
            self.assertTrue(apps.is_installed(app), f"{app} is not installed!")

# AUTENTYKACJI

class AuthenticationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_login_user(self):
        response = self.client.post('logowanie/', {'username': 'testuser', 'password': '12345'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome, testuser', response.content.decode())

