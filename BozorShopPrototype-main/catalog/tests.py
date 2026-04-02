from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Brand, Category, Product, Seller, Shop


class ProductApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.shop = Shop.objects.create(name='Bozor Shop')
        self.other_shop = Shop.objects.create(name='Another Shop')

        self.category = Category.objects.create(name='Phones', shop=self.shop)
        self.brand = Brand.objects.create(name='Samsung', shop=self.shop)
        self.seller = Seller.objects.create(
            name='Main Seller',
            rating=4.8,
            location='Tashkent',
            shop=self.shop,
        )
        self.other_category = Category.objects.create(name='Laptops', shop=self.other_shop)
        self.other_brand = Brand.objects.create(name='Lenovo', shop=self.other_shop)
        self.other_seller = Seller.objects.create(
            name='Other Seller',
            rating=4.2,
            location='Samarkand',
            shop=self.other_shop,
        )

        Product.objects.create(
            name='Galaxy S24',
            shop=self.shop,
            category=self.category,
            brand=self.brand,
            seller=self.seller,
            description='New',
            stock=10,
            price=Decimal('999.99'),
        )
        Product.objects.create(
            name='ThinkPad',
            shop=self.other_shop,
            category=self.other_category,
            brand=self.other_brand,
            seller=self.other_seller,
            description='Used',
            stock=3,
            price=Decimal('500.00'),
        )

    def test_product_list_can_be_filtered_by_shop(self):
        response = self.client.get('/api/products/', {'shop': self.shop.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Galaxy S24')

    def test_product_validation_rejects_foreign_relations_from_other_shop(self):
        product = Product(
            name='Broken Product',
            shop=self.shop,
            category=self.other_category,
            brand=self.brand,
            seller=self.seller,
            price=Decimal('10.00'),
            stock=1,
        )

        with self.assertRaises(ValidationError):
            product.full_clean()
