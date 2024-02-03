from django.contrib import admin

from .models import Review, Coupon


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'rating', 'content', 'created_by', 'created_at')

admin.site.register(Review)
admin.site.register(Coupon)