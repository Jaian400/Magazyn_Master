from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import MarketProduct,WarehouseProduct, Supplier, Order, WarehouseBalance
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


# BALANS KALKULACJA I INNE

from django.contrib import admin
from .models import WarehouseBalance

@admin.register(WarehouseBalance)
class WarehouseBalanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_inventory_value', 'total_liabilities', 'total_income', 'net_balance', 'recalculate_button')
    list_filter = ('date',)
    ordering = ('-date',)
    actions = ['recalculate_selected_balances']

    def recalculate_button(self, obj):
        """
        Przyciski do przeliczenia balansu na poziomie każdego rekordu.
        """
        return f'<button onclick="location.href=\'/admin/recalculate/{obj.id}/\'">Przelicz</button>'
    recalculate_button.short_description = "Przelicz balans"
    recalculate_button.allow_tags = True  # Pozwala na renderowanie HTML w Django Admin

    @admin.action(description="Przelicz wybrane dzienne salda")
    def recalculate_selected_balances(self, request, queryset):
        """
        Przelicz balans dla zaznaczonych rekordów.
        """
        for balance in queryset:
            balance.calculate_balance()
        self.message_user(request, "Wybrane salda zostały przeliczone.")

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

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'created_at', 'get_total_value')
    search_fields = ('order_id', 'user', 'created_at')
    list_filter = ('user', 'created_at')

    def get_total_value(self, obj):
        return obj.total_value()
    
    get_total_value.short_description = 'Total value' 
