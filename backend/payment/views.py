import uuid
import os

import stripe
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse

from cart.cart import Cart
from .forms import ShippingAddressForm
from .models import ShippingAddress, Order, OrderItem

from yookassa import Configuration, Payment
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

@login_required
def shipping(request):
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except ShippingAddress.DoesNotExist:
        shipping_address = None

    form = ShippingAddressForm(instance=shipping_address)

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            return redirect('account:dashboard')
    return render(request, 'payment/shipping.html', {'form':form})

@login_required
def checkout(request):
    if request.user.is_authenticated:
        shipping_address = get_object_or_404(ShippingAddress, user=request.user)
        if shipping_address:
            return render(request, 'payment/checkout.html', {'shipping_address': shipping_address})
    return render(request, 'payment/checkout.html')

@login_required
def complete_order(request):
    if request.method == 'POST':
        payment_type = request.POST.get('stripe-payment', 'yookassa-payment')

        name = request.POST.get('name')
        email = request.POST.get('email')
        street_address = request.POST.get('street_address')
        apartment_address = request.POST.get('apartment_address')
        country = request.POST.get('country')
        index = request.POST.get('index')
        cart = Cart(request)
        total_price = cart.get_total_price()

        shipping_address, _ = ShippingAddress.objects.get_or_create(
            user=request.user,
            defaults={
                'name': name,
                'email': email,
                'street_address': street_address,
                'apartment_address': apartment_address,
                'country': country,
                'index': index,
            })

        if payment_type == "stripe-payment":
            session_data = {
                'mode': 'payment',
                'success_url': request.build_absolute_uri(reverse('payment:payment-success')),
                'cancel_url': request.build_absolute_uri(reverse('payment:payment-failed')),
                'line_items': []
            }

            if request.user.is_authenticated:
                order = Order.objects.create(
                    user=request.user, shipping_address=shipping_address, amount=total_price)

                for item in cart:
                    OrderItem.objects.create(
                        order=order, product=item['product'], price=item['price'], quantity=item['qty'],
                        user=request.user)

                    session_data['line_items'].append({
                        'price_data': {
                            'unit_amount': int(item['price'] * Decimal(100)),
                            'currency': 'usd',
                            'product_data': {
                                'name': item['product']
                            },
                        },
                        'quantity': item['qty'],
                    })
                session_data['client_reference_id'] = order.id
                session = stripe.checkout.Session.create(**session_data)
                return redirect(session.url)
            else:
                return redirect('account:login')

        elif payment_type == "yookassa-payment":
                idempotence_key = uuid.uuid4()
                currency = 'RUB'
                description = 'Товары в корзине'
                payment = Payment.create({
                    "amount": {
                        "value": total_price,
                        "currency": currency
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": request.build_absolute_uri(reverse('payment:payment-success')),
                    },
                    "capture": True,
                    "test": True,
                    "description": description,
                }, idempotence_key)

                confirmation_url = payment.confirmation.confirmation_url

                if request.user.is_authenticated:
                    order = Order.objects.create(
                        user=request.user, shipping_address=shipping_address, amount=total_price)

                    for item in cart:
                        OrderItem.objects.create(
                            order=order, product=item['product'], price=item['price'], quantity=item['qty'],
                            user=request.user)

                    return redirect(confirmation_url)

                else:
                    return redirect('account:login')


def payment_success(request):
    for key in list(request.session.keys()):
        del request.session[key]
    return render(request, 'payment/payment-success.html')

def payment_failed(request):
    return render(request, 'payment/payment-fail.html')


# @staff_member_required
# def admin_order_pdf(request, order_id):
#     try:
#         order = Order.objects.select_related('user', 'shipping_address').get(id=order_id)
#     except Order.DoesNotExist:
#         raise Http404('Заказ не найден')
#     html = render_to_string('payment/order/pdf/pdf_invoice.html',
#                             {'order': order})
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
#     css_path = static('payment/css/pdf.css').lstrip('/')
#     # css_path = 'static/payment/css/pdf.css'
#     stylesheets = [weasyprint.CSS(css_path)]
#     weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
#     return response