from django.db import models

# Create your models here.

class Products_warehouse(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_amount = models.IntegerField()
    product_category = models.CharField(max_length=255)

class Products_market(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)

class Suppliers(models.Model):
    supplier_name = models.CharField(max_length=255)
