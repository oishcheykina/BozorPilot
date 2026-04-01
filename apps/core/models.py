from django.conf import settings
from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Role(TimeStampedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Profile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="profiles")
    preferred_language = models.CharField(max_length=8, default="uz")
    location = models.CharField(max_length=120, blank=True)
    company_type = models.CharField(max_length=120, blank=True)
    onboarding_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} profile"


class Marketplace(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    website_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    reliability_score = models.PositiveSmallIntegerField(default=80)
    coverage = models.CharField(max_length=120, blank=True)
    is_partner = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children")
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    brand = models.CharField(max_length=120)
    model_name = models.CharField(max_length=120, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    sku = models.CharField(max_length=64, blank=True)
    location = models.CharField(max_length=120, blank=True)
    seller_reliability = models.PositiveSmallIntegerField(default=80)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand}-{self.title}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductAlias(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="aliases")
    alias = models.CharField(max_length=255)
    source = models.CharField(max_length=120, default="manual")

    def __str__(self):
        return self.alias


class ProductPrice(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices")
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE, related_name="prices")
    title_snapshot = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="UZS")
    stock_status = models.CharField(max_length=64, default="in_stock")
    seller_name = models.CharField(max_length=120, blank=True)
    seller_reliability = models.PositiveSmallIntegerField(default=80)
    source_url = models.URLField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    captured_at = models.DateTimeField()

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.product} @ {self.marketplace}"


class ProductAnalytics(TimeStampedModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="analytics")
    market_average = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    weighted_average = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    low_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    high_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fair_min = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fair_max = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    volatility_score = models.FloatField(default=0)
    trend_score = models.FloatField(default=0)
    demand_score = models.FloatField(default=0)
    ai_summary = models.TextField(blank=True)

    def __str__(self):
        return f"Analytics for {self.product}"


class BusinessProduct(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="business_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="business_entries")
    buying_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.email} - {self.product.title}"


class BusinessInsight(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="business_insights")
    business_product = models.ForeignKey(BusinessProduct, on_delete=models.CASCADE, related_name="insights")
    recommended_price = models.DecimalField(max_digits=12, decimal_places=2)
    market_average = models.DecimalField(max_digits=12, decimal_places=2)
    competitor_position = models.CharField(max_length=64)
    risk_level = models.CharField(max_length=32)
    opportunity_level = models.CharField(max_length=32)
    demand_signal = models.CharField(max_length=64)
    trend_summary = models.TextField()
    pricing_advice = models.TextField()
    event_impact_score = models.FloatField(default=0)

    def __str__(self):
        return f"Insight for {self.business_product.product.title}"


class SearchHistory(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="searches")
    query = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    results_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.query


class FavoriteProduct(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorited_by")
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.email} -> {self.product.title}"


class EventSignal(TimeStampedModel):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    impact_level = models.CharField(max_length=32, default="medium")
    impact_score = models.FloatField(default=0)
    signal_type = models.CharField(max_length=64, default="market")
    summary = models.TextField()
    starts_at = models.DateField(null=True, blank=True)
    ends_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class PartnerClick(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="partner_clicks")
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE, related_name="partner_clicks")
    target_url = models.URLField()
    referrer_page = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.product} -> {self.marketplace}"


class APIImportLog(TimeStampedModel):
    source_name = models.CharField(max_length=120)
    mode = models.CharField(max_length=32, default="mock")
    status = models.CharField(max_length=32, default="success")
    imported_records = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    payload_sample = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.source_name} ({self.mode})"
