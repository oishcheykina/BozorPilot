from rest_framework.routers import DefaultRouter

from .views import BrandViewSet, CategoryViewSet, ProductViewSet, SellerViewSet, ShopViewSet

router = DefaultRouter()
router.register('shops', ShopViewSet, basename='shop')
router.register('categories', CategoryViewSet, basename='category')
router.register('brands', BrandViewSet, basename='brand')
router.register('sellers', SellerViewSet, basename='seller')
router.register('products', ProductViewSet, basename='product')

urlpatterns = router.urls
