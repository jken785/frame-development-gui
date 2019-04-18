from mpld3 import *

from sim.createFrame import *
from sim.createBaseFrame import *
import copy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import time
from sim.loadCases import *
import os
import datetime
import textile
from django.shortcuts import render, redirect
from sim.models import *
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

webPrintOut = ""
timeLeft = ""


def geneticOptimizer(ws, numGenerations, numSeeds, numChildrenPerSeed, maxNumRandNodes, maxNumRandTubes, weightMultiplier, maxDispOfAnyTargetNode, maxAvgDisp, maxWeight):
    global webPrintOut
    global timeLeft
    # Important Sim Parameters
    # ----------------------------

    useOriginalBaseFrame = True
    # ----------------------------

    # Plotting parameters
    # ----------------------------
    finalDisplacementScaling = 15
    # ----------------------------

    end = "false"

    currentDateTime = datetime.datetime.now()
    workingDir = os.getcwd()
    path = "%s\\media" % workingDir
    if os.path.isdir(path) is False:
        os.mkdir(path)
    timestamp = currentDateTime.strftime("%Y-%m-%d %Hh %Mm %Ss")
    simFolderPath = "%s\\media\\%s" % (workingDir, timestamp)
    os.mkdir(simFolderPath)
    consOutPath = "%s\\consoleOuput.txt" % simFolderPath
    consoleOutput = open(consOutPath, "w")

    def timeRemaining(left):
        global timeLeft
        timeLeft = '%.1f' % left;

    def printOut(line):
        consoleOutput.write(line)
        consoleOutput.write("\n")
        global webPrintOut
        webPrintOut += (line + "\n")

    printOut("--PARAMETERS--")
    printOut("\nNumber of Generations: %i" % numGenerations)
    printOut("Number of Surviving Seeds Per Generation: %i" % numSeeds)
    printOut("Number of Children Per Seed Per Generation: %i" % numChildrenPerSeed)
    numFramesAnalyzed = numGenerations * numSeeds * numChildrenPerSeed
    printOut("\nYou have elected to analyze %i frames" % numFramesAnalyzed)
    printOut("across %i generations (i.e. %i per generation)" % (numGenerations, int(numFramesAnalyzed/numGenerations)))
    printOut("\nMaximum number of mutated tubes per individual: %i" % maxNumRandTubes)
    printOut("Maximum number of mutated nodes per individual: %i" % maxNumRandNodes)
    printOut("\nMaximum displacement allowed for any target node: %.5f inches" % maxDispOfAnyTargetNode)
    printOut("Maximum average displacement allowed for all target nodes: %.5f inches" % maxAvgDisp)
    printOut("Maximum weight allowed: %.3f pounds" % maxWeight)
    printOut("\nFrame mass is weighted at %f in the objective function" % weightMultiplier)
    if useOriginalBaseFrame:
        printOut("\nUsing createBaseFrame() to construct the initial seeds")
    else:
        printOut("\nUsing createFrame() to construct the initial seeds")

    def sortingKey(elem):
        return elem[0]

    # Time the simulation
    start = time.time()

    # Set up graphs (change size of figure's window using the first line below)
    plt.tight_layout()
    fig = plt.figure(figsize=(6,7))
    grid = plt.GridSpec(6, 1, hspace=1.2)
    ax1 = fig.add_subplot(grid[0:2, :], title="Score/Weight vs Generations")
    ax1.set_ylabel('Objective Function Score')
    ax2 = fig.add_subplot(grid[2:4, :], title="Avg Displacement vs Generations")
    ax2.set_ylabel('Inches')
    ax3 = fig.add_subplot(grid[4:6, :], title="Weight vs Generations")
    ax3.set_ylabel('Pounds')

    fig3D = plt.figure(figsize=(7,7))
    ax4 = fig3D.add_subplot(1, 1, 1, projection='3d')
    ax4.view_init(azim=-135, elev=35)

    ax1.grid()
    ax2.grid()
    ax3.grid()
    ax4.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax4.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax4.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax4.xaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    ax4.yaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    ax4.zaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)

    # Initialize variables
    maxScorePerWeight = 0
    averageDisp = 0

    maxScoresPerWeight = []
    weights = []
    averageDisps = []
    iterations = []
    if useOriginalBaseFrame:
        baseFrame = createBaseFrame()
    else:
        baseFrame = createFrame()
    baseFrameScorePerWeight, dispList, baseFrameAvgDisp = baseFrame.solveAllLoadCases(weightMultiplier)
    printOut("\nBase Frame Weight: %.3f" % baseFrame.weight)
    printOut("Base Frame Score: %.3f" % baseFrameScorePerWeight)
    printOut("Base Frame Avg. Disp.: %.5f" % baseFrameAvgDisp)
    printOut("Base Frame Max Disp of A Target Node: %.5f" % max(dispList))

    maxScoresPerWeight.append(baseFrameScorePerWeight)
    weights.append(baseFrame.weight)
    averageDisps.append(baseFrameAvgDisp)
    iterations.append(0)

    maxFrame = baseFrame
    errorFlag = False
    seeds = []
    for i in range(numSeeds):
        seeds.append(maxFrame)

    ax1.plot(iterations, maxScoresPerWeight)
    ax2.plot(iterations, averageDisps)
    ax3.plot(iterations, weights)
    maxFrame.plotAni(ax4, "Maximum Frame")

    # Sends live sim data to webpage
    figHTML = fig_to_html(fig)
    sp = figHTML.split('<script>')
    div = sp[0].split('</style>')
    figDiv = div[1]
    script = sp[1].split('</script>')
    figScript = script[0]

    path = "%s\\sim\\static\\results\\%i" % (workingDir, int(ws.room_name))
    if os.path.isdir(path) is False:
        os.mkdir(path)
    fig3DPath = path + "\\fig3D.png"
    fig3D.savefig(fig3DPath)
    webPrintOut = textile.textile(webPrintOut, html_type="xhtml")
    ws.send(text_data=json.dumps({
        'end': end,
        'figDiv': figDiv,
        'figScript': figScript,
        'webPrintOut': webPrintOut,
        'timeLeft': timeLeft
    }))
    webPrintOut = ""

    printOut("\n--START--")

    for gen in range(1, numGenerations+1):
        # Generate generation individuals
        if gen is 1:
            startOneGen = time.time()
        individuals = []
        for seed in seeds:
            theSameInd = copy.deepcopy(seed)
            individuals.append(theSameInd)
            for i in range(1, numChildrenPerSeed):
                individual = copy.deepcopy(seed)
                randomizeThicknessNotGeometry = random.choice((True, False))
                if randomizeThicknessNotGeometry:
                    numRandTubes = random.randint(1, maxNumRandTubes)
                    for j in range(numRandTubes):
                        individual.randomizeThicknessOfRandomTube()
                else:
                    numRandNodes = random.randint(1, maxNumRandNodes)
                    for j in range(numRandNodes):
                        individual.randomizeLocationOfRandomNode()
                individuals.append(individual)

        # Solve generation individuals
        sortingList = []

        for i in range(len(individuals)):
            individual = individuals.__getitem__(i)
            scorePerWeight, dispList, avgDisp = individual.solveAllLoadCases(weightMultiplier)
            if (individual.weight < maxWeight and maxDispOfAnyTargetNode > max(dispList) and maxAvgDisp > avgDisp):
                tuple = (scorePerWeight, avgDisp, individual)
                sortingList.append(tuple)

        if len(sortingList) is 0:
            printOut("--ERROR--")
            printOut("Check that your maxWeight, maxDispOfAnyTargetNode and maxAvgDisp are not set too low")
            errorFlag = True
            break

        sortingList.sort(key = sortingKey, reverse=True)
        seeds.clear()
        for i in range(numSeeds):
            seeds.append(sortingList.__getitem__(i)[2])

        bestInd = sortingList.__getitem__(0)
        bestIndScore = bestInd[0]
        bestIndAvgDisp = bestInd[1]
        bestIndFrame = bestInd[2]
        if maxScorePerWeight < sortingList.__getitem__(0)[0]:
            maxScorePerWeight = bestIndScore
            averageDisp = bestIndAvgDisp
            maxFrame = bestIndFrame

        maxScoresPerWeight.append(maxScorePerWeight)
        averageDisps.append(averageDisp)
        iterations.append(gen)
        weights.append(maxFrame.weight)

        ax1.plot(iterations, maxScoresPerWeight)
        ax2.plot(iterations, averageDisps)
        ax3.plot(iterations, weights)
        maxFrame.plotAni(ax4, "Maximum Frame")

        if gen is 1:
            endOneGen = time.time()
            minutesPerGen = (endOneGen - startOneGen) / 60
            print("\nSimulation will take an estimated %.1f minutes to complete" % (minutesPerGen * (numGenerations+1)))
        printOut("\n")
        printOut("Generation No. %i" % gen)
        printOut("Max Score Per Weight:\t\t%.3f" % maxScorePerWeight)
        printOut("Avg Disp. of Target Nodes:\t%.5f" % averageDisp)
        printOut("Total Weight:\t\t\t%.3f" % maxFrame.weight)
        timeToGo = (minutesPerGen*numGenerations) - (minutesPerGen*(gen-1))
        timeRemaining(timeToGo)
        print("\n~%.1f minutes remaining..." % timeToGo)

        # Sends live sim data to webpage
        figHTML = fig_to_html(fig)
        sp = figHTML.split('<script>')
        div = sp[0].split('</style>')
        figDiv = div[1]
        script = sp[1].split('</script>')
        figScript = script[0]


        path = "%s\\sim\\static\\results\\%i" % (workingDir, int(ws.room_name))
        if os.path.isdir(path) is False:
            os.mkdir(path)
        fig3DPath = path + "\\fig3D.png"
        fig3D.savefig(fig3DPath)
        webPrintOut = textile.textile(webPrintOut, html_type="xhtml")
        ws.send(text_data=json.dumps({
            'end': end,
            'figDiv': figDiv,
            'figScript': figScript,
            'webPrintOut': webPrintOut,
            'timeLeft': timeLeft
        }))
        webPrintOut = ""


    ax1.plot(iterations, maxScoresPerWeight)
    ax2.plot(iterations, averageDisps)
    ax3.plot(iterations, weights)
    maxFrame.plotAni(ax4, "Maximum Frame")
    maxFrame.toTextFile(simFolderPath)

    if not errorFlag:
        printOut("\n--FINISHED--")

        printOut("\n--STATS--")
        end = time.time()
        minutesTaken = (end - start) / 60
        printOut("\nMinutes taken for simulation to complete: %.1f" % minutesTaken)
        printOut("That's %.2f frames per second!" % (numFramesAnalyzed/(minutesTaken*60)))
        printOut("\nTotal Number of Frames Analyzed: %i" % numFramesAnalyzed)
        printOut("\nThe best frame's score was %.3f" % (maxScorePerWeight-baseFrameScorePerWeight))
        printOut("better than the original seed frame")
        printOut("\nThe weight of the best frame was")
        printOut("%.2f pounds less than the original seed frame" % (baseFrame.weight-maxFrame.weight))
        printOut("\nThe avg. displacement of all target nodes for the best frame was")
        printOut("%.5f inches less than the original seed frame" % (baseFrameAvgDisp-averageDisp))

        # Plot graphs and frame/displacements

        figPath = '%s\\graph.png' % simFolderPath
        fig.savefig(figPath)
        for loadCase in LoadCases.listLoadCases:
            maxFrame.setLoadCase(loadCase)
            figPath = '%s\\%s.png' % (simFolderPath, loadCase.name)
            maxFrame.solve(weightMultiplier)
            maxFrame.plot(finalDisplacementScaling, figPath)
        plt.close(fig)

        end = "true"
        ws.send(text_data=json.dumps({
            'end': end,
        }))

    consoleOutput.close()


