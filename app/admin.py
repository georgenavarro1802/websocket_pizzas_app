from django.contrib import admin

from .models import Pizza, Order


@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image')
    search_fields = ('name', )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('code', 'pizza', 'user', 'amount', 'status', 'date')
    search_fields = ('code', 'pizza__name', 'user')
    list_filter = ('status', )
