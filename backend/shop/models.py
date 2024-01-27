import random
import string

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.text import slugify
from django.urls import reverse



def rand_slug():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(3))


class Category(models.Model):
    name = models.CharField('Категория',max_length=250, db_index=True)
    parent = models.ForeignKey('self',verbose_name='Родительская категория', on_delete=models.CASCADE,
                               related_name='children', blank=True, null=True)
    slug = models.SlugField('URL', max_length=250, unique=True, null=False, editable=True)
    created_at = models.DateTimeField('Дата создания',auto_now_add=True)

    class Meta:
        unique_together = (['slug', 'parent'])
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """
        Returns a string representation of the object.
        """
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' > '.join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(rand_slug() + self.name)
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category-list', kwargs={'slug': self.slug})


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField('Название', max_length=250)
    brand = models.CharField('Бренд', max_length=250)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=7, decimal_places=2, default=999.99)
    image = models.ImageField('Изображение', upload_to='images/products/%Y/%m/%d', default='images/products/default.jpg')
    available = models.IntegerField('Наличие', default=10, blank=False, null=True)
    slug = models.SlugField('URL', max_length=250)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    rating = models.DecimalField('Рейтинг', null=True, blank=True, max_digits=3, decimal_places=2)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_rating(self):
        count = self.reviews.count()
        if count > 0:
            sum = int(list(self.reviews.aggregate(Sum('rating')).values())[0])
            self.rating = round(float(sum/count),2)
            return self.rating

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(rand_slug() + self.title)
        super(Product, self).save(*args, **kwargs)

    def lower_available(self, quantity):
        self.available -= quantity
        return self.available

    def get_absolute_url(self):
        return reverse("shop:product-detail", args=[str(self.slug)])

    def get_discounted_price(self):
        """
        Calculates the discounted price based on the product's price and discount.

        Returns:
            decimal.Decimal: The discounted price.
        """
        discounted_price = self.price - (self.price * self.discount / 100)
        return round(discounted_price, 2)

    @property
    def full_image_url(self):
        """
        Returns:
            str: The full image URL.
        """
        return self.image.url if self.image else ''


class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(available__gt=0)

class ProductProxy(Product):

    objects = ProductManager()
    class Meta:
        proxy = True
