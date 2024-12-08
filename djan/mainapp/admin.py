from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ProductMarket,ProductWarehouse, Supplier
from django.core.exceptions import ValidationError

@admin.register(ProductMarket)
class ProductMarketAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_price', 'supplier')  
    search_fields = ('product_name', 'supplier__supplier_name')  
    list_filter = ('supplier',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name',)
    search_fields = ('supplier_name',)

@admin.register(ProductWarehouse)
class ProductWarehouseAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_price', 'product_category', 'product_amount', 'get_supplier') 
    search_fields = ('product_name', 'product_price', 'product_category', 'product_amount', 'product_market__supplier__supplier_name')  # Wyszukiwanie po dostawcy
    list_filter = ('product_category', 'product_market__supplier',)

    def get_supplier(self, obj):
        return obj.product_market.supplier.supplier_name if obj.product_market and obj.product_market.supplier else "-"
    
    get_supplier.short_description = 'Supplier' 

    def save_model(self, request, obj, form, change):
        """Weryfikacja przy zapisie - Produkt musi mieć powiązanie z ProductMarket."""
        if not obj.product_market:
            raise ValidationError("Produkt musi pochodzić z rynku.")
        super().save_model(request, obj, form, change)

# # Rozszerzenie UserAdmin (jeśli chcesz dostosować pola)
# class CustomUserAdmin(UserAdmin):
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important Dates', {'fields': ('last_login', 'date_joined')}),
#     )

# # Rejestracja modelu User z nową konfiguracją
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
