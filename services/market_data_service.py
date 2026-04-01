from statistics import mean

from apps.core.models import EventSignal, Marketplace, Product


class MarketDataService:
    """
    Supports mock/demo mode now and is structured for future marketplace APIs.
    """

    def get_featured_products(self, limit=6):
        return Product.objects.filter(is_active=True).select_related("category")[:limit]

    def get_marketplaces(self):
        return Marketplace.objects.all()

    def get_latest_prices(self, product):
        return product.prices.select_related("marketplace").order_by("price", "-captured_at")

    def get_market_pulse(self):
        products = Product.objects.filter(is_active=True)[:4]
        signals = EventSignal.objects.order_by("-created_at")[:4]
        pulse = []
        for product in products:
            prices = list(product.prices.values_list("price", flat=True))
            if prices:
                pulse.append(
                    {
                        "product": product.title,
                        "avg_price": round(mean(prices), 2),
                        "volatility": round((max(prices) - min(prices)) / max(prices) * 100, 1),
                        "trend": "up" if len(prices) % 2 == 0 else "stable",
                    }
                )
        return {"products": pulse, "signals": signals}

    def get_chart_payload(self, product):
        prices = product.prices.order_by("captured_at")
        labels = [price.captured_at.strftime("%d %b") for price in prices]
        values = [float(price.price) for price in prices]
        return {"labels": labels, "values": values}
