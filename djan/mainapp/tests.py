from django.test import TestCase
from mainapp.models import *
from unittest.mock import patch, MagicMock

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