# chat/consumers.py
from asgiref.sync import async_to_sync
from django.shortcuts import redirect
from channels.generic.websocket import WebsocketConsumer
import json
from sim.geneticOptimizer import geneticOptimizer
from sim.models import *
from FrameWebSim.settings import BASE_DIR
import os

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
        model = FrameModel.objects.get(pk=1)
        loadfile = model.createFrame
        createFrame = open(os.path.join(BASE_DIR, loadfile), 'r')

        sim = Sim.objects.get(pk=1)

        modelID = sim.fromModel_id
        loadfile = FrameModel.objects.get(pk=modelID).createFrame

        geneticOptimizer(self, createFrame, sim.numGens, sim.numSeeds, sim.numChildrenPerSeed,
                         sim.maxNumRandNodes, sim.maxNumRandTubes, sim.weightMultiplier,
                         sim.maxDispOfAnyTargetNode, sim.maxAvgDisp, sim.maxWeight)

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
