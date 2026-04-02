from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')

    class Meta:
        ordering = ['name']
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name


class Category(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='categories', verbose_name='Магазин')
    name = models.CharField(max_length=255, verbose_name='Название категории')

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        constraints = [models.UniqueConstraint(fields=['shop', 'name'], name='unique_category_name_per_shop')]

    def __str__(self):
        return f'{self.name} ({self.shop.name})'


class Brand(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='brands', verbose_name='Магазин')
    name = models.CharField(max_length=255, verbose_name='Название бренда')

    class Meta:
        ordering = ['name']
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        constraints = [models.UniqueConstraint(fields=['shop', 'name'], name='unique_brand_name_per_shop')]

    def __str__(self):
        return f'{self.name} ({self.shop.name})'


class Seller(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='sellers', verbose_name='Магазин')
    name = models.CharField(max_length=255, verbose_name='Продавец/точка')
    rating = models.FloatField(verbose_name='Рейтинг', validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    location = models.CharField(max_length=255, verbose_name='Локация')

    class Meta:
        db_table = 'soldier'
        ordering = ['name']
        verbose_name = 'Продавец'
        verbose_name_plural = 'Продавцы'
        constraints = [models.UniqueConstraint(fields=['shop', 'name', 'location'], name='unique_seller_per_shop_location')]

    def __str__(self):
        return f'{self.name} ({self.location})'


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products', verbose_name='Магазин')
    name = models.CharField(max_length=255, verbose_name='Название товара')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='Категория')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products', verbose_name='Бренд')
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT, related_name='products', verbose_name='Продавец')
    image = models.FileField(upload_to='products/', blank=True, null=True, verbose_name='Фото товара')
    description = models.TextField(blank=True, verbose_name='Описание')
    stock = models.PositiveIntegerField(default=0, verbose_name='Остаток')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def clean(self):
        errors = {}
        if self.category_id and self.shop_id and self.category.shop_id != self.shop_id:
            errors['category'] = 'Категория должна принадлежать тому же магазину.'
        if self.brand_id and self.shop_id and self.brand.shop_id != self.shop_id:
            errors['brand'] = 'Бренд должен принадлежать тому же магазину.'
        if self.seller_id and self.shop_id and self.seller.shop_id != self.shop_id:
            errors['seller'] = 'Продавец должен принадлежать тому же магазину.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
