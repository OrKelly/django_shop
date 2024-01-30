from django import forms

from shop.models import Product

class ProductChangeForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['rating', 'slug', 'created_at', 'updated_at']

