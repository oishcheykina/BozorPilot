from django.urls import path

from apps.core import views

app_name = "core"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("pricing/", views.pricing, name="pricing"),
    path("about/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("app/", views.app_router, name="router"),
]
