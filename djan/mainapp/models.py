from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255)

    def __str__(self):
        return self.supplier_name

class ProductMarket(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

# class SupplierObligation(models.Model):
#     obligation_amount = models.
#     supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

class ProductWarehouse(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_quantity = models.IntegerField()
    product_category = models.CharField(max_length=255)
    product_market = models.ForeignKey(ProductMarket, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.product_name} ({self.product_amount})"

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_product = models.ForeignKey(ProductWarehouse, on_delete=models.SET_NULL, null=True)
    order_product_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_product_quantity = models.IntegerField()

    def __str__(self):
        return f"Product {self.order_product.product_name} in Order {self.order.order_id}"
    
# CUSTOMOWY USERRRR == gowno, nie patrzec na to bo mozna sie zalamac

# class AppUser(AbstractUser):
#     USER_TYPE_CHOICES = (
#         (1, 'Employee'),
#         (2, 'Client'),
#     )

#     user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=2)

#     def __str__(self):
#         return self.email if self.email else self.username