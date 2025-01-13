from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.timezone import now
from django.utils.text import slugify
from decimal import Decimal
from django.contrib.sessions.models import Session
from datetime import datetime, timedelta
from enum import Enum

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
    product_price_discounted = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
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
            self.product_price, self.product_price_discounted = self.calculate_price()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} ({self.product_quantity})"
    
    def refresh_price(self):
        self.product_price, self.product_price_discounted = self.calculate_price()
        self.save()
    
    def calculate_price(self):
        market_price = self.product_market.product_price

        price_with_margin = Decimal(market_price) * (1 + Decimal(self.margin) / 100)
        price_with_tax = Decimal(price_with_margin) * (1 + Decimal(self.tax) / 100)

        final_price = price_with_tax

        if final_price > 1000:
            final_price = round(final_price / 50) * 50 - Decimal(0.01)
        elif final_price <= 1000 and final_price > 200:
            final_price = round(final_price, -1) - Decimal(0.01)
        elif final_price <= 200 and final_price > 20:
            final_price = round(final_price) - Decimal(0.01)
        else:
            final_price = round(final_price, 1)

        if self.product_discount > 0:
            final_price_discounted = price_with_tax * (1 - Decimal(self.product_discount) / 100)
            final_price_discounted = round(final_price_discounted, 1)
            return final_price, final_price_discounted
        else:
            return final_price, None

# ------------------------------------------------------------------------------------------------------------
# KOSZYK - > pomyslec jak chcemy obslugiwac 
# ------------------------------------------------------------------------------------------------------------
# jeden koszyk do jednego usera i jak zamowi to czyscic 
class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def total_value(self):
        return sum(item.total_price() for item in self.cartproduct_set.all())
    
    def delete_old_carts():
        old_date = now() - timedelta(days=30)
        Cart.objects.filter(user__isnull=True, session_key__isnull=True, created_at__lt=old_date).delete()
        
    def clear_cart(self):
        self.cartproduct_set.all().delete()
        self.save()
    
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
    
    def quantity_minus(self):
        if self.product_quantity > 0:
            self.product_quantity -= 1
        self.save()
    
    def quantity_plus(self):
        if self.product_quantity < self.product.product_quantity:
            self.product_quantity += 1
        self.save()

    def clear_product(self):
        self.cart.total_price -= self.total_price()
        self.cart.save()
        self.delete(keep_parents=True)

    def save(self, *args, **kwargs):
        previous_quantity = self.product_quantity
        super().save(*args, **kwargs)
        if self.product_quantity < 1:
            self.clear_product()
        elif self.product_quantity < previous_quantity:
            self.cart.total_price -= (previous_quantity - self.product_quantity) * self.product_price
            self.cart.save()
        else:
            self.cart.total_price = self.cart.total_value()
            self.cart.save()

# ------------------------------------------------------------------------------------------------------------
# ZAMOWIENIE -> user zamawia od nas
# ------------------------------------------------------------------------------------------------------------

class OrderStatus(Enum):
    WAIT_FOR_PAID = 'wait_for_paid'
    PENDING = 'pending'
    PAID = 'paid'
    WAIT_FOR_FULFILMENT = 'wait_for_fulfilment'
    FULFILLED = 'fulfilled'
    CANCELLED = 'cancelled'

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=255, choices=[(status.value, status.name) for status in OrderStatus], default=OrderStatus.PENDING.value)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def calculate_total_price(self):
        total = sum(
            item.order_product_price * item.order_product_quantity
            for item in self.orderproduct_set.all()
        )
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
    
    def make_order(self, cart):
        if not cart.cartproduct_set.exists():
            raise ValueError("Koszyk jest pusty. Nie można złożyć zamówienia.")

        self.status = OrderStatus.WAIT_FOR_PAID.value

        for cart_product in cart.cart_product.set.all():
            OrderProduct.objects.create(order=self, 
                                        order_product=cart_product.product, 
                                        order_product_price=cart_product.product_price,
                                        order_product_quantity=cart_product.product_quantity)

        cart.clear_cart()    
        self.save()
    
    def is_paid(self):
        return self.status == OrderStatus.PAID.value
    
    def is_fulfilled(self):
        return self.status == OrderStatus.FULFILLED.value
    
    def is_canceled(self):
        return self.status == OrderStatus.CANCELLED.value

    def switch_status(self, choice):
        if 0 <= choice < len(self.status_choices):
            self.status = self.status_choices[choice][0]
            self.save()
        else:
            raise ValueError("Nieprawidłowy indeks statusu.")

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_product = models.ForeignKey(WarehouseProduct, on_delete=models.SET_NULL, null=True)
    order_product_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_product_quantity = models.IntegerField()

    def __str__(self):
        return f"Product {self.order_product.product_name} in Order {self.order.order_id}"
    
    def clear_order_prodcut(self):
        self.delete(keep_parents=True)

    def save(self, *args, **kwargs):
        if self.order_product_quantity < 1:
            self.clear_order_prodcut()
            
        super().save(*args, **kwargs)
        self.order.calculate_total_price()
        self.order.save()
    