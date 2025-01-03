from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.timezone import now
from django.utils.text import slugify
from decimal import Decimal
from django.contrib.sessions.models import Session

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

# ------------------------------------------------------------------------------------------------------------
# ZOBOWIAZANIA
# ------------------------------------------------------------------------------------------------------------

class SupplierObligation(models.Model):
    obligation_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    obligation_amount = models.DecimalField(max_digits=15, decimal_places=2)
    obligation_date = models.DateField(auto_now_add=True) # data zakupu
    obligation_deadline = models.DateField(null=True) # deadline
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

# ------------------------------------------------------------------------------------------------------------
# BILANS -> do przemyslenia i pracy (mocno)
# ------------------------------------------------------------------------------------------------------------

class WarehouseBalance(models.Model):
    date = models.DateField(default=now, unique=True)  # Data - jedna na dzien to ma byc daily
    total_inventory_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Wartość inwentarza
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_liabilities_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Zobowiązania
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Dochody calkowite ever
    daily_income = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Dochody (narazie z zamówień)
    daily_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Dzienne saldo
    net_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Saldo netto

    class Meta:
        # verbose_name = "Dzienne saldo"
        verbose_name_plural = "Balance"
        ordering = ['-date']

    def __str__(self):
        return f"Balans na dzień {self.date}: {self.net_balance} PLN"

    def calculate_balance(self):
        # Suma wartosci inwentarza (to w miare polskie slowo)
        self.total_inventory_value = sum(
            product.product_price * product.product_quantity
            for product in WarehouseProduct.objects.all()
        )
        # Zobowiazania ktore dalej wisza
        self.total_liabilities = sum(
            obligation.obligation_amount
            for obligation in SupplierObligation.objects.filter(status__in=["pending", "overdue"]) # Dziala???
        )
        self.total_liabilities_total = sum(
            obligation.obligation_amount
            for obligation in SupplierObligation.objects.all()
        )

        # Suma dochodow calkowita - wydajnosc???
        self.total_income = sum(
            order.total_price
            for order in Order.objects.all()
        )
        # Dochody na dany dzien
        self.daily_income = sum(
            order.total_price
            for order in Order.objects.filter(created_at__date=self.date)
        )

        self.daily_balance= self.daily_income + self.total_inventory_value - self.total_liabilities
        self.net_balance= self.total_income + self.total_inventory_value - self.total_liabilities_total
        self.save()

# ------------------------------------------------------------------------------------------------------------
# TOWAR NA MAGAZYNIE TU
# ------------------------------------------------------------------------------------------------------------

class ProductCategory(models.Model):
    category_name = models.CharField(max_length=255, unique=True) # rzekomo to jest najzdrowsze rozwiazanie dla kategorii
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.category_name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

class WarehouseProduct(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_quantity = models.IntegerField()
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    product_market = models.ForeignKey(MarketProduct, on_delete=models.SET_NULL, null=True)
    product_image = models.CharField(max_length=255, null=True, blank=True) # nazwa zdjecia jako podadres w staticu
    product_description = models.TextField(blank=True)
    product_discount = models.IntegerField(default=0)  # Rabat w procentach
    margin = models.IntegerField(default=10) # marża w procentach
    tax = models.IntegerField(default=23) # podatek tez w procentach

    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        # if not self.slug:
        #     base_slug = slugify(self.product_name)
        #     unique_slug = base_slug
        #     num = 1
        #     while WarehouseProduct.objects.filter(slug=unique_slug).exists():
        #         unique_slug = f"{base_slug}-{num}"
        #         num += 1
        #     self.slug = unique_slug
        if not self.slug:
            self.slug = slugify(self.product_name)

        if self.product_price:
            self.product_price = self.calculate_price()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} ({self.product_quantity})"
    
    def calculate_price(self):
        market_price = self.product_market.product_price

        price_with_margin = market_price * (1 + Decimal(self.margin) / 100)
        price_with_tax = price_with_margin * (1 + Decimal(self.tax) / 100)
    
        final_price = price_with_tax * (1 - Decimal(self.product_discount) / 100)
        return round(final_price, 2)

# ------------------------------------------------------------------------------------------------------------
# KOSZYK - > pomyslec jak chcemy obslugiwac
# ------------------------------------------------------------------------------------------------------------

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True)
    # session = models.OneToOneField(Session, on_delete=models.CASCADE, null=True, blank=True)
    # session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    # STATUS_CHOICES = [ 
    # ('active', 'Active'),
    # ('closed', 'Closed'),
    # ('abandoned', 'Abandoned'),
    # ]
    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def total_value(self):
        return sum(item.total_price() for item in self.cartproduct_set.all())
    
    def clear_cart(self):
        self.cartproduct_set.all().delete()
    
    def __str__(self):
        if self.user:
            return f"Koszyk użytkownika {self.user.username} (ID: {self.cart_id})"
        else:
            return f"Koszyk sesyjny (ID: {self.cart_id})"

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(WarehouseProduct, on_delete=models.CASCADE)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_quantity = models.IntegerField(default=1)
    product_discount = models.IntegerField(default=0) # potraktowac jako procent, przepisywac z produktu na magazynie

    def total_price(self):
        return self.product_price * self.product_quantity

# ------------------------------------------------------------------------------------------------------------
# ZAMOWIENIE -> user zamawia od nas
# ------------------------------------------------------------------------------------------------------------

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
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def calculate_total_price(self):
        total = sum(item.order_product_price * item.order_product_quantity for item in self.orderproduct_set.all())
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_product = models.ForeignKey(WarehouseProduct, on_delete=models.SET_NULL, null=True)
    order_product_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_product_quantity = models.IntegerField()

    def __str__(self):
        return f"Product {self.order_product.product_name} in Order {self.order.order_id}"
    