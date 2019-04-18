from django.db import models
from django.conf import settings

# Create your models here.
class FrameModel(models.Model):
    name = models.CharField(max_length=255)
    load = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )


class Sim(models.Model):
    load = models.CharField(max_length=255)
    consoleOutput = models.CharField(max_length=255)
    graphOutput = models.CharField(max_length=255)
    plot3DPath = models.CharField(max_length=255)
    numGens = models.IntegerField(null=True)
    numSeeds = models.IntegerField(null=True)
    numChildrenPerSeed = models.IntegerField(null=True)
    maxNumRandNodes = models.IntegerField(null=True)
    maxNumRandTubes = models.IntegerField(null=True)
    weightMultiplier = models.FloatField(null=True)
    maxDispOfAnyTargetNode = models.FloatField(null=True)
    maxAvgDisp = models.FloatField(null=True)
    maxWeight = models.FloatField(null=True)
    started = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(null=True)
    runBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    fromModel = models.ForeignKey(
        'FrameModel',
        on_delete=models.CASCADE,
        null=True,
    )
