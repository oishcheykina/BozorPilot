from decimal import Decimal
from statistics import mean

from apps.core.models import EventSignal, ProductAnalytics


class AnalyticsService:
    outlier_threshold = Decimal("0.35")

    def _filtered_prices(self, product):
        prices = list(product.prices.values_list("price", flat=True))
        if not prices:
            return []
        avg = Decimal(str(mean(prices)))
        filtered = [price for price in prices if abs(price - avg) / avg <= self.outlier_threshold]
        return filtered or prices

    def build_product_analytics(self, product):
        prices = self._filtered_prices(product)
        if not prices:
            return None
        avg = Decimal(str(mean(prices)))
        low = min(prices)
        high = max(prices)
        weighted = Decimal(str(sum(float(price) * 1.02 for price in prices) / len(prices)))
        fair_min = avg * Decimal("0.95")
        fair_max = avg * Decimal("1.05")
        volatility = float((high - low) / avg * 100)
        trend_score = min(100.0, 45.0 + volatility / 2)
        demand_score = min(100.0, 50.0 + product.seller_reliability / 2)
        summary = (
            f"Bozor bo'yicha o'rtacha narx {avg:,.0f} UZS. "
            f"Adolatli diapazon {fair_min:,.0f} - {fair_max:,.0f} UZS."
        )
        analytics, _ = ProductAnalytics.objects.update_or_create(
            product=product,
            defaults={
                "market_average": avg,
                "weighted_average": weighted,
                "low_price": low,
                "high_price": high,
                "fair_min": fair_min,
                "fair_max": fair_max,
                "volatility_score": volatility,
                "trend_score": trend_score,
                "demand_score": demand_score,
                "ai_summary": summary,
            },
        )
        return analytics

    def get_event_impact_score(self, category):
        signals = EventSignal.objects.filter(category=category)
        return round(sum(signal.impact_score for signal in signals), 1)
