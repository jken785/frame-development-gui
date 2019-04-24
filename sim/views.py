from django.shortcuts import render, redirect
from sim.models import *
from django.views.decorators.csrf import csrf_exempt
from sim.geneticOptimizer import geneticOptimizer
import os
from FrameWebSim.settings import BASE_DIR
from sim.frameToString import *
from django.contrib.auth.decorators import login_required


@login_required(login_url="/login/")
def main(request):
    # sim = Sim.objects.get(pk=1)
    # consOutPath = sim.consoleOutput
    # consOutFile = open('sim/static/results/'+consOutPath, 'r')
    # consOut = consOutFile.read()
    #
    # graphsPath = sim.graphOutput
    # graphsFile = open('sim/static/results/'+graphsPath, 'r')
    # graphs = graphsFile.read()
    #
    # plot3DPath = "results/" + sim.plot3DPath
    # args = {'consOut': consOut, 'graphs': graphs, 'plot3DPath': plot3DPath}
    return render(request, 'sim/base.html')

@login_required(login_url="/login/")
def showCreateFrame(request, id):
    import textile
    file = open(os.path.join(BASE_DIR, ('sim\static\\results\%i\createFrame.txt' % id)), 'r')
    createString = textile.textile(file.read())
    args = { 'createFrame': createString, 'id':id }
    return render(request, 'sim/createFrame.html', args)

@login_required(login_url="/login/")
def createModelFromSim(request, id):
    args = { 'id': id }
    return render(request, 'sim/createFromSim.html', args)

@login_required(login_url="/login/")
def createModelFromSimBackend(request, id):
    newModel = FrameModel(name=request.POST.get('name'), author_id=request.user.id)
    newModel.save()
    loadPath = 'sim\static\models\%i\loadModel.txt' % newModel.id
    dirPath = os.path.join(BASE_DIR, ("sim\static\models\%i" % newModel.id))
    os.mkdir(dirPath)
    createFrame = open(os.path.join(BASE_DIR, loadPath), 'w+')
    simCreateFrame = open(os.path.join(BASE_DIR, ('sim\static\\results\%i\createFrame.txt' % id)), 'r')
    createFrame.write(simCreateFrame.read())
    simCreateFrame.close()
    createFrame.close()
    loadcases = open(os.path.join(BASE_DIR, ('sim\static\models\%i\loadcases.txt' % newModel.id)), 'w+')
    fromID = Sim.objects.get(pk=id).fromModel.id
    simLoadcases = open(os.path.join(BASE_DIR, ('sim\static\models\%i\loadcases.txt' % fromID)), 'r')
    loadcases.write(simLoadcases.read())
    loadcases.close()
    simLoadcases.close()
    newModel.createFrame = loadPath
    newModel.save()
    path = '/sim/load/%i/' % newModel.id
    return redirect(path)

@login_required(login_url="/login/")
def load(request):
    models = FrameModel.objects.filter(author=request.user.id)
    args = {'models': models}
    return render(request, 'sim/load.html', args)

@login_required(login_url="/login/")
def loaded(request, id):
    model = FrameModel.objects.get(pk=id)
    args = {'id': id}
    return render(request, 'sim/loaded.html', args)

@login_required(login_url="/login/")
def run(request, id):
    sim = Sim(runBy_id=request.user.id)
    sim.save()
    sim.fromModel_id = id
    sim.consoleOutput = "sim/static/results/%s/consoleOutput.txt" % sim.id
    sim.startingFrame = "sim/static/models/%s/loadModel.txt" % sim.fromModel_id
    sim.graphOutput = "sim/static/results/%s/graph.png" % sim.id
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
    args = { 'id': sim.id, 'modelID': id }

    open(os.path.join(BASE_DIR, ("sim\loadCases.py")), 'w').close()
    loadCaseCode = open(os.path.join(BASE_DIR, ("sim\loadCases.py")), 'w')
    loadCaseFile = open(os.path.join(BASE_DIR, ("sim\static\models\%i\loadcases.txt" % id)), 'r')
    for line in loadCaseFile:
        loadCaseCode.write(line)
    loadCaseCode.close()
    loadCaseFile.close()

    return render(request, 'sim/run.html', args)

@login_required(login_url="/login/")
def listResults(request, id):
    sims = Sim.objects.filter(fromModel=id)
    args = {'sims': sims, 'id':id }
    return render(request, 'sim/listSims.html', args)

@login_required(login_url="/login/")
def viewResults(request, id):
    import textile
    sim = Sim.objects.get(pk=id)
    consOutFile = open(os.path.join(BASE_DIR, ("sim\static\\results\%i\consoleOutput.txt" % id)), 'r')
    consOut = textile.textile(consOutFile.read(), html_type='xhtml')

    createFrameFile = "sim\static\\results\%i\createFrame.txt" % id
    create = open(os.path.join(BASE_DIR, createFrameFile), 'r')
    frame = createFrame(create)
    frame.plotForCreation(os.path.join(BASE_DIR, ("sim\static\\results\%i\plot.png" % id)))

    args = { 'sim': sim, 'consOut': consOut }
    return render(request, 'sim/viewResults.html', args)

@login_required(login_url="/login/")
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

@login_required(login_url="/login/")
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
    path = '/sim/editLoadcases/%i/' % id
    return redirect(path)

@login_required(login_url="/login/")
def create(request):
    return render(request, 'sim/create.html')

@login_required(login_url="/login/")
def createNew(request):
    newModel = FrameModel(name=request.POST.get('name'), author_id=request.user.id)
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

@login_required(login_url="/login/")
def editModel(request, id):
    model = FrameModel.objects.get(pk=id)
    createFrameFile = model.createFrame

    args = {'id': id }
    if os.path.getsize(os.path.join(BASE_DIR, createFrameFile)) > 0:
        create = open(os.path.join(BASE_DIR, createFrameFile), 'r')
        names = []
        tubes = []
        for line in create:
            if line.startswith("frame.addNode"):
                splitArray = line.split('"')
                names.append(splitArray[1])
            if line.startswith("frame.addTube"):
                size = line.split("(")[1].split(",")[0]
                splitArray = line.split('"')
                nodeFrom = splitArray[1]
                nodeTo = splitArray[3]
                tubes.append({ 'size': size, 'nodeFrom': nodeFrom, 'nodeTo': nodeTo })
        create.close()
        create = open(os.path.join(BASE_DIR, createFrameFile), 'r')
        toString = frameToLongString(create)
        create.close()

        create = open(os.path.join(BASE_DIR, createFrameFile), 'r')
        frame = createFrame(create)
        frame.plotForCreation(os.path.join(BASE_DIR, ("sim\static\models\%i\plot.png" % id)))

        args = { 'id': id, 'nodes': names, 'tubes': tubes, 'toString': toString}
    return render(request, 'sim/editModel.html', args)

@login_required(login_url="/login/")
def addNode(request, id):
    model = FrameModel.objects.get(pk=id)
    createFrameFile = model.createFrame
    create = open(os.path.join(BASE_DIR, createFrameFile), 'r')
    nodeLines = ""
    tubeLines = ""
    for line in create:
        if line.startswith("frame.addNode"):
            nodeLines += line
        elif line.startswith("frame.addTube"):
            tubeLines += line
    create.close()
    name = request.POST.get('name')
    x = request.POST.get('x')
    y = request.POST.get('y')
    z = request.POST.get('z')
    maxXNegDev = request.POST.get('maxXNegDev')
    maxXPosDev = request.POST.get('maxXPosDev')
    maxYNegDev = request.POST.get('maxYNegDev')
    maxYPosDev = request.POST.get('maxYPosDev')
    maxZNegDev = request.POST.get('maxZNegDev')
    maxZPosDev = request.POST.get('maxZPosDev')
    symmetric = request.POST.get('symmetric')
    required = request.POST.get('required')
    xGroup = request.POST.get('xGroup')
    addNode = 'frame.addNode("%s", %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % (
        name, x, y, z, symmetric, required, maxXNegDev, maxXPosDev, maxYNegDev,
        maxYPosDev, maxZNegDev, maxZPosDev
    )
    if xGroup is not "":
        addNode += (', "%s")\n' % xGroup)
    else:
        addNode += (')\n')
    nodeLines += addNode

    newLines = nodeLines + tubeLines
    create = open(os.path.join(BASE_DIR, createFrameFile), 'w+')
    create.write(newLines)
    create.close()

    path = '/sim/editModel/%i/' % id
    return redirect(path)

@login_required(login_url="/login/")
def addTube(request, id):
    model = FrameModel.objects.get(pk=id)
    createFrameFile = model.createFrame
    create = open(os.path.join(BASE_DIR, createFrameFile), 'a')
    size = request.POST.get('size')
    minSize = request.POST.get('minSize')
    nodeFrom = request.POST.get('nodeFrom')
    nodeTo = request.POST.get('nodeTo')
    symmetric = request.POST.get('symmetric')
    required = request.POST.get('required')
    tubeGroup = request.POST.get('tubeGroup')
    addTube = 'frame.addTube(%s, %s, "%s", "%s", %s, %s' % (
        size, minSize, nodeFrom, nodeTo, symmetric, required
    )
    if tubeGroup is not "":
        addTube += (', "%s")\n' % tubeGroup)
    else:
        addTube += (')\n')
    create.write(addTube)
    create.close()
    path = '/sim/editModel/%i/' % id
    return redirect(path)

@login_required(login_url="/login/")
def removeNode(request, id, name):
    model = FrameModel.objects.get(pk=id)
    createFrameFile = model.createFrame
    create = open(os.path.join(BASE_DIR, createFrameFile), 'r')
    frame = createFrame(create)
    frame.removeNodeByName(name)
    frame.toTextFile(os.path.join(BASE_DIR, createFrameFile))
    path = '/sim/editModel/%i/' % id
    return redirect(path)

@login_required(login_url="/login/")
def removeTube(request, id, nodeFrom, nodeTo):
    model = FrameModel.objects.get(pk=id)
    createFrameFile = model.createFrame
    create = open(os.path.join(BASE_DIR, createFrameFile), 'r')
    frame = createFrame(create)
    frame.removeTubeByNodes(nodeFrom, nodeTo)
    frame.toTextFile(os.path.join(BASE_DIR, createFrameFile))
    path = '/sim/editModel/%i/' % id
    return redirect(path)

@login_required(login_url="/login/")
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

@login_required(login_url="/login/")
def save(request, id):
    path = '/sim/load/%i/' % id
    return redirect(path)
