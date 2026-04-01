from django.contrib import admin

from apps.core.models import (
    APIImportLog,
    BusinessInsight,
    BusinessProduct,
    Category,
    EventSignal,
    FavoriteProduct,
    Marketplace,
    PartnerClick,
    Product,
    ProductAlias,
    ProductAnalytics,
    ProductPrice,
    Profile,
    Role,
    SearchHistory,
)


@admin.register(Role, Profile, Marketplace, Category, Product, ProductAlias, ProductPrice, ProductAnalytics, BusinessProduct, BusinessInsight, SearchHistory, FavoriteProduct, EventSignal, PartnerClick, APIImportLog)
class DefaultAdmin(admin.ModelAdmin):
    list_display = ("__str__", "created_at", "updated_at")
    search_fields = ("id",)
    list_filter = ("created_at", "updated_at")
