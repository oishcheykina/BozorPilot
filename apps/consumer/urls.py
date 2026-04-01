from django.urls import path

from apps.consumer import views

app_name = "consumer"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("search/", views.search, name="search"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("favorites/", views.favorites, name="favorites"),
    path("profile/", views.profile, name="profile"),
    path("favorite/<slug:slug>/", views.toggle_favorite, name="toggle_favorite"),
]
