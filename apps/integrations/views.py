from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from services.soliq_service import SoliqClassifierService


@staff_member_required
def import_center(request):
    categories = SoliqClassifierService().fetch_categories()
    return render(request, "analytics_app/import_center.html", {"categories": categories})
