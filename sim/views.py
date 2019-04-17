from django.shortcuts import render, redirect
from sim.models import *
from django.views.decorators.csrf import csrf_exempt
from sim.geneticOptimizer import geneticOptimizer

def main(request):
    sim = Sim.objects.get(pk=1)
    consOutPath = sim.consoleOutput
    consOutFile = open('sim/static/results/'+consOutPath, 'r')
    consOut = consOutFile.read()

    graphsPath = sim.graphOutput
    graphsFile = open('sim/static/results/'+graphsPath, 'r')
    graphs = graphsFile.read()

    plot3DPath = "results/" + sim.plot3DPath
    args = {'consOut': consOut, 'graphs': graphs, 'plot3DPath': plot3DPath}
    return render(request, 'sim/mostRecentSim.html', args)

def load(request):
    models = FrameModel.objects.all()
    args = {'models': models}
    return render(request, 'sim/load.html', args)

def loaded(request, id):
    model = FrameModel.objects.get(pk=id)
    args = {'id': id}
    return render(request, 'sim/loaded.html', args)

@csrf_exempt #You need to get rid of this eventually
def run(request, id):

    sim = Sim.objects.get(pk=id)
    sim.numGens = int(request.POST.get('numGens'))
    sim.numSeeds = int(request.POST.get('numSeeds'))
    sim.numChildrenPerSeed = int(request.POST.get('numChildrenPerSeed'))
    sim.maxNumRandNodes = int(request.POST.get('maxNumRandNodes'))
    sim.maxNumRandTubes = int(request.POST.get('maxNumRandTubes'))
    sim.weightMultiplier = float(request.POST.get('weightMultiplier'))
    sim.maxDispOfAnyTargetNode = float(request.POST.get('maxDispOfAnyTargetNode'))
    sim.maxAvgDisp = float(request.POST.get('maxAvgDisp'))
    sim.maxWeight = float(request.POST.get('maxWeight'))
    sim.save()

    args = { 'id': id }
    return render(request, 'sim/run.html', args)