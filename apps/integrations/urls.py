from django.urls import path

from apps.integrations.views import import_center

app_name = "integrations"

urlpatterns = [path("import-center/", import_center, name="import_center")]
