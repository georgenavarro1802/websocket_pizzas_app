import string
import json
import random

from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def random_string_generator():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6)).upper()


ORDER_STATUS_RECEIVED = 1
ORDER_STATUS_BAKING = 2
ORDER_STATUS_BAKED = 3
ORDER_STATUS_READY = 4
ORDER_STATUS_COMPLETE = 5

ORDER_STATUSES = (
    (ORDER_STATUS_RECEIVED, "Received"),
    (ORDER_STATUS_BAKING,   "Baking"),
    (ORDER_STATUS_BAKED,    "Baked"),
    (ORDER_STATUS_READY,    "Ready"),
    (ORDER_STATUS_COMPLETE, "Complete"),
)


def get_percentage_based_on_status(status):
    obj = {
        ORDER_STATUS_RECEIVED: 20,
        ORDER_STATUS_BAKING: 40,
        ORDER_STATUS_BAKED: 60,
        ORDER_STATUS_READY: 80,
        ORDER_STATUS_COMPLETE: 100
    }
    try:
        return obj[status]
    except:
        return obj[ORDER_STATUS_RECEIVED]


class Pizza(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=100)
    image = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Pizza'
        verbose_name_plural = 'Pizzas'


class Order(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100, blank=True)
    amount = models.IntegerField(default=100)
    status = models.PositiveSmallIntegerField(choices=ORDER_STATUSES, default=ORDER_STATUS_RECEIVED)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def get_details(self):

        return {
            'code': self.code,
            'amount': self.amount,
            'status': self.status,
            'status_name': self.get_status_display(),
            'date': self.date.__str__(),
            'progress': get_percentage_based_on_status(self.status)
        }

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = random_string_generator()
        super(Order, self).save(*args, **kwargs)


@receiver(post_save, sender=Order)
def order_status_handler(sender, instance, created, **kwargs):
    if not created:
        # Get channel layer
        channel_layer = get_channel_layer()

        data = {
            'code': instance.code,
            'amount': instance.amount,
            'status': instance.status,
            'status_name': instance.get_status_display(),
            'date': instance.date.__str__(),
            'progress': get_percentage_based_on_status(instance.status)
        }

        async_to_sync(channel_layer.group_send)(
            'order_%s' % instance.code,
            {
                'type': 'order_status',
                'value': json.dumps(data)
            }
        )
