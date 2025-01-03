from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import *
from django.core.exceptions import ValidationError

@admin.register(MarketProduct)
class ProductMarketAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_price', 'supplier')  
    search_fields = ('product_name', 'supplier__supplier_name')  
    list_filter = ('supplier',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name',)
    search_fields = ('supplier_name',)

@admin.register(SupplierObligation)
class SupplierObligationAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'obligation_amount', 'obligation_date','obligation_deadline')
    search_fields = ('supplier', 'obligation_amount', 'obligation_date','obligation_deadline')
    list_filter = ('supplier','obligation_date','obligation_deadline')

# ------------------------------------------------------------------------------------------------------------
# BALANS KALKULACJA I INNE
# ------------------------------------------------------------------------------------------------------------

@admin.register(WarehouseBalance)
class WarehouseBalanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_inventory_value', 'total_liabilities','daily_income', 'daily_balance','net_balance')
    list_filter = ('date',)
    ordering = ('-date',)
    actions = ['recalculate_selected_balances']

    @admin.action(description="Przelicz wybrane dzienne salda")
    def recalculate_selected_balances(self, request, queryset):
        for balance in queryset:
            balance.calculate_balance()
        self.message_user(request, "Wybrane salda zostały przeliczone.")

# ------------------------------------------------------------------------------------------------------------
# PRODUKTY NA MAGAZYNIE
# ------------------------------------------------------------------------------------------------------------

@admin.register(WarehouseProduct)
class ProductWarehouseAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_price', 'get_category', 'product_quantity', 'get_supplier') 
    search_fields = ('product_name', 'product_price', 'product_category', 'product_quantity', 'product_market__supplier__supplier_name')  # Wyszukiwanie po dostawcy
    list_filter = ('product_category', 'product_market__supplier',)

    def get_supplier(self, obj):
        return obj.product_market.supplier.supplier_name if obj.product_market and obj.product_market.supplier else "-"
    
    def get_category(self, obj):
        return obj.product_category.category_name if obj.product_category else "-"
    
    get_supplier.short_description = 'Supplier' 
    get_category.short_description = 'Category'

    def save_model(self, request, obj, form, change):
        if not obj.product_market:
            raise ValidationError("Produkt musi pochodzić z rynku.")
        super().save_model(request, obj, form, change)

# ------------------------------------------------------------------------------------------------------------
# ZAMOWIENIA
# ------------------------------------------------------------------------------------------------------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'created_at', 'status','total_price')
    search_fields = ('order_id', 'user', 'status','created_at')
    list_filter = ('user', 'created_at')
    actions = ['recalculate_selected_orders']

    # def get_total_value(self, obj):
    #     return obj._total_price()
    
    # get_total_value.short_description = 'Total value' 

    @admin.action(description="Przelicz wartosc calkowita zamowienia")
    def recalculate_selected_orders(self, request, queryset):
        for order in queryset:
            order.calculate_total_price()
        self.message_user(request, "Wybrane salda zostały przeliczone.")

@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'order_product', 'order_product_quantity', 'get_price')
    search_fields = ('order', 'order_product', 'order_product_quantity')
    list_filter = ('order', 'order_product')

    def get_price(self, obj):
        return obj.order_product_quantity * obj.order_product_price

    get_price.short_description = "Total value of product/s"

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'slug')
    search_fields = ('category_name',)
    list_filter = ('category_name',)
