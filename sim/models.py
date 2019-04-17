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
    weightMultiplier = models.DecimalField(max_digits=15, decimal_places=10, null=True)
    maxDispOfAnyTargetNode = models.DecimalField(max_digits=15, decimal_places=10, null=True)
    maxAvgDisp = models.DecimalField(max_digits=15, decimal_places=10, null=True)
    maxWeight = models.DecimalField(max_digits=15, decimal_places=10, null=True)
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
