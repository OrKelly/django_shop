import stripe
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.utils.dateformat import format
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from braces.views import GroupRequiredMixin

from shop.models import Product
from payment.models import Order
from shop.models import Category

from .tasks import send_cancel_order_mail, mail_sending
from .forms import ProductChangeForm, MailSendingForm, CancelOrderForm, PromoCreatingForm


def group_required(*group_names):
    """Проверяет группы пользователя, и если они входят в требуемые - пропускает его"""

    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups, login_url='403')


class ProductListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Product
    context_object_name = 'products'
    paginate_by = 15
    group_required = [u'staff', ]

    def get_template_names(self):
        if self.request.htmx:
            return "staffshop/components/product_list.html"
        return "staffshop/products.html"


class ProductAddView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Product
    group_required = [u'staff', ]
    success_url = reverse_lazy('staff:products')
    form_class = ProductChangeForm
    template_name = 'staffshop/product_change.html'


def product_detail_view(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category'), slug=slug)
    context = {'product': product}
    return render(request, 'staffshop/product_detail.html', context)


def search_products(request):
    query = request.GET.get('q')
    products = Product.objects.filter(title__icontains=query).distinct()
    context = {'products': products}
    if not query or not products:
        messages.error(
            request, 'К сожалению, нам ничего не удалось найти по вашему запросу!'
        )
        return redirect('staff:products')
    return render(request, 'staffshop/search_products.html', context)


class ActiveOrderListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    context_object_name = 'orders'
    group_required = [u'staff', ]
    template_name = 'stafforders/orders.html'
    extra_context = {'title': 'Активные заказы'}

    def get_queryset(self):
        return Order.objects.filter(status__in=['Оплачен', 'Подтвержден', 'В пути'])


class CompletedOrderListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    context_object_name = 'orders'
    group_required = [u'staff', ]
    template_name = 'stafforders/orders.html'
    extra_context = {'title': 'Завершенные заказы'}

    def get_queryset(self):
        return Order.objects.filter(status__in=['Доставлен', 'Отменен'])


@group_required('staff')
def order_detail(request, order_id):
    order = Order.objects.filter(pk=order_id).first()
    if request.method == 'POST':  # изменяем статус заказа
        if order.status == 'Оплачен':
            order.status = 'Подтвержден'
        elif order.status == 'Подтвержден':
            order.status = 'В пути'
        elif order.status == 'В пути':
            order.status = 'Доставлен'
            order.complete_order()
        else:
            messages.error(
                request, 'Заказ не оплачен, подтвердить можно только после оплаты!'
            )
        order.save()
    return render(request, 'stafforders/order_detail.html', {'order': order})


@group_required('staff')
def order_cancel(request, order_id):
    order = Order.objects.filter(pk=order_id).first()
    form = CancelOrderForm()
    if request.method == 'POST':
        form = CancelOrderForm(request.POST)
        if form.is_valid():
            order.status = 'Отменен'
            order.complete_order()
            order.cancel_reason = form.cleaned_data['title']
            order.save()
            title = form.cleaned_data['title']
            coupon = form.cleaned_data['send_coupon']
            send_cancel_order_mail.delay(order_id, title=title, coupon=coupon)
            return redirect('staff:order_detail', order_id=order_id)
    return render(request, 'stafforders/order_cancel.html', {'order': order, 'form': form})


@group_required('staff')
def change_product(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug)
    if request.method == 'POST':
        form = ProductChangeForm(request.POST, instance=product)
        form.save()
        return redirect('staff:products')
    else:
        form = ProductChangeForm(instance=product)

    return render(request, 'staffshop/product_change.html', {'form': form})


@group_required('staff')
def delete_product(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug)
    if request.method == 'POST':
        product.delete()
        return redirect('staff:products')
    return render(request, 'staffshop/product_delete.html', {'product': product})


@group_required('staff')
def email_sending(request):
    form = MailSendingForm()
    if request.method == 'POST':
        form = MailSendingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            mail = form.cleaned_data['mail']
            mail_sending.delay(title, mail)
            messages.success(request,
                             'Рассылка успешно отправлена! Скоро получатели получат её!')
    return render(request, 'mailing/mail_sender.html', {'form': form})


@group_required('staff')
def list_promo(request):
    promos = stripe.PromotionCode.list()
    return render(request, 'promo/promos.html', {'promos': promos})


@group_required('staff')
def add_promo(request):
    form = PromoCreatingForm()
    User = get_user_model()
    if request.method == 'POST':
        form = PromoCreatingForm(request.POST)
        if form.is_valid():
            date = format(form.cleaned_data['expires_on'], 'U')  # конвертируем дату в unix формат
            coupon = stripe.PromotionCode.create(
                coupon=f'sale{form.cleaned_data["sale"]}',
                expires_at=format(form.cleaned_data['expires_on'], 'U')
            )
            if form.cleaned_data['send_email']: # если выбрано "отправить клиентам письмо"
                if form.cleaned_data['title'] and form.cleaned_data['mail']:
                    title = form.cleaned_data['title']
                    mail = form.cleaned_data['mail'].format(sale=coupon.coupon.percent_off, promo=coupon.code)
                    mail_sending.delay(title, mail)
                else:
                    messages.error(request, 'Заполните данные для письма!')
            messages.success(request, f'Промокод {coupon.code} успешно создан!')
    return render(request, 'promo/promo_form.html', {'form': form})


@group_required('staff')
def set_promo_mail_template(request):
    # шаблон для отправки письма с промокодом клиентам
    if request.method == 'GET':
        title = 'НОВАЯ АКЦИЯ! УСПЕЙ, ПОКА ВСЕ НЕ РАЗОБРАЛИ!'
        mail = 'У нас есть персональный подарок для тебя! Активируй наш новый промокод и получи скидку - {sale}. ' \
               'Используй промокод {promo} при следующей покупке!'

        response = JsonResponse({'title': title, 'mail': mail})
        return response


@group_required('staff')
def deactivate_promo(request, coupon_id):
    coupon = stripe.PromotionCode.retrieve(coupon_id)
    coupon.active = False
    coupon.save()
    messages.success(request, f'Промокод "{coupon.code}" успешно деактивирован!')
    return redirect('staff:promo')
