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
    list_display = ('date', 'total_inventory_value', 'total_liabilities', 'total_income', 'net_balance')
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
    list_display = ('product_name', 'product_price', 'product_category', 'product_quantity', 'get_supplier') 
    search_fields = ('product_name', 'product_price', 'product_category', 'product_quantity', 'product_market__supplier__supplier_name')  # Wyszukiwanie po dostawcy
    list_filter = ('product_category', 'product_market__supplier',)

    def get_supplier(self, obj):
        return obj.product_market.supplier.supplier_name if obj.product_market and obj.product_market.supplier else "-"
    
    get_supplier.short_description = 'Supplier' 

    def save_model(self, request, obj, form, change):
        if not obj.product_market:
            raise ValidationError("Produkt musi pochodzić z rynku.")
        super().save_model(request, obj, form, change)

# ------------------------------------------------------------------------------------------------------------
# ZAMOWIENIA
# ------------------------------------------------------------------------------------------------------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'created_at', 'get_total_value')
    search_fields = ('order_id', 'user', 'created_at')
    list_filter = ('user', 'created_at')

    def get_total_value(self, obj):
        return obj.total_value()
    
    get_total_value.short_description = 'Total value' 
