#!/usr/bin/python

import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
sys.path.append("/home/ryan/pylink")
import pylink
from eyeTracker import Tracker_EyeLink, Tracker_Dummy, EyeLinkCoreGraphicsPsychopy
from psychopy import core, data, event, visual, gui
from time import sleep
from wilsonLab import Experiment1

#setup window
win = visual.Window(size=(1366, 768), fullscr=True, screen=0, 
                    allowGUI=False, 
                    allowStencil=False,
                    monitor='testMonitor', 
                    color='black', 
                    colorSpace='rgb', 
                    units='pix'
                    )
#setup clock 

clock = core.Clock()

#setup tracker
#tracker = Tracker_EyeLink(win, clock)
tracker = Tracker_Dummy(win, clock)

#setup calibration?
#test = EyeLinkCoreGraphicsPsychopy(tracker, win, 1000)


x = Experiment1(win, clock)
x.run()

    



