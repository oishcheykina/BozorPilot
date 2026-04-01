from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.core.forms import BusinessProductForm
from apps.core.models import BusinessProduct, EventSignal
from services.market_data_service import MarketDataService
from services.recommendation_service import RecommendationService


market_service = MarketDataService()
recommendation_service = RecommendationService()


def business_nav(active):
    return [
        {"label": "Dashboard", "url": "/business/", "active": active == "dashboard"},
        {"label": "Products", "url": "/business/products/", "active": active == "products"},
        {"label": "Analytics", "url": "/business/analytics/", "active": active == "analytics"},
        {"label": "Insights", "url": "/business/insights/", "active": active == "insights"},
        {"label": "Alerts", "url": "/business/alerts/", "active": active == "alerts"},
        {"label": "Settings", "url": "/business/profile/", "active": active == "profile"},
    ]


@login_required
def dashboard(request):
    items = BusinessProduct.objects.filter(user=request.user).select_related("product", "category")
    summaries = [(item, recommendation_service.business_summary(item)) for item in items]
    overpriced = sum(1 for _, summary in summaries if summary["underpriced_or_overpriced"] == "overpriced")
    underpriced = sum(1 for _, summary in summaries if summary["underpriced_or_overpriced"] == "underpriced")
    avg_margin = round(sum(float(summary["probable_margin_zone"]) for _, summary in summaries) / len(summaries), 1) if summaries else 0
    context = {
        "items": summaries,
        "market_pulse": market_service.get_market_pulse(),
        "alerts": EventSignal.objects.order_by("-created_at")[:5],
        "nav_items": business_nav("dashboard"),
        "dashboard_eyebrow": "Business pricing intelligence",
        "dashboard_title": "SaaS-style control room for portfolio pricing",
        "dashboard_description": "Monitor margins, opportunities, risk alerts, and benchmark positioning in one view.",
        "kpis": {
            "tracked": items.count(),
            "avg_margin": avg_margin,
            "overpriced": overpriced,
            "underpriced": underpriced,
            "opportunities": max(1, underpriced + 2 if items else 3),
            "risks": EventSignal.objects.count(),
        },
    }
    return render(request, "business/dashboard.html", context)


@login_required
def products(request):
    if request.method == "POST":
        form = BusinessProductForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect("business:products")
    else:
        form = BusinessProductForm()
    items = BusinessProduct.objects.filter(user=request.user).select_related("product")
    return render(
        request,
        "business/products.html",
        {
            "form": form,
            "items": items,
            "nav_items": business_nav("products"),
            "dashboard_eyebrow": "Portfolio management",
            "dashboard_title": "Tracked products",
            "dashboard_description": "Add products, buying price, selling price, stock, and notes for AI analysis.",
        },
    )


@login_required
def analytics(request):
    items = BusinessProduct.objects.filter(user=request.user).select_related("product")
    summaries = [(item, recommendation_service.business_summary(item)) for item in items]
    return render(
        request,
        "business/analytics.html",
        {
            "items": summaries,
            "market_pulse": market_service.get_market_pulse(),
            "nav_items": business_nav("analytics"),
            "dashboard_eyebrow": "Analytics studio",
            "dashboard_title": "Demand trend, volatility, and category dynamics",
            "dashboard_description": "Read market movement before you adjust price or inventory.",
        },
    )


@login_required
def insights(request):
    items = BusinessProduct.objects.filter(user=request.user).select_related("product")
    summaries = [(item, recommendation_service.business_summary(item)) for item in items]
    return render(
        request,
        "business/insights.html",
        {
            "items": summaries,
            "nav_items": business_nav("insights"),
            "dashboard_eyebrow": "AI Analyzer",
            "dashboard_title": "Structured pricing recommendations",
            "dashboard_description": "Deterministic advice today, ready for richer AI later.",
        },
    )


@login_required
def alerts(request):
    alerts_qs = EventSignal.objects.order_by("-created_at")
    return render(
        request,
        "business/alerts.html",
        {
            "alerts": alerts_qs,
            "nav_items": business_nav("alerts"),
            "dashboard_eyebrow": "Risk monitoring",
            "dashboard_title": "Alerts feed",
            "dashboard_description": "Stay ahead of event-driven pricing pressure and demand swings.",
        },
    )


@login_required
def profile(request):
    return render(
        request,
        "business/profile.html",
        {
            "nav_items": business_nav("profile"),
            "dashboard_eyebrow": "Workspace settings",
            "dashboard_title": "Business profile",
            "dashboard_description": "Company details and operating context for tailored recommendations.",
        },
    )
