from django.urls import path

from apps.analytics_app import views

app_name = "analytics_app"

urlpatterns = [
    path("market-pulse/", views.market_pulse_json, name="market_pulse_json"),
    path("product-chart/<slug:slug>/", views.product_chart_json, name="product_chart_json"),
    path("alerts-feed/", views.alerts_feed_json, name="alerts_feed_json"),
]
