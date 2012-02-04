#!/usr/bin/python

# -*- coding: utf-8 -*-
#
# wilsonLab.py
#
# Copyright (C) 2012 Ryan Cotterell
# Provides an Psychopy implementation of phonological experiments conducted
# at Johns Hopkins University

import os, re
from psychopy import core, data, event, visual, gui, sound
from time import sleep
from datetime import datetime
from random import shuffle
from itertools import permutations

class Experiment1:
    '''Experiment 1 tests the ability of the participants to associate phonological features with images'''

    max_images_per_trial = 4
    images_multiple = 12 #needs to be a multiple of 12

    right_margin = 150
    left_margin = 150

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

        self.setImageCoordinates(self.right_margin, self.left_margin)
        self.loadTrialDataFromFile(imageBaseDir='/home/ryan/research/WilsonLab/snodgrass-vanderwart/color/', soundBaseDir='/home/ryan/research/WilsonLab/snodgrass-vanderwart/wav/')
        self.createTrialOrder()
        self.clock.reset()
        self.mouse = event.Mouse(visible=True, newPos=None, win=self.win)

        while self.hasNextTrial():
            startTime = self.clock.getTime()
            self.mouse.clickReset()
            self.nextTrial()
            event.clearEvents()
            waiting = True
            pressed = False

            while waiting:
                #print self.boxClicked(self.mouse.getPos())
                
                if (self.mouse.getPressed()[0] and self.clock.getTime() > self.soundStop):
                    pressed = True

                if event.getKeys(['escape']): #quits experiment early
                    core.quit()
                elif (pressed and not self.mouse.getPressed()[0]): #moves to next trial
                    pressed = False
                    waiting = False
                    endTime = self.clock.getTime()
                    self.saveToFile(self.currentTrialNum, startTime, endTime, self.boxClicked(self.mouse.getPos()))

            
            self.win.flip()
            self.win.flip()
            sleep(2) #intertrial period
        self.win.flip()
        
    def setImageCoordinates(self, xMargin = 0.0, yMargin = 0.0):
        '''Determines the appropriate size of the image given
        the size of the screen
        xMargin: the vertical margin
        yMargin: the horizontal margin
        '''
        
        #numboxesX should equal numBoxesY and they should both be odd
        # for most experiments
        self.numboxesX = 5
        self.numboxesY = 5

        self.imageCoordinates = []
        self.imageBuffer = 4
        self.xLineCoord = set([])
        self.yLineCoord = set([])

 
        #TODO Only pix are supported
        #could be set to 
        #if (self.units == 'norm'):
        #    self.absoluteMaxX = 1.0
        #    self.absoluteMaxY = 1.0
        #    self.absoluteMinX = -1.0
        #    self.absoluteMinY = -1.0
        if (self.units == 'pix'):
            self.absoluteMaxX = self.size[0] / 2
            self.absoluteMaxY = self.size[1] / 2
            self.absoluteMinX = -self.absoluteMaxX
            self.absoluteMinY = -self.absoluteMaxY   
            self.edgeBuffer = 1
        else:
            raise Exception('Only pix are supported')
            
        self.boxWidth  = self.size[0] / self.numboxesX
        self.boxHeight = self.size[1] / self.numboxesY

        boxX = self.absoluteMinX -  self.boxWidth / 2
        boxY = self.absoluteMaxY - self.boxHeight / 2
        lineX = self.absoluteMinX + self.edgeBuffer
        lineY = self.absoluteMaxY -  self.edgeBuffer

        xCount = 0
        yCount = 0
        while boxY > self.absoluteMinY:
            while boxX < self.absoluteMaxX:
                self.xLineCoord.add(lineX)

                #determine picture boxes
                #x = (boxes per row - 3) / 2 
                #y = (boxes per column - 3) / 2
                if ((xCount == (self.numboxesX - 3) / 2 + 1 or xCount == self.numboxesX - (self.numboxesX - 3) / 2)
                    and (yCount == (self.numboxesY / 2) - 1 or yCount == (self.numboxesY / 2) + 1)):  
                    self.imageCoordinates.append((boxX, boxY))
    
                if (xCount == self.numboxesX / 2 + 1  and yCount == self.numboxesY / 2):
                    self.centerBox = (boxX, boxY)                    

                boxX += self.boxWidth
                lineX += self.boxWidth
                xCount += 1
                

            boxX = self.absoluteMinX - self.boxWidth / 2
            lineX = self.absoluteMinX + self.edgeBuffer
            xCount = 0
            self.yLineCoord.add(lineY)
            lineY -= self.boxHeight
            boxY -= self.boxHeight
            yCount += 1

        self.xLineCoord.add(self.absoluteMaxX-self.edgeBuffer)
        self.yLineCoord.add(self.absoluteMinY + self.edgeBuffer)

        #Display
        #---------------
        #|   1  |   2  |
        #|______|______|
        #|      |      |
        #|   3  |   4  |
        #---------------


    def drawBoxes(self):
        
        for x in self.xLineCoord:
            tmpLine = visual.ShapeStim(win=self.win,
                                       units=self.units,
                                       lineWidth=2.0,
                                         lineColor='black',
                                       pos=(0,0),
                                       vertices=((x, self.absoluteMinY),(x, self.absoluteMaxY)))
            tmpLine.draw()
            
            for y in self.yLineCoord:
              tmpLine = visual.ShapeStim(win=self.win,
                                         units=self.units,
                                         lineWidth=2.0,
                                         lineColor='black',
                                         pos=(0,0),
                                         vertices=((self.absoluteMinX, y),(self.absoluteMaxX,y)))
              tmpLine.draw()

              
     
    def drawImages(self, num):
        '''Draw the nth set of images from the loaded
        trial data
        num: n
        '''

        for imageObj in self.imageObjs[num]:
            imageObj.draw()  
        
    def drawCrossHair(self, crossColor = 'black', lineWidth = 2):
        '''Draws a crosshair in the center box
        crossColor: the color of the crosshair
        '''

        #determine units
        if (self.units == 'pix'):
            size1 = 2
            size2 = 60
        else:
            raise Exception('Pix are the only supported units')
        
        #elif (self.units == 'norm'):
        #    size1 = 0.05
        #    size2 = 0.1

        fixation1 = visual.PatchStim(win=self.win,
                                    pos=self.centerBox, 
                                     size=(self.boxWidth / 3, lineWidth),
                                    sf=0,
                                    color=crossColor,
                                    mask=None)
        fixation2 = visual.PatchStim(win=self.win,
                                     pos=self.centerBox,
                                     size=(lineWidth, self.boxHeight / 3),
                                     sf=0,
                                     color=crossColor,
                                     mask=None)
        fixation1.draw()
        fixation2.draw()

    def loadTrialDataFromFile(self, filename='./files', imageBaseDir = './image_dir/', soundBaseDir = './sound_dir/'):
        '''
        Loads the trial data (sounds and images) from the file can only load 4 images per page
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

        lines = f.read().splitlines()
    
        self.possibleLocations = self.generatePermutations(len(lines))
        print self.possibleLocations
        sleep(40)

        #analyze the file line by line
        for line in lines:

            files = line.split(', ')

            if (len(files) > 5):
                raise Exception("Each line of the stimuli file must be contain a comma separated list of 5 elements. The four image stimuli and the sound stimulus")

            self.soundFileNames.append(files[-1])
            self.soundObjs.append(sound.Sound(value = soundBaseDir + files.pop()))
 
            imageFileName = []
            #image objects for draw function
            imageObj = []
            
            #nth image per trial
            n = 0
            
            for fileName in files:
                
                id = os.popen("identify %s" % (imageBaseDir + fileName)).read()
                
                if id == '':
                    raise Exception('You need to install ImageMagick')

                m = re.search('([1-9]*)x([1-9]*)',id)
                width = float(m.group(1))
                height = float(m.group(2))

                if width > height:
                    imageObj.append(visual.PatchStim(self.win, 
                                                 tex = imageBaseDir + fileName,
                                                 units=self.units,
                                                 pos=(self.imageCoordinates[self.possibleLocations[self.numTrials][n]]),
                                                 size=(self.boxWidth - self.imageBuffer, (self.boxWidth / (width / height)) - self.imageBuffer)))
                else:
                    imageObj.append(visual.PatchStim(self.win, 
                                                 tex = imageBaseDir + fileName,
                                                 units=self.units,
                                                 pos=(self.imageCoordinates[self.possibleLocations[self.numTrials][n]]),
                                                 size=((self.boxHeight / (height / width)) - self.imageBuffer, self.boxWidth - self.imageBuffer)))
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
        self.win.flip()
        self.drawBoxes()
        
        self.currentTrialNum = self.order.pop(0)
        self.currentDuration = self.soundObjs[self.currentTrialNum].getDuration()
        self.soundStop = self.clock.getTime() + self.currentDuration
        self.drawImages(self.currentTrialNum)
        self.drawCrossHair()
        self.win.flip()
        self.soundObjs[self.currentTrialNum].play()
      

    def saveToFile(self,orderNum, startTime, endTime, posClicked, resultsBaseDir = './results_dir/'):
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
        f.write(str(self.imageFileNames[orderNum]) + '\t' + str(self.possibleLocations[orderNum]) + '\t' +  str(self.soundFileNames[orderNum]) + 
                '\t\t' + '%f' % startTime + '\t' + '%f' % endTime + '\t' + str(posClicked) + '\n')
        f.close()


    def boxClicked(self, pos):
        return ((pos[0] + self.absoluteMaxX)/ self.boxWidth - (self.numboxesX / 2), (pos[1] + self.absoluteMaxY) / self.boxHeight - (self.numboxesY / 2))
        

 
    def generatePermutations(self, n):
        n = n / self.images_multiple
        remainder = n % self.images_multiple
        s = set([0,1,2,3])
        imageArrangements = list(permutations(s, 2))
        
        permutList = []

        for arrangement in imageArrangements:
            arrangement = list(arrangement)
            arrangement.extend(s.difference(set(arrangement)))
            permutList.append(arrangement)

        permutList = permutList * n
        permutList += permutList[0:remainder]
        shuffle(permutList)
        return permutList

class Familiarization:

    def __init__(self, win, clock, units=None):
        self.win = win
        self.clock = clock
        self.units = units
        self.mouse = event.Mouse(visible=True, newPos=None, win=self.win)

        if (self.units == None):
            self.units = self.win.units

    def loadFamiliarization(self, filename='./familiarization', imageBaseDir = './image_dir'):
        
        self.familiarizationNames = []
        self.familiarizationImages = []

        percentOfSize = .5
        imageHeight = 0
        imageBuffer = 50
        fontSize = 60

        f = open(filename, 'r')
        lines = f.read().splitlines()

        for line in lines:
            elements = line.split(', ')

    
            #
            #
            #this is repeated code and should be abstracted out into 
            #another class. a utlity class should be created


            id = os.popen("identify %s" % (imageBaseDir + elements[1])).read()
            
            if id == '':
                raise Exception('You need to install ImageMagick')
            
            m = re.search('([1-9]*)x([1-9]*)',id)
            width = float(m.group(1))
            height = float(m.group(2))

            if (width > height):
                self.familiarizationImages.append(visual.PatchStim(win=self.win,
                                                               tex = imageBaseDir + elements[1],
                                                               units = self.units,
                                                               pos=(0,0),
                                                               size = (self.win.size[0] * percentOfSize, (self.win.size[1] * percentOfSize) / (width / height))))
                imageHeight = (self.win.size[1] * percentOfSize) / (width / height)
            else:
                self.familiarizationImages.append(visual.PatchStim(win=self.win,
                                                               tex = imageBaseDir + elements[1],
                                                               units = self.units,
                                                               pos=(0,0),
                                                               size = ((self.win.size[0] * percentOfSize) / (height / width), self.win.size[1] * percentOfSize)))
                imageHeight = self.win.size[1] * percentOfSize


            self.familiarizationNames.append(visual.TextStim(win = self.win,
                                                         text=elements[0],
                                                         units = self.units,
                                                         pos = (0,-(imageHeight / 2) - imageBuffer),
                                                         color = 'black',
                                                         height = fontSize))

                
                                                                          

    def run(self):
        self.loadFamiliarization(imageBaseDir='/home/ryan/research/WilsonLab/snodgrass-vanderwart/color/')

        for i in range(0, len(self.familiarizationImages)):
            self.win.flip()
            self.familiarizationImages[i].draw()
            self.familiarizationNames[i].draw()
            self.win.flip()
            waiting = True

            while waiting:
                
               if event.getKeys(['escape']): #quits experiment early
                   core.quit()
               elif event.getKeys(['space']):
                   waiting = False
                   

        
