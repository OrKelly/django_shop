from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from shop.models import Product

from .utils import get_coupon_code_length, get_random_code

User = get_user_model()


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),
                                                          MaxValueValidator(5)])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_by} на товар: {self.product}"


class Coupon(models.Model):
    code_length = get_coupon_code_length()

    code = models.CharField(max_length=code_length, default=get_random_code, verbose_name="Купон", unique=True)
    discount = models.IntegerField('Размер скидки', validators=[MinValueValidator(5), MaxValueValidator(50)])
    available = models.BooleanField('Активность', default=True)
    created = models.DateTimeField(editable=False, verbose_name="Дата создания", auto_now=True)

    is_mass = models.BooleanField(default=False)

    def use_coupon(self):
        if not self.is_mass:
            self.available = False
            return self.available

class CouponManager(models.Manager):
    def get_queryset(self):
        return super(CouponManager, self).get_queryset().filter(available=True)

class CouponProxy(Coupon):

    objects = CouponManager()
    class Meta:
        proxy = True
