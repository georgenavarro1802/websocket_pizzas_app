import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer

from asgiref.sync import async_to_sync

from .models import Order


class OrderConsumer(AsyncWebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None

    async def connect(self):
        self.group_name = 'order_data'
        await self.channel_layer.groud_add(
            self.group_name, 
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, code):
        pass
    
    async def receive(self, text_data=None, bytes_data=None):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_order',
                'value': text_data
            }
        )
        
    async def send_order(self, event):
        print(event)
        await self.send(event['value'])
    
    
class OrderProgressConsumer(WebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.room_name = None

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['code']  # room_name == code
        self.room_group_name = 'order_%s' % self.room_name
        print(self.room_group_name)
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        order_details = Order.objects.get(code=self.room_name).get_details()
        
        self.accept()
        
        self.send(
            text_data=json.dumps({
                'payload': order_details
            })
        )
        
    def disconnect(self, code):
        # leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        
    def receive(self, text_data=None, bytes_data=None):
        # Send message to group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'order_status',
                'payload': text_data
            }
        )
        
    def order_status(self, event):
        print(event)
        data = json.loads(event['value'])
        # send message to websocket
        self.send(
            text_data=json.dumps({
                'payload': data
            })
        )
        