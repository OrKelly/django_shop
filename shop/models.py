import random
import string

from django.db import models
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
    image = models.ImageField('Изображение', upload_to='products/products/%Y/%m/%d')
    available = models.BooleanField('Наличие', default=True)
    slug = models.SlugField('URL', max_length=250)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(rand_slug() + self.title)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:product-detail', kwargs={'slug': self.slug})


class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(available=True)

class ProductProxy(Product):

    objects = ProductManager()
    class Meta:
        proxy = True
