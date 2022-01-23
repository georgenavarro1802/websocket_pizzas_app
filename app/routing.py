from django.urls import path

from app.consumers import OrderProgressConsumer


ws_pattern = [
    path('ws/pizza/<code>', OrderProgressConsumer.as_asgi()),
]

