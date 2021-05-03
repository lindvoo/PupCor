#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 09:05:25 2021

@author: lindadevoogd
"""


# Settings
class pupcor_settings():
    
    def __init__(self):
        
        self.which_eyetracker='Tobii' #[EyeLink / Tobii]
        
        # GUI settings [generally you do not need to change this but if you 
        # are unhappy with the size or position on the screen you can change this]
                
        self.top = 20
        self.left = 20
        self.width = 1300
        self.height = 800
        
        # General settings
        self.rawdat = []
        self.pupdat = []
        self.int_pupdat= []
        self.smooth_int_pupdat = []
        
        # Interpolation settings [this is linked to the slider and can be updated
        # within the GUI, but if the interpolation still does not work well you 
        # can try to change these settings]
        self.win_ave=15 # how many samples used for averaging before/after blink
                        # this value van be changed in steps of 5
                        # 15 is the middle value and slide ranges 5-25
        self.blinkval=0
        self.win_lim=int(self.win_ave*2) # minimum difference between eye blink 
                                         # events > should be bigger than win_ave 
        
        # Smoothing defaults [can be flexibly changed within the GUI]
        self.smoothval=5
        self.plotsmooth=0

        # Trial data
        self.baseline = 1  # seconds > can be changed in GUI
        self.stimduur = 6  # seconds > can be changed in GUI
        
        # Define sample frequency > is used f.e. for trial-by-trail data and other convertion of sec to samples
        if  self.which_eyetracker == 'Tobii':
             self.Hz=40 #standard sample frequency?
        elif self.which_eyetracker == 'EyeLink':
            self.Hz=50 #EyeLink data will be downsampled to 50 hz
        
        # Tobii settings
        self.whichside='Mean' # Pick your eye: Left, Right, Mean
        self.rol_val=10 # rolling average for removing Tobii high freq noise, 
                        # 10 seems to work well [1=no smoothing] note: as rolling average
                        # shifts the signal the signal is put back in time to account
                        # for this
