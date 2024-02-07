from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

import stripe

from payment.models import Order

User = get_user_model()


@shared_task()
def send_cancel_order_mail(order_id, title, coupon):
    # sending cancel order mail to the user
    order = Order.objects.get(id=order_id)
    subject = f'Заказ {order.id} отменен'
    receipent_email = order.user.email

    if coupon:  # if choosen 'send promo'
        coupon = stripe.PromotionCode.create(
            coupon='BLVPs4rB',
            max_redemptions=1,
        )
        message = f'К сожалению, нам пришлось отменить ваш заказ. Причина:{title}' \
                  f'В качестве извинения присылаем вам купон на скидку для следующего заказа. Вот он: {coupon.code}'
    else:
        message = f'К сожалению, нам пришлось отменить ваш заказ. Причина:{title}. Извините, что ' \
                  f'так получилось'

    mail_to_sender = send_mail(
        subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[receipent_email],
    )
    return mail_to_sender


@shared_task()
def mail_sending(title, mail):
    # email sending to the all users
    users = User.objects.all()
    subject = title
    message = mail
    receipent_email = []
    for user in User.objects.all():
        receipent_email.append(user.email)
    mail_to_sender = send_mail(
        subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[receipent_email],
    )
    return mail_to_sender
