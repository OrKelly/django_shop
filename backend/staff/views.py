from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from braces.views import GroupRequiredMixin

from shop.models import Product
from payment.models import Order
from shop.models import Category

from .tasks import send_cancel_order
from .forms import ProductChangeForm


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups, login_url='403')
class ProductListView(LoginRequiredMixin,GroupRequiredMixin, ListView):
    model = Product
    context_object_name = 'products'
    paginate_by = 15
    group_required = [u'staff', ]


    def get_template_names(self):
        if self.request.htmx:
            return "staffshop/components/product_list.html"
        return "staffshop/products.html"


class CategoryListView(LoginRequiredMixin,GroupRequiredMixin, ListView):
    context_object_name = 'cats'
    group_required = [u'staff', ]
    template_name = 'staffcategory/cats.html'

    def get_queryset(self):
        return Category.objects.all()


class ActiveOrderListView(LoginRequiredMixin,GroupRequiredMixin, ListView):
    context_object_name = 'orders'
    group_required = [u'staff', ]
    template_name = 'stafforders/orders.html'

    def get_queryset(self):
        return Order.objects.filter(status__in=['Оплачен', 'Подтвержден', 'В пути'])


class CompletedOrderListView(LoginRequiredMixin,GroupRequiredMixin, ListView):
    context_object_name = 'orders'
    group_required = [u'staff', ]
    template_name = 'stafforders/orders.html'

    def get_queryset(self):
        return Order.objects.filter(status__in=['Доставлен', 'Отменен'])


@group_required('staff')
def order_detail(request, order_id):
    order = Order.objects.filter(pk=order_id).first()
    if request.method == 'POST':
        if order.status == 'Оплачен':
            order.status = 'Подтвержден'
        elif order.status == 'Подтвержден':
            order.status = 'В пути'
        elif order.status == 'В пути':
            order.status = 'Доставлен'
        else:
            messages.error(
                request, 'Заказ не оплачен, подтвердить можно только после оплаты!'
            )
        order.save()
    return render(request, 'stafforders/order_detail.html', {'order': order})

@group_required('staff')
def order_cancel(request, order_id):
    order = Order.objects.filter(pk=order_id).first()
    if request.method == 'POST':
        order.status = 'Отменен'
        order.save()
        send_cancel_order.delay(order_id)
        return redirect('staff:order_detail', order_id=order_id)
    return render(request, 'stafforders/order_cancel.html', {'order': order})


@group_required('staff')
def change_product(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug)
    if request.method == 'POST':
        form = ProductChangeForm(request.POST, instance=product)
        form.save()
        return redirect('staff:products')
    else:
        form = ProductChangeForm(instance=product)

    return render(request, 'staffshop/product_change.html', {'form':form})

@group_required('staff')
def delete_product(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug)
    if request.method == 'POST':
        product.delete()
        return redirect('staff:products')
    return render(request, 'staffshop/product_delete.html', {'product':product})



