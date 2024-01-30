from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from payment.models import Order


@shared_task()
def send_cancel_order(order_id):

    order = Order.objects.get(id=order_id)
    subject = f'Заказ {order.id} отменен'
    receipent_email = order.user.email
    message = f'К сожалению, нам пришлось отменить ваш заказ. Более подробную информацию вы можете получить, обравтившись к нам.'

    mail_to_sender = send_mail(
        subject,message=message,from_email=settings.EMAIL_HOST_USER, recipient_list=[receipent_email],
    )
    return mail_to_sender