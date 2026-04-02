from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .filters import ProductFilter
from .models import Brand, Category, Product, Seller, Shop
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductSerializer,
    SellerSerializer,
    ShopSerializer,
)


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.select_related('shop').all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['shop']
    search_fields = ['name', 'shop__name']
    ordering_fields = ['id', 'name']


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.select_related('shop').all()
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['shop']
    search_fields = ['name', 'shop__name']
    ordering_fields = ['id', 'name']


class SellerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Seller.objects.select_related('shop').all()
    serializer_class = SellerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['shop', 'location']
    search_fields = ['name', 'location', 'shop__name']
    ordering_fields = ['id', 'name', 'rating']


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related(
        'shop',
        'category',
        'brand',
        'seller',
    ).all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = [
        'name',
        'description',
        'shop__name',
        'category__name',
        'brand__name',
        'seller__name',
    ]
    ordering_fields = ['id', 'name', 'price', 'stock', 'created_at']
