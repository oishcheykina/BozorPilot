import json
from decimal import Decimal, InvalidOperation
from statistics import mean
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from django.conf import settings

from apps.core.models import EventSignal, Marketplace, Product


class MarketDataService:
    """
    Reads local demo data and external product search results from
    BozorShopPrototype running on localhost:8001.
    """

    product_list_path = "/api/products/"
    seller_detail_path = "/api/sellers/{seller_id}/"

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
                pulse.append({"product": product.title, "avg_price": round(mean(prices), 2), "volatility": round((max(prices) - min(prices)) / max(prices) * 100, 1), "trend": "up" if len(prices) % 2 == 0 else "stable"})
        return {"products": pulse, "signals": signals}

    def get_chart_payload(self, product):
        prices = product.prices.order_by("captured_at")
        labels = [price.captured_at.strftime("%d %b") for price in prices]
        values = [float(price.price) for price in prices]
        return {"labels": labels, "values": values}

    def search_shop_products(self, query, filters=None, limit=12):
        filters = filters or {}
        query = (query or "").strip()
        payload = self._fetch_products(query, filters)
        if payload is None:
            return {"results": [], "source": self.product_list_path, "error": f"BozorShopPrototype bilan ulanib bo'lmadi. {settings.SHOP_API_BASE_URL} da service ishlab turganini tekshiring."}
        results = self._normalize_search_payload(payload, limit)
        results = self._apply_local_filters(results, filters)
        return {"results": results, "source": self.product_list_path, "error": None}

    def _fetch_products(self, query, filters):
        params = {}
        if query:
            params["search"] = query
        if filters.get("min_price") not in (None, ""):
            params["min_price"] = filters["min_price"]
        if filters.get("max_price") not in (None, ""):
            params["max_price"] = filters["max_price"]
        if filters.get("seller_reliability") not in (None, ""):
            params["min_rating"] = round(float(filters["seller_reliability"]) / 20, 2)
        url = f"{urljoin(settings.SHOP_API_BASE_URL, self.product_list_path)}?{urlencode(params, doseq=True)}"
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "BozorPilotAI/1.0"})
        try:
            with urlopen(request, timeout=4) as response:
                raw = response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError, ValueError):
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def _normalize_search_payload(self, payload, limit):
        items = payload if isinstance(payload, list) else payload.get("results") or [] if isinstance(payload, dict) else []
        normalized = []
        for item in items[:limit]:
            if not isinstance(item, dict):
                continue
            price = self._to_decimal(item.get("price") or 0)
            market_average = self._to_decimal(item.get("avg_price") or price)
            product_id = item.get("id")
            seller_meta = self._fetch_seller_meta(item.get("seller"))
            normalized.append({
                "title": item.get("name") or "Unknown product",
                "brand": item.get("brand_name") or "Unknown",
                "model": item.get("model_name") or item.get("model") or "",
                "category": item.get("category_name") or "Marketplace item",
                "description": item.get("description") or "",
                "image_url": item.get("image_url") or "",
                "current_price": price,
                "original_price": price,
                "market_average": market_average,
                "low_price": self._to_decimal(item.get("min_price") or price),
                "high_price": self._to_decimal(item.get("max_price") or price),
                "platform": item.get("shop_name") or "BozorShopPrototype",
                "location": seller_meta["location"] or item.get("location") or "Uzbekistan",
                "seller_reliability": seller_meta["seller_reliability"],
                "detail_url": urljoin(settings.SHOP_API_BASE_URL, f"/api/products/{product_id}/") if product_id else "",
                "label": self._price_label(price, market_average),
            })
        return normalized

    def _fetch_seller_meta(self, seller_id):
        if not seller_id:
            return {"location": "", "seller_reliability": 80}
        url = urljoin(settings.SHOP_API_BASE_URL, self.seller_detail_path.format(seller_id=seller_id))
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "BozorPilotAI/1.0"})
        try:
            with urlopen(request, timeout=4) as response:
                raw = response.read().decode("utf-8")
            payload = json.loads(raw)
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
            return {"location": "", "seller_reliability": 80}
        rating = float(payload.get("rating") or 4)
        return {"location": payload.get("location") or "", "seller_reliability": int((rating / 5) * 100)}

    def _apply_local_filters(self, results, filters):
        brand = (filters.get("brand") or "").strip().lower()
        category = (filters.get("category") or "").strip().lower()
        location = (filters.get("location") or "").strip().lower()
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")
        seller_reliability = filters.get("seller_reliability")
        filtered = []
        for item in results:
            if brand and brand not in item["brand"].lower():
                continue
            if category and category not in item["category"].lower():
                continue
            if location and location not in item["location"].lower():
                continue
            if min_price not in (None, "") and item["current_price"] < Decimal(str(min_price)):
                continue
            if max_price not in (None, "") and item["current_price"] > Decimal(str(max_price)):
                continue
            if seller_reliability not in (None, "") and item["seller_reliability"] < int(seller_reliability):
                continue
            filtered.append(item)
        return filtered

    def _to_decimal(self, value):
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")

    def _price_label(self, price, market_average):
        if price <= market_average * Decimal("0.95"):
            return "выгодно"
        if price >= market_average * Decimal("1.05"):
            return "дорого"
        return "средняя цена"
