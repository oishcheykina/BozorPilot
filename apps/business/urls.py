from django.urls import path

from apps.business import views

app_name = "business"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("products/", views.products, name="products"),
    path("analytics/", views.analytics, name="analytics"),
    path("insights/", views.insights, name="insights"),
    path("alerts/", views.alerts, name="alerts"),
    path("profile/", views.profile, name="profile"),
]
