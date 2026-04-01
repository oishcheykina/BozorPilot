def global_navigation(request):
    from apps.core.models import EventSignal, Marketplace, Product

    return {
        "marketplace_count": Marketplace.objects.count(),
        "product_count": Product.objects.count(),
        "signal_count": EventSignal.objects.count(),
    }
