# Generated by Django 4.2.9 on 2024-01-27 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_order_total_cost'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shippingaddress',
            options={'ordering': ['-id'], 'verbose_name': 'Адрес достави', 'verbose_name_plural': 'Адреса доставки'},
        ),
        migrations.RemoveField(
            model_name='order',
            name='total_cost',
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Не оплачен', 'Не оплачен'), ('Оплачен', 'Оплачен'), ('Подтвержден', 'Подтвержден'), ('В пути', 'В пути'), ('Доставлен', 'Доставлен'), ('Отменен', 'Отменен')], default='Не оплачен', max_length=100),
        ),
    ]
