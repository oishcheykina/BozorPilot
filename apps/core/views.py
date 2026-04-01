from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.core.models import EventSignal
from services.market_data_service import MarketDataService


market_service = MarketDataService()


def landing(request):
    context = {
        "featured_products": market_service.get_featured_products(),
        "marketplaces": market_service.get_marketplaces(),
        "market_pulse": market_service.get_market_pulse(),
        "signals": EventSignal.objects.order_by("-created_at")[:3],
    }
    return render(request, "core/landing.html", context)


def pricing(request):
    return render(request, "core/pricing.html")


def about(request):
    return render(request, "core/about.html")


def faq(request):
    return render(request, "core/faq.html")


@login_required
def app_router(request):
    role = getattr(getattr(request.user, "profile", None), "role", None)
    if role and role.code == "business":
        return redirect("business:dashboard")
    return redirect("consumer:dashboard")
