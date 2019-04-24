from sim.createFrame import *
import textile

def frameToNodeString(create):

    frame = createFrame(create)
    return textile.textile(frame.toString('nodes'), html_type="xhtml")

def frameToTubeString(create):

    frame = createFrame(create)
    return textile.textile(frame.toString('tubes'), html_type="xhtml")

def frameToLongString(create):

    frame = createFrame(create)
    return textile.textile(frame.toString('nodes', 'long'), html_type="xhtml")