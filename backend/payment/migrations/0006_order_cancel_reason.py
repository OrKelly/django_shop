# Generated by Django 4.2.9 on 2024-01-31 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_order_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cancel_reason',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]