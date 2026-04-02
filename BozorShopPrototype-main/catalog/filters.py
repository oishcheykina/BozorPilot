import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_stock = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    max_stock = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='seller__rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='seller__rating', lookup_expr='lte')

    class Meta:
        model = Product
        fields = {
            'shop': ['exact'],
            'category': ['exact'],
            'brand': ['exact'],
            'seller': ['exact'],
        }
