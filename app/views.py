import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .models import Pizza, Order


def home(request):
    pizzas = Pizza.objects.all()
    orders = Order.objects.filter(user=request.user)
    context = {
        'pizzas': pizzas,
        'orders': orders
    }
    return render(request, 'index.html', context)


def order(request, code):
    try:
        order = Order.objects.get(code=code)
        return render(request, 'order.html', {'order': order})
    except Order.DoesNotExist:
        return redirect('/')


@csrf_exempt
def order_pizza(request):
    user = request.user
    data = json.loads(request.body)

    try:
        pizza = Pizza.objects.get(id=data.get('id'))
        Order.objects.create(user=user, pizza=pizza, amount=pizza.price)
        return JsonResponse({'message': 'Success'})

    except Pizza.DoesNotExist:
        return JsonResponse({'error': 'Something went wrong'})
