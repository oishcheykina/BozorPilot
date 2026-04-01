from datetime import timedelta
from decimal import Decimal
from random import randint

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import (
    APIImportLog,
    BusinessProduct,
    Category,
    EventSignal,
    Marketplace,
    Product,
    ProductAlias,
    ProductPrice,
    Profile,
    Role,
)
from services.analytics_service import AnalyticsService


class Command(BaseCommand):
    help = "Loads investor-demo seed data for Bozor Pilot AI."

    def handle(self, *args, **options):
        consumer_role, _ = Role.objects.get_or_create(code="consumer", defaults={"name": "Consumer"})
        business_role, _ = Role.objects.get_or_create(code="business", defaults={"name": "Business"})

        marketplaces = [
            ("Uzum Market", "https://uzum.uz", True, 89),
            ("OLX Uzbekistan", "https://olx.uz", False, 72),
            ("Asaxiy", "https://asaxiy.uz", True, 92),
            ("MediaPark", "https://mediapark.uz", False, 86),
        ]
        mp_objects = []
        for name, url, partner, score in marketplaces:
            mp, _ = Marketplace.objects.get_or_create(
                name=name,
                defaults={"website_url": url, "is_partner": partner, "reliability_score": score, "coverage": "Uzbekistan"},
            )
            mp_objects.append(mp)

        electronics, _ = Category.objects.get_or_create(name="Electronics", defaults={"description": "Consumer electronics"})
        smartphones, _ = Category.objects.get_or_create(name="Smartphones", parent=electronics)
        household, _ = Category.objects.get_or_create(name="Household Goods")
        appliances, _ = Category.objects.get_or_create(name="Household Electronics", parent=electronics)

        sample_products = [
            ("Samsung Galaxy A55 8/256", "Samsung", smartphones, "A55", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9"),
            ("iPhone 15 128GB", "Apple", smartphones, "15", "https://images.unsplash.com/photo-1592750475338-74b7b21085ab"),
            ("Redmi Note 13 Pro", "Xiaomi", smartphones, "Note 13 Pro", "https://images.unsplash.com/photo-1580910051074-3eb694886505"),
            ("Artel Smart TV 43", "Artel", appliances, "TV43", "https://images.unsplash.com/photo-1593784991095-a205069470b6"),
            ("Goodwell Air Fryer 5L", "Goodwell", household, "AF-5", "https://images.unsplash.com/photo-1585238342024-78d387f4a707"),
            ("Avalon Blender Pro", "Avalon", household, "BL-900", "https://images.unsplash.com/photo-1570222094114-d054a817e56b"),
        ]

        product_objects = []
        for title, brand, category, model_name, image_url in sample_products:
            product, _ = Product.objects.get_or_create(
                title=title,
                defaults={
                    "brand": brand,
                    "category": category,
                    "model_name": model_name,
                    "description": f"{title} uchun investor-demo yozuvi.",
                    "image_url": image_url,
                    "location": "Tashkent",
                    "seller_reliability": randint(78, 96),
                },
            )
            ProductAlias.objects.get_or_create(product=product, alias=title)
            product_objects.append(product)

        base_prices = {
            "Samsung Galaxy A55 8/256": [4499000, 4620000, 4715000, 4599000],
            "iPhone 15 128GB": [10250000, 10420000, 10380000, 10550000],
            "Redmi Note 13 Pro": [3780000, 3699000, 3890000, 3755000],
            "Artel Smart TV 43": [3199000, 3289000, 3350000, 3255000],
            "Goodwell Air Fryer 5L": [899000, 949000, 915000, 965000],
            "Avalon Blender Pro": [459000, 489000, 475000, 505000],
        }

        for product in product_objects:
            for index, marketplace in enumerate(mp_objects):
                for days_ago in range(6):
                    ProductPrice.objects.get_or_create(
                        product=product,
                        marketplace=marketplace,
                        title_snapshot=product.title,
                        price=Decimal(base_prices[product.title][index] + randint(-55000, 55000)),
                        original_price=Decimal(base_prices[product.title][index] + randint(15000, 95000)),
                        seller_reliability=randint(70, 97),
                        location="Tashkent",
                        source_url=marketplace.website_url,
                        captured_at=timezone.now() - timedelta(days=days_ago),
                    )

        signals = [
            ("Ramazon demand uplift", smartphones, "high", 12.5, "seasonal", "Smartphone promo traffic is rising before salary cycle."),
            ("Import logistics cooling", appliances, "medium", 7.0, "supply", "TV and appliance shipment timing improved across Tashkent."),
            ("Weekend promo compression", household, "medium", 6.5, "promotion", "Household goods margins may tighten due to marketplace promos."),
        ]
        for title, category, level, score, signal_type, summary in signals:
            EventSignal.objects.get_or_create(
                title=title,
                defaults={"category": category, "impact_level": level, "impact_score": score, "signal_type": signal_type, "summary": summary},
            )

        consumer_user, created = User.objects.get_or_create(
            email="consumer@bozorpilot.ai",
            defaults={"username": "consumer_demo", "first_name": "Dilnoza", "last_name": "Karimova"},
        )
        if created:
            consumer_user.set_password("demo12345")
            consumer_user.save()
        Profile.objects.get_or_create(user=consumer_user, defaults={"role": consumer_role, "location": "Tashkent", "onboarding_completed": True})

        business_user, created = User.objects.get_or_create(
            email="business@bozorpilot.ai",
            defaults={"username": "business_demo", "first_name": "Aziz", "last_name": "Rahimov", "company_name": "Toshkent Tech Supply"},
        )
        if created:
            business_user.set_password("demo12345")
            business_user.save()
        Profile.objects.get_or_create(
            user=business_user,
            defaults={"role": business_role, "location": "Tashkent", "company_type": "Retailer", "onboarding_completed": True},
        )

        for product in product_objects[:4]:
            BusinessProduct.objects.get_or_create(
                user=business_user,
                product=product,
                defaults={
                    "buying_price": Decimal(base_prices[product.title][0]) * Decimal("0.82"),
                    "selling_price": Decimal(base_prices[product.title][0]) * Decimal("1.01"),
                    "stock": randint(8, 42),
                    "category": product.category,
                    "notes": "Demo portfolio item",
                },
            )
            AnalyticsService().build_product_analytics(product)

        APIImportLog.objects.get_or_create(
            source_name="demo_seed",
            defaults={"mode": "mock", "status": "success", "imported_records": ProductPrice.objects.count(), "notes": "Initial investor demo seed"},
        )

        self.stdout.write(self.style.SUCCESS("Demo data loaded."))
