from django.shortcuts import render, redirect
from sim.models import *
from django.views.decorators.csrf import csrf_exempt
from sim.geneticOptimizer import geneticOptimizer
import os
from FrameWebSim.settings import BASE_DIR
from sim.frameToString import *

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

    open(os.path.join(BASE_DIR, ("sim\loadCases.py")), 'w').close()
    loadCaseCode = open(os.path.join(BASE_DIR, ("sim\loadCases.py")), 'w')
    loadCaseFile = open(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id)), 'r')
    for line in loadCaseFile:
        loadCaseCode.write(line)
    loadCaseCode.close()
    loadCaseFile.close()

    return render(request, 'sim/run.html', args)

@csrf_exempt #You need to get rid of this eventually
def saveLoadcase(request, id):
    model = FrameModel.objects.get(pk=id)
    prev = ""
    names = ""
    alreadyThere = False
    if os.path.isfile(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id))):
        alreadyThere = True
        with open(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id)), 'r') as f:
            for line in f:
                if line.find('name') > 0:
                    names += ","+line.split('"')[1]
                if line.find('listLoadCases') < 0:
                    prev += line
    loadCaseFile = open(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id)), 'w+')
    loadCaseFile.write(prev)
    if not alreadyThere:
        loadCaseFile.write('class LoadCases:\n')
    loadCaseFile.write('\tclass %s:\n' % request.POST.get('name'))
    loadCaseFile.write('\t\tname = "%s"\n' % request.POST.get('name'))
    loadCaseFile.write('\t\tforce = [%f, %f, %f, %f, %f, %f]\n' % (
        float(request.POST.get('x')),
        float(request.POST.get('y')),
        float(request.POST.get('z')),
        float(request.POST.get('xMom')),
        float(request.POST.get('yMom')),
        float(request.POST.get('zMom'))
    ))
    loadCaseFile.write('\t\tnodesForce = [%s, force]\n' % request.POST.get('nodesAffected'))
    loadCaseFile.write('\t\tnodeForceCases = [nodesForce]\n')
    loadCaseFile.write('\t\tfixedNodes = [%s]\n' % request.POST.get('fixedNodes'))
    loadCaseFile.write('\t\tobjFuncNodes = [%s]\n' % request.POST.get('objFuncNodes'))
    loadCaseFile.write('\t\tobjFuncWeight = %f\n' % float(request.POST.get('objFuncWeight')))
    loadCaseFile.write('\tlistLoadCases = [%s%s]' % (request.POST.get('name'), names))
    loadCaseFile.close()

    args = { 'saved': True }
    path = '/sim/editLoadcases/%i/' % id
    return redirect(path)

def deleteLoadcase(request, id, name):
    lines = ""
    with open(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id)), 'r') as f:
        lines = f.read()
        f.close()

    splitArray = lines.split('\tclass '+ name + ':\n')
    splitArray[1] = splitArray[1].splitlines()
    splitArray[1] = splitArray[1][7:len(splitArray[1])-1]
    for i in range(len(splitArray[1])):
        splitArray[1][i] += "\n"
    splitArray[1] = "".join(splitArray[1])
    output = splitArray[0] + splitArray[1]
    with open(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id)), 'w+') as f:
        f.write(output)
        f.close()
    names = ""
    with open(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id)), 'r') as f:
        for line in f:
            if line.find('name') > 0:
                if len(names) is 0:
                    names += line.split('"')[1]
                else:
                    names += ',' + line.split('"')[1]
        f.close()
    with open(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id)), 'a') as f:
        f.write('\tlistLoadCases = [%s]\n' % names)
        f.close()
    print(repr(output))
    path = '/sim/editLoadcases/%i/' % id
    return redirect(path)

@csrf_exempt #You need to get rid of this eventually
def create(request):
    return render(request, 'sim/create.html')


@csrf_exempt #You need to get rid of this eventually
def createNew(request):
    newModel = FrameModel(name=request.POST.get('name'))
    newModel.save()
    path = '/sim/editModel/%i/' % newModel.id
    loadPath = 'sim\static\models\%i\loadModel.txt' % newModel.id
    dirPath = os.path.join(BASE_DIR, ("sim\static\models\%i" % newModel.id))
    os.mkdir(dirPath)
    createFrame = open(os.path.join(BASE_DIR, loadPath), 'w+')
    createFrame.close()
    newModel.createFrame = loadPath
    newModel.save()
    return redirect(path)


@csrf_exempt #You need to get rid of this eventually
def editModel(request, id):
    model = FrameModel.objects.get(pk=id)
    createFrameFile = model.createFrame
    create = open(os.path.join(BASE_DIR, createFrameFile), 'r')
    names = []
    for line in create:
        splitArray = line.split('"')
        names.append(splitArray[1])
    create.close()
    create = open(os.path.join(BASE_DIR, createFrameFile), 'r')
    toString = frameToLongString(create)
    create.close()

    create = open(os.path.join(BASE_DIR, createFrameFile), 'r')
    frame = createFrame(create)
    frame.plotForCreation(os.path.join(BASE_DIR, ("sim\static\models\%i\plot.png" % id)))

    args = { 'id': id, 'nodes': names, 'toString': toString}
    return render(request, 'sim/editModel.html', args)

@csrf_exempt #You need to get rid of this eventually
def editLoadcases(request, id):
    model = FrameModel.objects.get(pk=id)
    createFrameFile = model.createFrame
    createFrame = open(os.path.join(BASE_DIR, createFrameFile), 'r')
    toString = frameToNodeString(createFrame)
    args = {'id': id, 'toString': toString}

    if os.path.isfile(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id))):
        loadcases = []
        loadCaseFile = open(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id)), 'r')
        length = len(loadCaseFile.read().split('class')) - 2
        loadCaseFile.close()
        loadCaseFile = open(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id)), 'r')
        loadCaseFile.readline()
        loadCaseFile.readline()

        for i in range(length):
            nameArray = loadCaseFile.readline().split('"')
            name = nameArray[1]
            force = loadCaseFile.readline().split('[')[1].split(']')[0]
            nodes = loadCaseFile.readline().split('[')[1].split(', ')[0]
            loadCaseFile.readline()
            fixed = loadCaseFile.readline().split('[')[1].split(']')[0]
            objFuncNodes = loadCaseFile.readline().split('[')[1].split(']')[0]
            objFuncWeight = loadCaseFile.readline().split(' ')[2].split('\n')[0]
            loadcases.append({'name':name, 'force':force, 'nodes': nodes,
                              'fixed': fixed, 'objFuncNodes': objFuncNodes, 'objFuncWeight': objFuncWeight})
            loadCaseFile.readline()

        loadCaseFile.close()
        args = {'id': id, 'toString': toString, 'loadcases': loadcases}

    return render(request, 'sim/editLoadcases.html', args)

@csrf_exempt #You need to get rid of this eventually
def save(request, id):
    path = '/sim/load/%i/' % id
    return redirect(path)
