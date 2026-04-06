from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "active", "sort_order")
    list_filter = ("active",)
    search_fields = ("name", "slug")
    ordering = ("sort_order", "name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "category", "price", "active", "featured")
    list_filter = ("active", "featured", "category")
    search_fields = ("name", "slug", "description")
    autocomplete_fields = ("category",)
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}
