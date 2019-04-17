# chat/consumers.py
from asgiref.sync import async_to_sync
from django.shortcuts import redirect
from channels.generic.websocket import WebsocketConsumer
import json
from sim.geneticOptimizer import geneticOptimizer

class SimConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['id']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        self.runSim()

    def runSim(self):
        geneticOptimizer(self, 3, 5, 4, 2, 2, .0075, 70, 70, 70)

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
