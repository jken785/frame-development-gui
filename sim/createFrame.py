from sim.tubeSizes import *
from sim.frame import *
from sim.createBaseFrame import *

def createFrame(create):
    frame = Frame()

    line = create.readline()

    while line:
        exec(line)
        line = create.readline()

    return frame