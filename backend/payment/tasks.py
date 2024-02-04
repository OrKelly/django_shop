from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Order, ShippingAddress


@shared_task()
def send_order_confirmation(order_id):
    """Отправляем клиенту письмо о подтверждении и оформлении заказа"""

    order = Order.objects.get(id=order_id)
    subject = f'Подтверждение заказа №{order.id}'
    receipent_data = ShippingAddress.objects.get(user=order.user)
    receipent_email = receipent_data.email
    message = f'Ваш заказ был подтвержден.Номер заказа - {order.id}. Скоро мы начнем его сборку'

    mail_to_sender = send_mail(
        subject,message=message,from_email=settings.EMAIL_HOST_USER, recipient_list=[receipent_email],
    )
    return mail_to_sender