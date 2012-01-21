#!/usr/bin/python

# -*- coding: utf-8 -*-
#
# wilsonLab.py
#
# Copyright (C) 2012 Ryan Cotterell
# Provides an Psychopy implementation of phonological experiments conducted
# at Johns Hopkins University

from psychopy import core, data, event, visual, gui, sound
from time import sleep
from datetime import datetime
from random import shuffle

class Experiment1:
    '''Experiment 1 tests the ability of the participants to associate phonological features with images'''

    RIGHT_MARGIN = 50
    LEFT_MARGIN = 50

    def __init__(self, win, clock, units=None, name='John Smith'):
        '''Initialize Experiment 1
        win: a Psychopy display window object
        clock: a Psychopy clock object
        units: units used by the display
        name: name of the participant
        '''

        self.win = win
        self.clock = clock
        self.units = units
        self.size = win.size
        self.experimentTime = datetime.now().strftime("%Y-%m-%d@%H:%M")
        self.name = name
        
        #If not unit is specified then the units
        #default to those used by the display
        if (self.units == None):
            self.units = self.win.units

    def run(self):
        '''starts Experiment 1. Loads all trial data from the files specifies,
        displays media, records reaction time
        '''

        self.setImageCoordinates(50, 50)
        self.loadTrialDataFromFile()
        self.createTrialOrder()
        self.clock.reset()

        while self.hasNextTrial():
            startTime = self.clock.getTime()
            self.nextTrial()
            event.clearEvents()
            waiting = True

            while waiting:

                if event.getKeys(['escape']): #quits experiment early
                    core.quit()
                elif event.getKeys(['f','j']): #moves to next trial
                    waiting = False
                    endTime = self.clock.getTime()
                    self.saveToFile(self.currentTrialNum, startTime, endTime, 
                                    self.currentDuration)

        self.win.flip()
        
    def setImageCoordinates(self, xMargin = 0.0, yMargin = 0.0):
        '''Determines the appropriate size of the image given
        the size of the screen
        xMargin: the vertical margin
        yMargin: the horizontal margin
        '''

        #to keep the variables in scope
        absoluteMaxX = None;
        absoluteMaxY = None;
        absoluteMinX = None;
        absoluteMinY = None;
        
        #could be set to 
        if (self.units == 'norm'):
            absoluteMaxX = 1.0
            absoluteMaxY = 1.0
            absoluteMinX = -1.0
            absoluteMinY = -1.0
        elif (self.units == 'pix'):
            absoluteMaxX = self.size[0] / 2.0
            absoluteMaxY = self.size[1] / 2.0
            absoluteMinX = -absoluteMaxX
            absoluteMinY = -absoluteMaxY        
        else:
            raise Exception('That unit is not supported')
            
        self.width  = (absoluteMaxX - absoluteMinX) / 2.0
        self.height = (absoluteMaxY - absoluteMinY) / 2.0
        
        maxX = absoluteMaxX - self.width   / 2.0 
        maxY = absoluteMaxY - self.height  / 2.0
        
        minX = absoluteMinX +  self.width  / 2.0
        minY = absoluteMinY +  self.height / 2.0

        self.width -= xMargin
        self.height -= yMargin
        
        #Card Display
        #---------------
        #|   1  |   2  |
        #|______|______|
        #|      |      |
        #|   3  |   4  |
        #---------------

        self.imageCoordinates = [(minX,maxY), (maxX,maxY), (minX,minY), (maxX,minY)]


    def drawImages(self, num):
        '''Draw the nth set of images from the loaded
        trial data
        num: n
        '''

        for imageObj in self.imageObjs[num]:
            imageObj.draw()  
        
    def drawCrossHair(self, x = 0, y = 0, crossColor = 'white'):
        '''Draws a crosshair in the middle of the screen for the 
        x: the x coordinate of the crosshair
        y: the y coordinate of the crosshair
        crossColor: the color of the crosshair
        '''

        size1 = 0
        size2 = 0

        #determine units
        if (self.units == 'pix'):
            size1 = 2
            size2 = 60
        elif (self.units == 'norm'):
            size1 = 0.05
            size2 = 0.1

        fixation1 = visual.PatchStim(win=self.win,
                                    pos=(x,y), 
                                    size=(size1, size2),
                                    sf=0,
                                    color=crossColor,
                                    mask=None)
        fixation2 = visual.PatchStim(win=self.win,
                                     pos=(x,y),
                                     size=(size2, size1),
                                     sf=0,
                                     color=crossColor,
                                     mask=None)
        fixation1.draw()
        fixation2.draw()

    def loadTrialDataFromFile(self, filename='./files', imageBaseDir = './image_dir/', soundBaseDir = './sound_dir/'):
        '''
        Loads the trial data (sounds and images) from the file
        filename: the name of the file
        imageBaseDir: the directory where the images are stored
        soundBaseDir: the directory where the sounds are stored
        '''

        #empty lists
        self.numTrials = 0
        #image objects for draw functions 
        self.imageObjs = []
        #image file names for results file
        self.imageFileNames = []
        #sound objects for play functions
        self.soundObjs = []
        #sound file names for results file
        self.soundFileNames = []

        f = open(filename,'r')

        #analyze the file line by line
        for line in f.read().splitlines():
            files = line.split(', ')

            self.soundFileNames.insert(self.numTrials, files[-1])
            self.soundObjs.insert(self.numTrials,sound.Sound(value = soundBaseDir + files.pop()))
 
            imageFileName = []
            #image objects for draw function
            imageObj = []
            n = 0
            for fileName in files:
                imageObj.append(visual.PatchStim(self.win, 
                                                tex = imageBaseDir + fileName,
                                                units=self.units,
                                                pos=(self.imageCoordinates[n]),
                                                size=(self.width, self.height)))
                imageFileName.append(fileName)
                n += 1
                  
            self.imageObjs.insert(self.numTrials, imageObj)
            self.imageFileNames.insert(self.numTrials, imageFileName)
            self.numTrials += 1

                   
    def createTrialOrder(self, randomOrder=True):
        '''Creates a trial order: either random or in the order loaded 
        from the file
        '''

        self.order = [x for x in range(0,self.numTrials)]
        if (randomOrder):
            shuffle(self.order)

    def getNextTrial(self):
        '''Returns the next trial
        '''

        return self.order[0]

    def hasNextTrial(self):
        ''' Checks whether there is another unrun trial
        '''

        if (len(self.order) > 0):
            return True
        else:
            return False

    def nextTrial(self):
        '''Preforms the next trial
        first draws the images and the crosshair and red
        then it plays the sound and sleeps for the duration of the sound
        preventing the user from moving on to the next trial while
        the sound is still playing. When sound finishes playing the cross
        hair turns white and the user may hit any key
        '''
        self.currentTrialNum = self.order.pop(0)
        self.currentDuration = self.soundObjs[self.currentTrialNum].getDuration()
        self.drawImages(self.currentTrialNum)
        self.drawCrossHair(crossColor='red')
        self.win.flip()
        self.soundObjs[self.currentTrialNum].play()
        sleep(self.currentDuration)
        self.drawImages(self.currentTrialNum)
       	self.drawCrossHair(crossColor='white')
        self.win.flip()
        

    def saveToFile(self,orderNum, startTime, endTime, soundDuration, resultsBaseDir = './results_dir/'):
        '''saves the data to the file determined by the participant's names
        and the exact start time of the experiment
        orderNum: the trial num
        startTime: the start time of the trial
        endTime: the end time of the trial
        soundDuration: the duration of the sound played
        resultsBaseDir: the directory to save the results file
        '''

        #adjust start time to prevent really small numbers
        if (startTime < 0.1):
            starTime = 0

        baseFileName = self.name + '_'
        fileName = baseFileName + self.experimentTime + '.txt'

        f = open(resultsBaseDir + fileName, 'a')
        f.write(str(self.imageFileNames[orderNum]) + '\t' + str(self.soundFileNames[orderNum]) + 
                '\t' + '%f' % startTime + '\t' + '%f' % endTime + '\t' 
                + '%f' % soundDuration + '\n')
        f.close()

