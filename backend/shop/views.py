from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.db.models import Q
from django.contrib import messages
from .models import Category, ProductProxy
from payment.models import OrderItem


class ProductListView(ListView):
    model = ProductProxy
    context_object_name = 'products'
    paginate_by = 15

    def get_template_names(self):
        if self.request.htmx:
            return "shop/components/product_list.html"
        return "shop/products.html"

class SalesListView(ListView):
    context_object_name = 'products'

    def get_queryset(self):
        sales = ProductProxy.objects.filter(discount__gt=0).order_by('-discount')
        return sales
    def get_template_names(self):
        if self.request.htmx:
            return "shop/components/product_list.html"
        return "shop/search_products.html"


def product_detail_view(request, slug):
    product = get_object_or_404(
        ProductProxy.objects.select_related('category'), slug=slug)
    try:
        buyer = OrderItem.objects.filter(Q(product=product) & Q(user=request.user))
        check_reviews = product.reviews.filter(created_by=request.user).exists()
    except TypeError:
        buyer, check_reviews = False, False
    finally:
        if request.method == 'POST':
            if request.user.is_authenticated:
                if check_reviews:
                    messages.error(
                        request, 'Вы уже оставляли отзыв на этот продукт')
                elif not buyer:
                    messages.error(
                        request, 'Вы можете оставить отзыв только на купленный продукт!')
                else:
                    rating = request.POST.get('rating', 3)
                    content = request.POST.get('content', '')
                    if content:
                        product.reviews.create(
                            rating=rating, content=content, created_by=request.user, product=product)
                        return redirect(request.path)
            else:
                messages.error(
                    request, 'Вы должны быть авторизованы, чтобы оставить отзыв')

        context = {'product': product, 'buyer':buyer, 'check_reviews':check_reviews}
    return render(request, 'shop/product_detail.html', context)


def categories_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = ProductProxy.objects.select_related('category').filter(category=category)
    context = {'category': category, 'products': products}
    return render(request, 'shop/category_list.html', context)


def search_products(request):
    query = request.GET.get('q')
    products = ProductProxy.objects.filter(title__icontains=query).distinct()
    context = {'products': products}
    if not query or not products:
        messages.error(
            request, 'К сожалению, нам ничего не удалось найти по вашему запросу!'
        )
        return redirect('shop:products')
    return render(request, 'shop/search_products.html', context)