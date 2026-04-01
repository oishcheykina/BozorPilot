from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apps.core.models import EventSignal, Product
from services.market_data_service import MarketDataService


@login_required
def market_pulse_json(request):
    data = MarketDataService().get_market_pulse()
    return JsonResponse(
        {
            "products": data["products"],
            "signals": [
                {"title": item.title, "impact_level": item.impact_level, "impact_score": item.impact_score}
                for item in data["signals"]
            ],
        }
    )


@login_required
def product_chart_json(request, slug):
    product = Product.objects.get(slug=slug)
    return JsonResponse(MarketDataService().get_chart_payload(product))


@login_required
def alerts_feed_json(request):
    alerts = EventSignal.objects.order_by("-created_at")[:8]
    return JsonResponse({"alerts": [{"title": a.title, "summary": a.summary, "level": a.impact_level} for a in alerts]})
