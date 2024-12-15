from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.timezone import now

# MODELE ALE NIE MODELKI

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255)

    def __str__(self):
        return self.supplier_name

class MarketProduct(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

# ZOBOWIAZANIA

class SupplierObligation(models.Model):
    obligation_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    obligation_amount = models.DecimalField(max_digits=15, decimal_places=2)
    obligation_date = models.DateField(auto_now_add=True)
    obligation_deadline = models.DateField(null=True)
    status_choices = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')

    def __str__(self):
        return f"Obligation {self.obligation_id} to {self.supplier.supplier_name}: {self.obligation_amount} ({self.status})"

    def mark_as_paid(self):
        self.status = 'paid'
        self.save()

    def is_overdue(self):
        if self.status == 'pending' and self.obligation_deadline < timezone.now().date():
            self.status = 'overdue'
            self.save()

class WarehouseBalance(models.Model):
    date = models.DateField(default=now, unique=True)  # Data balansu, unikalna dla każdego dnia
    total_inventory_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Wartość magazynu
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Zobowiązania
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Dochody (narazie z zamówień)
    net_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Saldo netto

    class Meta:
        verbose_name = "Dzienne saldo"
        verbose_name_plural = "Dzienny balans"
        ordering = ['-date']

    def __str__(self):
        return f"Balans na dzień {self.date}: {self.net_balance} PLN"

    def calculate_balance(self):
        self.total_inventory_value = sum(
            product.product_price * product.product_quantity
            for product in WarehouseProduct.objects.all()
        )
        self.total_liabilities = sum(
            obligation.obligation_amount
            for obligation in SupplierObligation.objects.filter(status="pending")
        )
        self.total_income = sum(
            order.total_price
            for order in Order.objects.filter(created_at__date=self.date)
        )

        self.net_balance = self.total_income + self.total_inventory_value - self.total_liabilities
        self.save()

# TOWAR NA MAGAZYNIE TU:

class WarehouseProduct(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_quantity = models.IntegerField()
    product_category = models.CharField(max_length=255)
    product_market = models.ForeignKey(MarketProduct, on_delete=models.SET_NULL, null=True)
    # product_image = models.ImageField(upload_to='products/')
    # product_description = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.product_name} ({self.product_quantity})"


# ZAMOWIENIE

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    status_choices = [
        ('wait_for_paid', 'Wait_for_paid'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('wait_for_fulfilment', 'wait_for_fulfilment'),
        ('fulfilled', 'Fulfilled'),
    ]

    status = models.CharField(max_length=255, choices=status_choices, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.)
    

    def _total_price(self):
        total = sum(item.order_product_price * item.order_product_quantity for item in self.orderproduct_set.all())
        return total

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_product = models.ForeignKey(WarehouseProduct, on_delete=models.SET_NULL, null=True)
    order_product_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_product_quantity = models.IntegerField()

    def __str__(self):
        return f"Product {self.order_product.product_name} in Order {self.order.order_id}"