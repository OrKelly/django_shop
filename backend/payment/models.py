from datetime import datetime
from decimal import Decimal

from django.db import models

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
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
        verbose_name = "Адрес достави"
        verbose_name_plural = "Адреса доставки"
        ordering = ['-id']

    def __str__(self):
        return "Адрес" + " - " + self.full_name

    @classmethod
    def create_default_shipping_address(cls, user):
        """Creating blank shipping address for new users"""
        default_shipping_address = {"user": user, "full_name": "Noname", "email": "email@example.com",
                                    "street_address": "fill address", "apartment_address": "fill address",
                                    "country": ""}
        shipping_address = cls(**default_shipping_address)
        shipping_address.save()
        return shipping_address


class Order(models.Model):
    #   order's statuses
    CHOICES = (
        ('Не оплачен', 'Не оплачен'),
        ('Оплачен', 'Оплачен'),
        ('Подтвержден', 'Подтвержден'),
        ('В пути', 'В пути'),
        ('Доставлен', 'Доставлен'),
        ('Отменен', 'Отменен'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    completed = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(max_length=100, choices=CHOICES, default='Не оплачен')
    cancel_reason = models.CharField(max_length=100, null=True, blank=True)

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
        return "Order" + str(self.id)

    def get_total_cost_before_discount(self):
        """Returns total cost before discount"""
        return sum(item.get_cost() for item in self.items.all())

    @property
    def get_discount(self):
        """Returns discount's summ"""
        if (total_cost := self.get_total_cost_before_discount()) and self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)

    def get_total_cost(self):
        """Returns total cost of orders"""
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount

    def complete_order(self):
        """Sets date of complete order"""
        self.completed = datetime.now()
        return self.completed


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
        return "Товар" + str(self.id)

    @property
    def total_cost(self):
        return self.price * self.quantity

    @classmethod
    def get_total_quantity_for_product(cls, product):
        """Returns total quantity of orders with this product"""
        return cls.objects.filter(product=product).aggregate(total_quantity=models.Sum('quantity'))[
            'total_quantity'] or 0

    @staticmethod
    def get_average_price():
        return OrderItem.objects.aggregate(average_price=models.Avg('price'))['average_price']
