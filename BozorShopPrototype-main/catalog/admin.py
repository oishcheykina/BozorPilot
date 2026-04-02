from django.contrib import admin
from django.utils.html import format_html

from .models import Brand, Category, Product, Seller, Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'shop')
    list_filter = ('shop',)
    search_fields = ('name', 'shop__name')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'shop')
    list_filter = ('shop',)
    search_fields = ('name', 'shop__name')


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'shop', 'rating', 'location')
    list_filter = ('shop', 'rating')
    search_fields = ('name', 'location', 'shop__name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'shop', 'category', 'brand', 'seller', 'image_preview', 'price', 'stock')
    list_filter = ('shop', 'category', 'brand', 'seller')
    search_fields = ('name', 'description', 'shop__name', 'category__name', 'brand__name', 'seller__name')
    readonly_fields = ('image_preview',)
    fields = ('shop', 'name', 'category', 'brand', 'seller', 'image', 'image_preview', 'description', 'stock', 'price')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 90px; border-radius: 8px;" />', obj.image.url)
        return 'Нет фото'

    image_preview.short_description = 'Превью'
