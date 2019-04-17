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
    print(request.POST)
    numGens = int(request.POST.get('numGens'))
    numSeeds = int(request.POST.get('numSeeds'))
    numChildrenPerSeed = int(request.POST.get('numChildrenPerSeed'))
    maxNumRandNodes = int(request.POST.get('maxNumRandNodes'))
    maxNumRandTubes = int(request.POST.get('maxNumRandTubes'))
    weightMultiplier = float(request.POST.get('weightMultiplier'))
    maxDispOfAnyTargetNode = float(request.POST.get('maxDispOfAnyTargetNode'))
    maxAvgDisp = float(request.POST.get('maxAvgDisp'))
    maxWeight = float(request.POST.get('maxWeight'))
    geneticOptimizer(numGens, numSeeds, numChildrenPerSeed, maxNumRandNodes, maxNumRandTubes, weightMultiplier, maxDispOfAnyTargetNode, maxAvgDisp, maxWeight)

    return render(request, 'sim/run.html')