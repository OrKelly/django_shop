from decimal import Decimal

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
    city = models.CharField(max_length=100, blank=True, null=True)
    index = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "Shipping address"
        verbose_name_plural = "Shipping addresses"
        ordering = ['-id']

    def __str__(self):
        return "Shipping address" + " - " + self.full_name

    @classmethod
    def create_default_shipping_address(cls, user):
        default_shipping_address = {"user": user, "full_name": "Noname", "email": "email@example.com",
                                    "street_address": "fill address", "apartment_address": "fill address",
                                    "country": ""}
        shipping_address = cls(**default_shipping_address)
        shipping_address.save()
        return shipping_address


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    discount = models.IntegerField(validators=[MaxValueValidator(0), MaxValueValidator(100)])

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(
                amount__gte=0), name='amount_gte_0'),
        ]

    def __str__(self):
        return "Order" + str(self.id)

    def get_total_cost_before_discount(self):
        return sum(item.get_cost() for item in self.items.all())

    @property
    def get_discount(self):
        if (total_cost := self.get_total_cost_before_discount()) and self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)

    def get_total_cost(self):
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount


class OrderItem(models.Model):
    price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.IntegerField(default=1)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=True, null=True, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "Item" + str(self.id)

    def get_cost(self):
        return self.price * self.quantity

    @property
    def total_cost(self):
        return self.price * self.quantity

    @classmethod
    def get_total_quantity_for_product(cls, product):
        return cls.objects.filter(product=product).aggregate(total_quantity=models.Sum('quantity'))[
            'total_quantity'] or 0

    @staticmethod
    def get_average_price():
        return OrderItem.objects.aggregate(average_price=models.Avg('price'))['average_price']
