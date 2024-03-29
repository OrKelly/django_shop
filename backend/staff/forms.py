from django import forms

from shop.models import Product


class ProductChangeForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['rating', 'slug', 'created_at', 'updated_at']


class CancelOrderForm(forms.Form):
    title = forms.CharField(label='Причина', max_length=100)
    send_coupon = forms.BooleanField(label='Отправить промокод клиенту', required=False)


class MailSendingForm(forms.Form):
    title = forms.CharField(label='Заголовок', max_length=100)
    mail = forms.CharField(label='Письмо', widget=forms.Textarea)


class PromoCreatingForm(forms.Form):
    CHOICES = (
        ('10', '10%'),
        ('20', '20%'),
        ('30', '30%'),
    )

    sale = forms.ChoiceField(label='Процент скидки', choices=CHOICES)
    expires_on = forms.DateField(label='Действует до',
                                 widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
                                 input_formats=["%Y-%m-%d"])
    send_email = forms.BooleanField(label='Разослать его клиентам?', required=False, initial=False)
    title = forms.CharField(label='Заголовок', max_length=100, required=False,
                            widget=forms.TextInput({'placeholder': 'Заголовок', 'display': 'none'}))
    mail = forms.CharField(label='''Письмо.
    {sale} - сумма скидки или её процент, {promo} - промокод.
    Заполнять их не нужно, значения подставятся сами. НЕ МЕНЯТЬ НАЗВАНИЯ ВНУТРИ {}''',
                           widget=forms.Textarea({'placeholder': 'Письмо', 'display': 'none'}), required=False)
