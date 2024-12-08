from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AppUser


class CustomUserAdmin(UserAdmin):
    model = AppUser
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type',)}),
    )


admin.site.register(AppUser, CustomUserAdmin)
