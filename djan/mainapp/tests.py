from django.test import TestCase
from mainapp.models import *

class CartModelTestCase(TestCase):
    def test_total_value(self):
        user = User.objects.create_user(username='TEST_user', password='12345678D')
        cart = Cart.objects.create(user=user)
        supplier = Supplier.objects.create(name='TEST_supplier')
        product_market = MarketProduct.objects.create(name='TEST_product',supplier=supplier)

        product1 = WarehouseProduct.objects.create(name='TEST_product_1', price=50.00)
        product2 = WarehouseProduct.objects.create(name='TEST_product_2', price=100.00)

        CartProduct.objects.create(cart=cart, product=product1, product_price=50.00, product_quantity=1)
        CartProduct.objects.create(cart=cart, product=product2, product_price=100.00, product_quantity=2)

        self.assertEqual(cart.total_value(), 250.00)