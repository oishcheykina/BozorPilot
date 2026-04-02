from rest_framework import serializers

from .models import Brand, Category, Product, Seller, Shop


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'shop', 'shop_name']


class BrandSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'shop', 'shop_name']


class SellerSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = Seller
        fields = ['id', 'name', 'rating', 'location', 'shop', 'shop_name']


class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'shop', 'shop_name', 'category', 'category_name', 'brand', 'brand_name', 'seller', 'seller_name', 'image', 'image_url', 'description', 'stock', 'price', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if not obj.image:
            return ''
        if request is not None:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
