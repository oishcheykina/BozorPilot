import json

from django.contrib.auth.decorators import login_required
from django.db.models import Min
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.forms import ProductSearchForm
from apps.core.models import FavoriteProduct, Product, SearchHistory
from services.analytics_service import AnalyticsService
from services.ai_product_selection_service import AIProductSelectionService
from services.market_data_service import MarketDataService
from services.recommendation_service import RecommendationService


analytics_service = AnalyticsService()
ai_product_selection_service = AIProductSelectionService()
market_service = MarketDataService()
recommendation_service = RecommendationService()


def consumer_nav(active):
    return [
        {"label": "Dashboard", "url": "/consumer/", "active": active == "dashboard"},
        {"label": "Search", "url": "/consumer/search/", "active": active == "search"},
        {"label": "Favorites", "url": "/consumer/favorites/", "active": active == "favorites"},
        {"label": "Profile", "url": "/consumer/profile/", "active": active == "profile"},
    ]


@login_required
def dashboard(request):
    featured = Product.objects.filter(is_active=True).select_related("category")[:6]
    favorites = FavoriteProduct.objects.filter(user=request.user).select_related("product")[:4]
    searches = SearchHistory.objects.filter(user=request.user).order_by("-created_at")[:5]
    pulse = market_service.get_market_pulse()
    return render(request, "consumer/dashboard.html", {"featured": featured, "favorites": favorites, "searches": searches, "market_pulse": pulse, "nav_items": consumer_nav("dashboard"), "dashboard_eyebrow": "Consumer savings assistant", "dashboard_title": "Simple and fast price comparison for everyday buying", "dashboard_description": "Search Uzbek market products, compare marketplace prices, and save the best offers."})


@login_required
def search(request):
    form = ProductSearchForm(request.GET or None)
    cards = []
    ai_pick = None
    external_error = None
    q = ""
    has_external_query = False
    use_ai = request.GET.get("use_ai") == "1"

    if form.is_valid():
        q = (form.cleaned_data.get("q") or "").strip()
        brand = form.cleaned_data.get("brand")
        category = form.cleaned_data.get("category")
        location = form.cleaned_data.get("location")
        min_price = form.cleaned_data.get("min_price")
        max_price = form.cleaned_data.get("max_price")
        seller_reliability = form.cleaned_data.get("seller_reliability")
        has_external_query = any(value not in (None, "", []) for value in [q, brand, category, location, min_price, max_price, seller_reliability])

        if has_external_query:
            external_search = market_service.search_shop_products(q, filters={"brand": brand, "category": category, "location": location, "min_price": min_price, "max_price": max_price, "seller_reliability": seller_reliability})
            cards = [{"external": True, "item": item} for item in external_search["results"]]
            external_error = external_search["error"]
            SearchHistory.objects.create(user=request.user, query=q or "filtered search", results_count=len(cards))

    if not has_external_query:
        queryset = Product.objects.filter(is_active=True).select_related("category")
        for product in queryset.distinct()[:12]:
            analytics = analytics_service.build_product_analytics(product)
            best_price = product.prices.aggregate(best=Min("price"))["best"]
            summary = recommendation_service.consumer_summary(product)
            cards.append({"external": False, "product": product, "analytics": analytics, "best_price": best_price, "summary": summary})

    if use_ai:
        ai_pick = ai_product_selection_service.pick_best(cards, query=q)
        if ai_pick and ai_pick.get("best_index") is not None:
            best_index = ai_pick["best_index"]
            if 0 <= best_index < len(cards):
                cards[best_index]["ai_selected"] = True

    return render(request, "consumer/search.html", {"form": form, "cards": cards, "ai_pick": ai_pick, "use_ai": use_ai, "external_error": external_error, "using_external_results": has_external_query, "nav_items": consumer_nav("search"), "dashboard_eyebrow": "Search intelligence", "dashboard_title": "Find fair prices in seconds", "dashboard_description": "Search and filters on this page are fetched from BozorShopPrototype on localhost:8001."})


@login_required
def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug)
    analytics = analytics_service.build_product_analytics(product)
    summary = recommendation_service.consumer_summary(product)
    prices = product.prices.select_related("marketplace").order_by("price")
    chart_data = json.dumps(market_service.get_chart_payload(product))
    return render(request, "consumer/product_detail.html", {"product": product, "analytics": analytics, "summary": summary, "prices": prices, "chart_data": chart_data, "nav_items": consumer_nav("search"), "dashboard_eyebrow": "Product intelligence", "dashboard_title": product.title, "dashboard_description": "Historical price trend, marketplace comparison, and AI analyzer summary."})


@login_required
def favorites(request):
    items = FavoriteProduct.objects.filter(user=request.user).select_related("product")
    return render(request, "consumer/favorites.html", {"items": items, "nav_items": consumer_nav("favorites"), "dashboard_eyebrow": "Saved shortlist", "dashboard_title": "Favorites", "dashboard_description": "Track products you want to monitor or buy later."})


@login_required
def profile(request):
    return render(request, "consumer/profile.html", {"nav_items": consumer_nav("profile"), "dashboard_eyebrow": "Account", "dashboard_title": "Profile", "dashboard_description": "Language, location, and consumer preferences."})


@login_required
def toggle_favorite(request, slug):
    product = get_object_or_404(Product, slug=slug)
    favorite, created = FavoriteProduct.objects.get_or_create(user=request.user, product=product)
    if not created:
        favorite.delete()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"saved": created})
    return redirect("consumer:favorites")
