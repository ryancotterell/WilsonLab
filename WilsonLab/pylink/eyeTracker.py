# -*- coding: utf-8 -*-
#
# eyeTracker.py
#
# Copyright (C) 2011 Jason Locklin
# Distributed under the terms of the GNU General Public License (GPL).
#
# Provides a standard set of functions for using an eye tracker that
# allows experiment code to be simple and tracker agnostic.
#
# This module provides a generic interface for eye trackers
# use the following to load:
# from eyeTracker import Tracker_Eyelink as Tracker
# or
# from eyeTracker import Tracker_dummy as Tracker
# etc.
# That way, an experiment can be switched from one eyetracker
# to another without changing any code beyond this one line.
# Note: import eyeTracker before numpy or psychopy
 
 
import pylink
import sys, os, gc
from psychopy import visual, info, misc, monitors, event, core
from numpy import array, hstack
 
RIGHT_EYE = 1
LEFT_EYE = 0
BINOCULAR = 2
HIGH = 1
LOW = 0
WHITE = (255,255,255)
GRAY = GREY = (128,128,128)
BLACK = (0,0,0)
buttons =(0, 0);
spath = os.path.dirname(sys.argv[0])
if len(spath) !=0: os.chdir(spath)
 
 
 
class EyeLinkCoreGraphicsPsychopy(pylink.EyeLinkCustomDisplay):
    def __init__(self, tracker, display, displaySize):
        '''Initialize a Custom EyeLinkCoreGraphics for Psychopy
        tracker: the TRACKER() object
        display: the Psychopy display window
        '''
        pylink.EyeLinkCustomDisplay.__init__(self)
        self.display = display
        self.displaySize = displaySize
        #self.pal = None 
        self.tracker = tracker
        self.mouse = event.Mouse(visible=False)
        self.target = visual.PatchStim(display, tex = None, mask = 'circle',
                                       units='pix', pos=(0,0),
                                       size=(6,6), color = [1,1,1] )
        print("Finished initializing custom graphics")
 
    def setup_cal_display(self):
        '''This function is called just before entering calibration or validation modes'''
        self.display.flip()
    def exit_cal_display(self):
        '''This function is called just before exiting calibration/validation mode'''
        self.display.flip()
    def record_abort_hide(self):
        '''This function is called if aborted'''
        pass
    def clear_cal_display(self):
        '''Clear the calibration display'''
        self.display.flip()
    def erase_cal_target(self):
        '''Erase the calibration or validation target drawn by previous call to draw_cal_target()'''
        self.display.flip()
    def draw_cal_target(self, x, y):
        '''Draw calibration/validation target'''
        self.target.setPos((x - 0.5*self.displaySize[0], 0.5*self.displaySize[1] - y))
        self.target.draw()
        self.display.flip()
    def play_beep(self, beepid):
        ''' Play a sound during calibration/drift correct.'''
        pass
    #The following example function should be a library
    # def getColorFromIndex(self, colorindex):
    #     '''Return psychopy colors for varius objects'''
    #     if colorindex   ==  pylink.CR_HAIR_COLOR:          return (255,255,255,255)
    #     elif colorindex ==  pylink.PUPIL_HAIR_COLOR:       return (255,255,255,255)
    #     elif colorindex ==  pylink.PUPIL_BOX_COLOR:        return (0,255,0,255)
    #     elif colorindex ==  pylink.SEARCH_LIMIT_BOX_COLOR: return (255,0,0,255)
    #     elif colorindex ==  pylink.MOUSE_CURSOR_COLOR:     return (255,0,0,255)
    #     else: return (0,0,0,0)
    def draw_line(self, x1,y1,x2,y2,colorindex):
        '''Draw a line to the display screen. This is used for drawing crosshairs'''
        color = self.getColorFromIndex(colorindex)
        line = visual.ShapeStim(self.display, vertices = ( (x1,y1),(x2,y2) ),
                                lineWidth=1.0, lineColor=color )
        line.draw()
    def draw_losenge(self, x,y,width,height,colorindex):
        '''Draw the cross hair at (x,y) '''
        color = self.getColorFromIndex(colorindex)
 
    def get_mouse_state(self):
        '''Get the current mouse position and status'''
        pos = self.mouse.getPos()
        state = self.mouse.getPressed()[0]
    def get_input_key(self):
        '''Check the event buffer for special keypresses'''
        k= event.getKeys([])
        #Check for keys in keymappings
        #return keys from keymappings
 
    def exit_image_display(self):
        '''Called to end camera display'''
        self.display.flip()
    def alert_printf(self,msg):
        '''Print error messages.'''
        print "alert_printf"
    def setup_image_display(self, width, height):
        self.display.flip()
    def image_title(self, text):
        '''Draw title text at the top of the screen for camera setup'''
        title = visual.TextStim(self.display, text = text, pos=(-10,0), units=cm)
        title.draw()
        self.display.flip()
        title.draw()
    def draw_image_line(self, width,line, totlines, buff):
        '''Display image given pixel by pixel'''
        pass 
    def set_image_palette(self, r,g,b): 
        '''Given a set of RGB colors, create a list of 24bit numbers representing the pallet.
        I.e., RGB of (1,64,127) would be saved as 82047, or the number 00000001 01000000 011111111'''
        self.imagebuffer = array.array('l')
        self.clear_cal_display()
        sz = len(r)
        i =0
        self.pal = []
        while i < sz:
            rf = int(b[i])
            gf = int(g[i])
            bf = int(r[i])
            self.pal.append((rf<<16) |  (gf<<8) | (bf)) 
            i = i+1        
 
 
 
 
 
 
class Tracker_EyeLink():
    def __init__(self, win, clock, sj = "TEST", autoCalibration=True, 
                 saccadeSensitivity = HIGH, calibrationType = 'HV9',
                 calibrationTargetColor = WHITE,
                 calibrationBgColor = BLACK, CalibrationSounds = False
                 ):
        '''
        win: psychopy visual window used for the experiment
 
        clock: psychopy time clock recording time for whole experiment
 
        sj: Subject identifier string (affects EDF filename)
 
        autoCalibration:
         True: enable auto-pacing during calibration
 
        saccadeSensitivity:
         HIGH: Pursuit and neurological work
         LOW:  Cognitive research
 
        calibrationType:
         H3: Horizontal 3-point
         HV3: 3-point calibration, poor linearization
         HV5: 5-point calibration, poor at corners
         HV9: 9-point calibration, best overall
 
        calibrationTargetColor and calibrationBgColor:
         RGB tuple, i.e., (255,0,0) for Red
         One of: BLACK, WHITE, GRAY
 
        calibrationSounds:
         True: enable feedback sounds when calibrating 
 
        '''
        self.edfFileName = str(sj)+".EDF"
        print(self.edfFileName)
        inf = info.RunTimeInfo("J","1",win, refreshTest=None, 
                             userProcsDetailed=False)
        self.screenSize = inf['windowSize_pix']
        self.units = inf['windowUnits']
        self.monitorName = inf['windowMonitor.name']
        monitor = monitors.Monitor(self.monitorName)
 
        print("Connecting to eyetracker.")
        self.tracker = pylink.EyeLink()
        self.timeCorrection = clock.getTime() - self.tracker.trackerTime()
        print("Loading custom graphics")
        genv = EyeLinkCoreGraphicsPsychopy(self.tracker, win, self.screenSize)
        self.tracker.openDataFile(self.edfFileName)
        pylink.flushGetkeyQueue();
        self.tracker.setOfflineMode();
        self.tracker.sendCommand("screen_pixel_coords =  0 0 %d %d"
                                    %( tuple(self.screenSize) ))
        self.tracker.setCalibrationType(calibrationType)
        self.tracker.sendMessage("DISPLAY_COORDS  0 0 %d %d"
                                    %( tuple(self.screenSize) ))
 
        eyelink_ver = self.tracker.getTrackerVersion()
        if eyelink_ver == 3:
            tvstr = self.tracker.getTrackerVersionString()
            vindex = tvstr.find("EYELINK CL")
            tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))
        else: tracker_software_ver = 0
        if eyelink_ver>=2:
            self.tracker.sendCommand("select_parser_configuration %d" %saccadeSensitivity)
        else:
            if saccadeSensitivity == HIGH:
                svt, sat = 22, 5000
            else: svt, sat = 30, 9500
            self.tracker.sendCommand("saccade_velocity_threshold = %d" %svt)
            self.tracker.sendCommand("saccade_acceleration_threshold = %d" %sat)
 
        if eyelink_ver == 2: #turn off scenelink camera stuff
            self.tracker.sendCommand("scene_camera_gazemap = NO")
 
        # set EDF file contents
        self.tracker.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
        if tracker_software_ver>=4:
            self.tracker.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")
        else:
            self.tracker.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")
        # set link data (used for gaze cursor)
        self.tracker.sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
        if tracker_software_ver>=4:
            self.tracker.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
        else:
            self.tracker.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")
 
        #Set the calibration settings:
        pylink.setCalibrationColors( calibrationTargetColor, calibrationBgColor)
        if CalibrationSounds:
            pylink.setCalibrationSounds("", "", "")
            pylink.setDriftCorrectSounds("", "off", "off")
        else:
            pylink.setCalibrationSounds("off", "off", "off")
            pylink.setDriftCorrectSounds("off", "off", "off")
 
        if autoCalibration:
            self.tracker.enableAutoCalibration
        else: self.tracker.disableAutoCalibration
        win.flip()
        print("Opening graphics")
        pylink.openGraphicsEx(genv)
        print("Begining tracker setup")
        self.tracker.doTrackerSetup()
        win.flip()
 
 
 
    def sendMessage(self, msg):
        '''Record a message to the tracker'''
        print(msg)
        self.tracker.sendMessage(msg)
 
    def sendCommand(self, msg):
        '''Send command to the tracker'''
        print(msg)
        self.tracker.sendCommand(message)
 
    def resetEventQue(self):
        '''Reset the eyetracker event cue
            usage: use this prior to a loop calling recordFixation() so
            that old fixations or other events are cleared from the 
            buffer.
        '''
        self.tracker.resetData()
 
 
    def getStatus(self):
        """Return the status of the connection to the eye tracker"""
        if self.tracker.breakPressed():
            return("ABORT_EXPT")
        if self.tracker.escapePressed():
            return("SKIP_TRIAL")
        if self.tracker.isRecording()==0:
            return("RECORDING")
        if self.tracker.isConnected():
            return("ONLINE")
        else:
            return("OFFLINE")
        return("UNKNOWN STATUS: " + str(self.tracker.getStatus()) )
 
    #================================================================
 
 
 
 
 
    #####################################################################
    #    Eyetracker set up and take-down
    #####################################################################
 
    def preTrial(self, trial, calibTrial, win):
        '''Set up each trial with the eye tracker
        '''
 
        if calibTrial: cond = "Test/Calibration Trial"
        else: cond = "Non-test/no calibration trial"
        message ="record_status_message 'Trial %d %s'"%(trial+1, cond)
        self.tracker.sendCommand(message)
        msg = "TRIALID %s"%trial
        self.tracker.sendMessage(msg)
        #Do drift correction if necissary
 
        if calibTrial:
            win.flip()
            while True:
                try:
                    error = self.tracker.doDriftCorrect(self.screenSize[0]/2,self.screenSize[1]/2,1,1) 
                    if error != 27:
                        self.tracker.applyDriftCorrect
                        break
                    else:
                        #self.tracker.doTrackerSetup()
                        win.flip()
                except:
                    print("Exception")
                    break
            win.flip()
        print("Switching to record mode")
        error = self.tracker.startRecording(1,1,1,1)
        pylink.beginRealTimeMode(100)
        if error: return error
 
        if not self.tracker.waitForBlockStart(1000, 1, 0):
            endTrial()
            print "ERROR: No link samples received!"
            return "ABORT_EXPT"
        self.eye_used = self.tracker.eyeAvailable(); 
        #determine which eye(s) are available
        if self.eye_used == RIGHT_EYE:
            self.tracker.sendMessage("EYE_USED 1 RIGHT")
        elif self.eye_used == LEFT_EYE or self.eye_used == BINOCULAR:
            self.tracker.sendMessage("EYE_USED 0 LEFT")
            self.eye_used = LEFT_EYE
        else:
            print "Error in getting the eye information!"
            return "ABORT_EXPT"
 
        self.tracker.flushKeybuttons(0)
 
 
 
    def endTrial(self):
        '''Ends recording: adds 100 msec of data to catch final events'''
        pylink.endRealTimeMode()
        pylink.pumpDelay(100)
        self.tracker.stopRecording()
        while self.tracker.getkey() :
            pass;
 
 
    def closeConnection(self):
        '''Clean everything up, save data and close connection to tracker'''
        if self.tracker != None:
            # File transfer and cleanup!
            self.tracker.setOfflineMode();
            core.wait(0.5)
            #Close the file and transfer it to Display PC
            self.tracker.closeDataFile()
            self.tracker.receiveDataFile(self.edfFileName, 
                                         self.edfFileName) 
            self.tracker.close();
            return "Eyelink connection closed successfully"
        else:
            return "Eyelink not available, not closed properly"
 
 
 
 
    ####################################################################
    #    Getting data from the eyetracker
    ####################################################################
 
    def getSample(self, unit=None):
        '''Quickly return the current eye position
            purpose: For use with gaze contingent display experiments
            Note: For speed, this always returns in pixels
        '''
        # check for new sample update:
        sample = self.tracker.getNewestSample() 
        if(sample != None): #Perhapse, change to loop untill sample?
            if self.eye_used == RIGHT_EYE and sample.isRightSample():
                return (array(sample.getRightEye().getGaze()) -0.5*self.screenSize) *array([1,-1])
            elif self.eye_used == LEFT_EYE and sample.isLeftSample():
                return (array(sample.getLeftEye().getGaze()) - 0.5*self.screenSize) * array([1,-1])
        return None
 
    def recordFixation(self, timeout = 2):
        '''Check the event cue for a Fixation, and then return it's 
        complete parameters
            timeout: the duration of time in seconds to wait for a 
            fixation
            returns a dictionary:
            Times are based on the psychopy clock passed to init
            Gazes are in the window default unit1
            Velocities are in visual degrees per second
            Angular resolutions are in default unit per visual degree
            See pylink EndFixationEvent for more information.
 
        TODO: This function requires work. It's totally untested at the moment.
        '''
        splitTime = core.Clock()
        while 1:
            core.wait(0.01) # remove when done testing
            if self.getStatus() != "RECORDING": 
                return eyeTracker.getStatus()
            if splitTime.getTime() > timeout: #const
                self.sendMessage("TIMEOUT")
                return {'StartTime': "TIMEOUT",
                    'EndTime':          "TIMEOUT",
                    'TotalTime':        "TIMEOUT", 
                    'RecordingEye':   "TIMEOUT",
                    'StartGaze' :        "TIMEOUT",
                    'EndGaze':          "TIMEOUT",
                    'Gaze':                "TIMEOUT",
                    'StartHeadREF':  "TIMEOUT",
                    'EndHeadREF':   "TIMEOUT",
                    'HeadREF':         "TIMEOUT",
                    'PupilSize':        "TIMEOUT",
                    'StartVelocity':   "TIMEOUT",
                    'EndVelocity':    "TIMEOUT",
                    'Velocity':          "TIMEOUT",
                    'PeakVelocity':  "TIMEOUT",
                    'StartAngRes':   "TIMEOUT",
                    'EndAngRes':    "TIMEOUT"}
            sampleType = self.tracker.getNextData()
            if sampleType == pylink.ENDFIX:
                sample = self.tracker.getFloatData()
                if ( self.eye_used == RIGHT_EYE and 
                     sample.getEye() == RIGHT_EYE ):
                    break
                # or sample.getStartTime(), sample.getStartGaze()
                if ( self.eye_used == LEFT_EYE and 
                     sample.getEye() == LEFT_EYE ):
                    break
            elif ( (sampleType == 0) or (sampleType == 200) or 
                   (sampleType == 63)): #i.e., no data
                pass
        return {'StartTime': sample.getStartTime() + self.timeCorrection,
                'EndTime':   sample.getEndTime() + self.timeCorrection,
                'TotalTime': (sample.getEndTime()-sample.getStartTime()
                              + 4 ) + self.timeCorrection, 
                'RecordingEye': sample.getEye(),
                'StartGaze' : self._pix2(sample.getStartGaze()   ),
                'EndGaze':    self._pix2(sample.getEndGaze()     ),
                'Gaze':       self._pix2(sample.getAverageGaze() ),
                'StartHeadREF': sample.getStartHREF(),
                'EndHeadREF':   sample.getEndHREF(),
                'HeadREF':      sample.getAverageHREF(),
                'PupilSize':    sample.getAveragePupilSize(),
                'StartVelocity':sample.getStartVelocity(),
                'EndVelocity':  sample.getEndVelocity(),
                'Velocity':     sample.getAverageVelocity(),
                'PeakVelocity': sample.getPeakVelocity(),
                'StartAngRes':  self._pix2(sample.getStartPPD()),
                'EndAngRes':    self._pix2(sample.getEndPPD()) }
 
    def _pix2(pixels, unit = None):
        """Convert size in pixels to size in the default unit for a given Monitor object"""   
        if unit == None: #Use default unit for window
            unit = self.units
        if unit == 'pix':
            return pixels
        if unit == 'cm':
            return psychopy.misc.pix2cm(pixels, self.monitor)
        if unit == 'deg':
            return psychopy.misc.pix2deg(pixels, self.monitor)
 
 
status ="OFFLINE"
class Tracker_Dummy():
    def __init__(self, win, clock, sj = "TEST", autoCalibration=True, 
                 saccadeSensitivity = HIGH, calibrationType = 'HV9',
                 calibrationTargetColor = WHITE,
                 calibrationBgColor = BLACK, CalibrationSounds = False
                 ):
        '''A fake eyeTracker for testing purposes. This class simulates 
        all the eyeTracker commands, but does not require a connected
        tracker, or even eyeTracker specific libraries to be available.'''
        global status
        status = "ONLINE"
        #TODO: instantiate psychopy mouse
        #return True
 
    def sendMessage(self, msg):
        print(msg)
    def sendCommand(self, msg):
        print(msg)
    def resetEventQue(self):
        return True
    def getStatus(self):
        global status
	return status
    def preTrial(self, trial, calibTrial, win):
        global status
        status = "RECORDING"
        #TODO: make a fake drift-correct procedure that uses the mouse
    def endTrial(self):
        global status
        status = "ONLINE"
    def closeConnection(self):
        global status
        status = "OFFLINE"
    def getSample(self, unit=None):
        #TODO: return mouse coordinate
        return 0,0
    def recordFixation(self, timeout = 2):
        #TODO: wait for keypress, then return mouse coordinate
        return 0,0
 
 
 
 
if __name__ == "__main__":
    """Run simple gaze contingent demonstration.
    """
    win = visual.Window(size = (800,600), fullscr=True, allowGUI=False, 
                        color=[-1,-1,-1], units='pix', waitBlanking=True,
                        winType = 'pyglet', monitor='2246',
                        colorSpace='rgb')
    target = visual.PatchStim(win, tex = None, mask = None, 
                              units = 'pix', pos = (0,0), 
                              size = (10, 10),  color = [1,1,1])
    note = visual.TextStim(win, pos=[0,0], units = 'pix', 
                               text='none', 
                               color=(1,1,1))
    clock = core.Clock()
    eyeTracker = Tracker_EyeLink(win, clock)
    status = eyeTracker.getStatus()
    for Ttype in [True, False, False, True]: #loop for each "trial"
        if Ttype: note.setText("Drift Correct Trial")
        else: note.setText("Standard Trial")
        note.draw()
        win.flip()
        core.wait(1)
        eyeTracker.preTrial(99, Ttype, win)
        gc.disable()
        done = False
        while not(done): #within-trial loop
            eye_pos = eyeTracker.getSample()
            note.setText( str(eye_pos))
            target.setPos(eye_pos)
            target.draw()
            note.draw()
            win.flip()
            for key in event.getKeys():
                if ( key in ['escape','q'] ) or (eyeTracker.getStatus() != "RECORDING"):
                    win.close()
                    eyeTracker.closeConnection()
                    core.quit()
                elif key == 'space':
                    win.flip()
                    print(eyeTracker.recordFixation() )
                    print('----------------------------')
                    print(eyeTracker.getSample())
                    print(clock.getTime())
                    done = True
        eyeTracker.endTrial()
        win.flip()
        gc.enable()
    win.close()
    eyeTracker.closeConnection()
    print("Self-test completed")
    core.quit()
