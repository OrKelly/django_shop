# Generated by Django 4.2.9 on 2024-02-04 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0008_alter_order_coupon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='coupon',
        ),
    ]
