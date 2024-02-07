import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Order, OrderItem, ShippingAddress


class ShippingAdressAdmin(admin.ModelAdmin):
    list_display = ('full_name_bold', 'user', 'email', 'country', 'city', 'index')
    empty_value_display = "-empty-"
    list_display_links = ('full_name_bold',)
    list_filter = ('user', 'country', 'city')

    @admin.display(description="Full Name", empty_value="Noname")
    def full_name_bold(self, obj):
        return format_html("<b style='font-weight: bold;'>{}</b>", obj.full_name)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['price', 'product', "quantity", "user"]
        return super().get_readonly_fields(request, obj)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'shipping_address', 'amount',
                    'created', 'updated', 'paid', 'discount']
    list_filter = ['paid', 'updated', 'created', ]
    inlines = [OrderItemInline]
    list_per_page = 15
    list_display_links = ['id', 'user']


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress, ShippingAdressAdmin)

