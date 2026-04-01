from decimal import Decimal

from services.analytics_service import AnalyticsService


class RecommendationService:
    def __init__(self):
        self.analytics_service = AnalyticsService()

    def consumer_summary(self, product):
        analytics = product.analytics if hasattr(product, "analytics") else self.analytics_service.build_product_analytics(product)
        prices = list(product.prices.select_related("marketplace").order_by("price"))
        if not analytics or not prices:
            return None
        best = prices[0]
        label = "средняя цена"
        if best.price < analytics.fair_min:
            label = "выгодно"
        elif best.price > analytics.fair_max:
            label = "дорого"
        savings = max(Decimal("0"), analytics.market_average - best.price)
        return {
            "market_average": analytics.market_average,
            "low_price": analytics.low_price,
            "high_price": analytics.high_price,
            "label": label,
            "best_option": best,
            "explanation": analytics.ai_summary,
            "savings_estimate": savings,
        }

    def business_summary(self, business_product):
        analytics = business_product.product.analytics if hasattr(business_product.product, "analytics") else self.analytics_service.build_product_analytics(business_product.product)
        event_score = self.analytics_service.get_event_impact_score(business_product.product.category)
        recommended = analytics.market_average * Decimal("0.99")
        margin_zone = recommended - business_product.buying_price
        status = "underpriced" if business_product.selling_price < analytics.fair_min else "overpriced" if business_product.selling_price > analytics.fair_max else "competitive"
        demand = "strong" if analytics.demand_score > 75 else "balanced"
        return {
            "recommended_price": recommended,
            "probable_margin_zone": margin_zone,
            "competitor_position": status,
            "underpriced_or_overpriced": status,
            "demand_outlook": demand,
            "short_term_recommendation": "Narxni biroz moslab, aksiyaga tayyor turing." if event_score > 10 else "Marjani saqlagan holda benchmarkga yaqin turing.",
            "risk_notes": "Volatility moderate" if analytics.volatility_score < 10 else "Watch sudden importer-led moves",
            "suggested_action": "Increase" if business_product.selling_price < analytics.fair_min else "Hold",
            "event_impact_score": event_score,
            "market_average": analytics.market_average,
        }
