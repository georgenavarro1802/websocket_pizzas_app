from django.urls import path

from .views import home, order_pizza, order


urlpatterns = [
    path('', home, name='home'),
    path('api/order', order_pizza, name='order_pizza'),
    path('<code>/', order, name='order')
]