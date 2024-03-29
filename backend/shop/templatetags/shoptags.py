from django import template

from shop.models import ProductProxy

register = template.Library()


@register.inclusion_tag('shop/components/product_most_rated.html')
def get_most_rated_products():
    """Returns 10 high rated products"""
    products = ProductProxy.objects.filter(rating__gte=0).order_by('-rating')[:10]
    return {'prods': products}


@register.inclusion_tag('shop/components/product_sale.html')
def get_sale_products():
    """Returns 10 products with sale"""
    products = ProductProxy.objects.filter(discount__gte=10).order_by('-discount')[:10]
    return {'prods': products}
