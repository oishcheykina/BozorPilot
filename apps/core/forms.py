from django import forms

from apps.core.models import BusinessProduct


class ProductSearchForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    brand = forms.CharField(required=False)
    category = forms.CharField(required=False)
    location = forms.CharField(required=False)
    min_price = forms.DecimalField(required=False, decimal_places=2, max_digits=12)
    max_price = forms.DecimalField(required=False, decimal_places=2, max_digits=12)
    seller_reliability = forms.IntegerField(required=False, min_value=0, max_value=100)


class BusinessProductForm(forms.ModelForm):
    class Meta:
        model = BusinessProduct
        fields = ["product", "buying_price", "selling_price", "stock", "category", "notes"]
