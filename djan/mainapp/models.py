from django.db import models

# Create your models here.

class Suppliers(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255)

class Products_market(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier_id = models.ForeignKey(Suppliers, on_delete=models.CASCADE)

class Products_warehouse(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_amount = models.IntegerField()
    product_category = models.CharField(max_length=255)
    product_id = models.ForeignKey(Products_market, on_delete=None)

class Users(models.model):
    user_id = models.AutoField(primary_key=True)
    user_type = models.BooleanField()
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField(max_length=255)
    #user_password = models.

class Orders(models.model):
    order_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)

class Orders_Products(models.model):
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    order_product_id = models.ForeignKey(Products_warehouse, on_delete=None)
    order_prodcut_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_prodcut_amount = models.IntegerField()