from django.db import models

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from shop.models import Product

User = get_user_model()

class ShippingAddress(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True, null=True)
    index = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Адрес доставки"
        verbose_name_plural = "Адреса доставки"
        ordering = ['-id']

    def __str__(self):
        return "Адрес доставки" + " - " + self.full_name

class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(
                amount__gte=0), name='amount_gte_0'),
        ]

    def __str__(self):
        return "Заказ" + str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=True, null=True, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "Вещь" + str(self.id)
