from django import forms

from .models import ShippingAddress


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'email', 'country','city', 'street_address', 'apartment_address','index']
        exclude = ['user']
        labels = {
            'full_name': 'ФИО',
            'email': 'Электронная почта',
            'country': 'Страна',
            'city': 'Город',
            'street_address': 'Улица',
            'apartment_address': 'Дом',
            'index': 'Почтовый индекс',
        }