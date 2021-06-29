#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 18:47:31 2020

@author: lindadevoogd
"""

# General
import os
import sys
import numpy as np
import pandas as pd

# Basis for the GUI
#from PyQt5.QtGui     import *
#from PyQt5.QtCore    import *
#from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QInputDialog, QLineEdit, QSlider, QLabel

# Used to plot the data
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtCore
from matplotlib.figure import Figure

# Filter
import scipy.ndimage as ndimage

# ------------------------------------------------------------------------------

# Now adding defaults from a different file for easy access of settings
from defaults_PupCor_v2 import pupcor_settings


# ------------------------------------------------------------------------------

# Main window
class Window(QMainWindow):

    def __init__(self):

        super().__init__()


        # Get the settings
        self.inputdata = pupcor_settings()
        title = "PupCor"
        
        # GUI
        top = self.inputdata.top
        left = self.inputdata.left
        self.width = self.inputdata.width
        self.height = self.inputdata.height
        self.setWindowTitle(title)
        self.setGeometry(top, left, self.width, self.height)
        self.setFixedSize(self.width, self.height)

        # Run GUI
        self.MyUI()

    def MyUI(self):
        
        # Add plot, entire time course
        self.canvas_tc = PlotCanvas(self,
                                    width=(self.width * .85) / 100,
                                    height=(self.height * .5) / 100)
        self.canvas_tc.move(self.width / 8, 0)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar(self.canvas_tc, self))

        # Add plot, trial by trial
        self.canvas_tr = PlotCanvasTrials(self,
                                          width=(self.width * .85) / 100,
                                          height=(self.height * .3) / 100)
        self.canvas_tr.move(self.width / 8, (self.height / 2) + self.height / 10)

        # Draw Line

        
        # Add buttons > time course [tc plot]
        x_left = self.width / 60
        y_start = self.width / 60
        self.makebutton("Get data", x=x_left, y=y_start,
                        do_action=self.get_data)
        self.makebutton("Interpol val", x=x_left, y=y_start * 6,
                        do_action=self.canvas_tc.changeinterpol)
        self.makebutton("Get blinks", x=x_left, y=y_start * 7,
                        do_action=self.canvas_tc.do_interpol)
        
        self.nameLabel1 = QLabel('Manual changes:', self)
        self.nameLabel1.setFont(QFont('Arial', 8))
        self.nameLabel1.move(x_left,y_start * 8)
        
        self.makebutton("Remove", x=x_left, y=y_start * 9,
                        do_action=self.canvas_tc.do_man_interpol)
        self.makebutton("Restore", x=x_left, y=y_start * 10,
                        do_action=self.canvas_tc.do_man_restore)
        
        self.nameLabel1 = QLabel('Others:', self)
        self.nameLabel1.setFont(QFont('Arial', 8))
        self.nameLabel1.move(x_left,y_start * 11)
        
        self.makebutton("Smooth", x=x_left, y=y_start * 12,
                        do_action=self.canvas_tc.dosmooth)
        self.makebutton("Save", x=x_left, y=y_start * 13,
                        do_action=self.canvas_tc.save)
        
        #--window
        self.nameLabel = QLabel('Interpolate blinks:', self)
        self.nameLabel.setFont(QFont('Arial', 10))
        self.nameLabel.move(x_left,y_start * 3)

        mySlider = QSlider(Qt.Horizontal, self)
        mySlider.setGeometry(x_left, y_start * 4, 120, 30)
        mySlider.setMinimum(1)
        mySlider.setMaximum(5)
        mySlider.setValue(3)
        mySlider.setTickInterval(1)
        mySlider.setTickPosition(QSlider.TicksBelow)
        
        
        mySlider.valueChanged[int].connect(self.canvas_tc.slidervalue2)
        mySlider.setSingleStep(10)
        #---


        # Add buttons > trials [tr canvas]
        self.makebutton("Get trials", x=x_left, y=((self.height / 2) + self.height / 10) + y_start,
                        do_action=self.get_trials)  # self.canvas_tr.get_trials)
        self.makebutton(">", x=x_left, y=((self.height / 2) + self.height / 10) + y_start * 2,
                        do_action=self.canvas_tr.trialup)
        self.makebutton("<", x=x_left, y=((self.height / 2) + self.height / 10) + y_start * 3,
                        do_action=self.canvas_tr.trialdown)
        self.makebutton("Accept", x=x_left, y=((self.height / 2) + self.height / 10) + y_start * 4,
                        do_action=self.canvas_tr.accepttrial)
        self.makebutton("Reject", x=x_left, y=((self.height / 2) + self.height / 10) + y_start * 5,
                        do_action=self.canvas_tr.rejecttrial)
        self.makebutton("Save", x=x_left, y=((self.height / 2) + self.height / 10) + y_start * 6,
                        do_action=self.canvas_tr.save)

        self.fileLabel = QLabel('file name', self)
        self.fileLabel.move(x_left,((self.height / 2) + self.height / 10) + y_start * 10)

    def change_label(self):

        nameoffile = self.canvas_tc.filename[0].rstrip(os.sep)
        head, tail = os.path.split(nameoffile)
        self.fileLabel.setText(tail)

    def makebutton(self, tekst, x, y, do_action):
        """
        Function to make a button to not repeate code
        """
        button = QPushButton(tekst, self)
        button.move(x, y)
        if do_action:
            button.clicked.connect(do_action)
        if tekst == "Reject":
            button.setStyleSheet("color:rgb(125,60,60)")
        elif tekst == "Accept":
            button.setStyleSheet("color:rgb(60,125,60)")

    # Run trial analysis in other class, this contructions allows the
    # two PlotCanvas' to communicate [tc = time course, tr =  trial]
    def get_data(self):

        # Clear the plots in case of reopening a new file
        self.canvas_tc.axes.cla()
        self.canvas_tc.draw()
        self.canvas_tr.axes.cla()
        self.canvas_tr.draw()

        # Get data
        try:
            self.canvas_tc.get_data()
            self.change_label()
        except:
            "No file was selected"
            
    def get_trials(self):
        
        self.canvas_tc.int_pupdat
        self.canvas_tr.get_trials()
        self.canvas_tr.update_trials(self.canvas_tc.pupdat, self.canvas_tc.int_pupdat, self.canvas_tc.smooth_int_pupdat)


# ------------------------------------------------------------------------------

# Canvas for plotting
class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=5, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor([.92, .92, .92])  # Color of the plot canvas
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        # Get data classes
        self.inputdata = pupcor_settings()
        self.sF=self.inputdata.Hz
        
        # General settings
        self.rawdat = self.inputdata.rawdat
        self.pupdat = self.inputdata.pupdat
        self.int_pupdat= self.inputdata.int_pupdat
        self.smooth_int_pupdat = self.inputdata.smooth_int_pupdat
        
        # Interpolation settings
        self.win_ave=self.inputdata.win_ave # how many samples used for averaging
        self.blinkval=self.inputdata.blinkval # samples with 0's are blinks [change this in the GUI]
        self.win_lim=self.inputdata.win_lim # minimum difference between eye blink events
        
        # Smoothing settings
        self.smoothval=self.inputdata.smoothval # smoothing parameter
        self.plotsmooth=self.inputdata.plotsmooth # 0/1 indicates whether it should be plotted

    def slidervalue1(self, value):
        
        pass #self.blinkval=value*1000
        
    def slidervalue2(self, value):
        
        # Update interpolation settings based on the slide
        self.win_ave=value*5
        self.win_lim=int(self.win_ave*2)
        
    def ds_tobii_data(self):
    
        newpup=[]
        
        # Take sample 1,2,3 > only one of those is a valid sample but Tobii 
        # does this inconsistantly, therefore try all and take the valid sample
        pupdat_1=self.pupdat[0::3]
        pupdat_2=self.pupdat[1::3]
        pupdat_3=self.pupdat[2::3]
        
        for c,val in enumerate(pupdat_1):
            temp=[pupdat_1[c], pupdat_2[c], pupdat_3[c]]
            
            newpup.append(np.max(temp))
        
        self.pupdat = newpup   
        
    def get_data(self):

        # Get datafile
        self.filename = QFileDialog.getOpenFileName(self,
                                                    'Open a data file', '.', 'Files (*.asc *.tsv);;All Files (*.*)')
        
        
        flname, file_extension = os.path.splitext(self.filename[0])
        
        f = open(self.filename[0], 'r')
        self.rawdat=f.readlines()


        if file_extension == '.asc': # eye link converted ascii file
        
            # Get the sample frequency
            rcd_line=[line for cnt, line in enumerate(self.rawdat) if "RECCFG" in line]
            sampleline=rcd_line[0].split()
            self.eyelink_sF=int(sampleline[4])
            print('Your sample freq is ' + str(self.eyelink_sF) + ' Hz and will be downsamled to 50 Hz')
        
            # remove lines [script crashes when these lines are in there]
            for rmstr in ["EFIX","ESACC","SFIX","SSACC","SBLINK","EBLINK","END"]:
                self.rawdat = [line for line in self.rawdat if not rmstr in line]
            
            # take the pupil diameter
            dat=[ [], [], [], [] ]
            self.rawevt=[]
            
            #get recording line so everything  before will be removed
            rcd_line=[cnt for cnt, line in enumerate(self.rawdat) if "SAMPLES" in line]
            
            # remove those lines from rawdata
            self.rawdat = self.rawdat[rcd_line[-1]+1:]
            
            # get events and make vector
            for c,line in enumerate(self.rawdat):
                #if c>rcd_line[-1]: # just throws away lines before calibration [but might be file specific]
    
                if "MSG" in line:
                    self.rawevt.append(line)
                else:
                    spt_line=line.split('\t')
                    for cc,dd in enumerate(spt_line):
                        if cc<4:
                            dat[cc].append(dd.strip('  '))
            
            #get pupil dilation
            self.pupdat = [int(float(x)) for x in dat[3]]
    
            #down sample to 50 HZ
            downsF=int(self.eyelink_sF/self.sF)
            self.pupdat=self.pupdat[0::downsF]
            
            
        elif file_extension == '.tsv': #Tobii implementation
            
            self.blinkval=-1 #Tobii sets blinks to -1
            
            header = self.rawdat[0].split()
            dat = [[] for val in header]
            
            for c,line in enumerate(self.rawdat[1:]):
                
                spt_line=line.split('\t')
                
                for cc,dd in enumerate(spt_line):
                    dat[cc].append(dd.strip('  '))
            
            #get pupil dilation
            if self.inputdata.whichside=='Left':
                which_side=[c for c,val in enumerate(header) if val=='PupilSizeLeft'] 
                self.pupdat = [float(x) for x in dat[which_side[0]]] 
            elif self.inputdata.whichside=='Right':
                which_side=[c for c,val in enumerate(header) if val=='PupilSizeRight'] 
                self.pupdat = [float(x) for x in dat[which_side[0]]] 
            elif self.inputdata.whichside=='Mean':
                which_sideL=[c for c,val in enumerate(header) if val=='PupilSizeLeft'] 
                which_sideR=[c for c,val in enumerate(header) if val=='PupilSizeRight'] 
                self.pupdatL = [float(x) for x in dat[which_sideL[0]]] 
                self.pupdatR = [float(x) for x in dat[which_sideR[0]]] 
                self.pupdat=[(val+self.pupdatL[c])/2 for val in self.pupdatR]
            
            # Tobii records only every 3rd sample
            #OLD way which did not work well for all data: self.pupdat = self.pupdat[0::3]
            self.ds_tobii_data()
            
            # Remove highfreq noise from Tobii data with a rolling average
            rol_val=self.inputdata.rol_val
            pupdat_nan=[np.nan if val==-1 else self.pupdat[c] for c,val in enumerate(self.pupdat)]
            df = pd.DataFrame(pupdat_nan)
            pupdat_nan_sm = df.rolling(rol_val, min_periods=1).mean()
            pupdat_nan_sm = pupdat_nan_sm[0].values.tolist()
            pupdat_nan_sm= pupdat_nan_sm[int(rol_val/2):] + [-1] * int(rol_val/2)
            self.pupdat=[-1 if val==-1 else pupdat_nan_sm[c] for c,val in enumerate(self.pupdat)] # Put back blinks [-1]


        self.axes.cla()
        self.axes.plot(self.pupdat, c='C0')
        self.draw()


    def get_eyeblinks(self):
        
        """Get eye blinks for interpolation"""
                       
        if self.blinkval < max(self.pupdat):
            
            # make empty
            self.interpol_evt_str=[]
            self.interpol_evt_end=[]
            
            # Get events based on input value, 0 == a blink, 
            if self.blinkval==0:
                interpol_vec=[int(x==0) for x in self.pupdat] 
            elif self.blinkval==-1: #-1 blink in Tobii data
                interpol_vec=[int(x==-1) for x in self.pupdat] 
            else:
                interpol_vec=[int(x<self.blinkval) for x in self.pupdat] 
                          
            # Do not do this for the beginning and end
            interpol_vec[0:self.win_lim]=[0]*self.win_lim
            interpol_vec[-self.win_lim+1:-1]=[0]*self.win_lim
            
            # Get start and end of each interpolation window
            for c, num in enumerate(np.diff(interpol_vec)):
                if num == 1:
                    self.interpol_evt_str.append(c+1)
                elif num == -1:
                    self.interpol_evt_end.append(c)
            
            # Remove last start value if there is more than end
            if len(self.interpol_evt_str)>len(self.interpol_evt_end):
                self.interpol_evt_str.pop()
            
            #remove "eyeblinks" occure to close in time
            for c, num in enumerate(self.interpol_evt_str): 
                if c<len(self.interpol_evt_str)-1:
                    if (self.interpol_evt_str[c+1]-self.interpol_evt_end[c])<self.win_lim:
                        self.interpol_evt_str[c+1]=0
                        self.interpol_evt_end[c]=0
                   
            #remove zero's        
            self.interpol_evt_str=[num for num in self.interpol_evt_str if num!=0]
            self.interpol_evt_end=[num for num in self.interpol_evt_end if num!=0]
            
            # Print how much data is interpolated
            prop_int=sum(interpol_vec)/len(self.pupdat)
            print("% of invaled samples is " + str(prop_int*100) + " %")
            
        else:
            
            print('Your cut off value is too high, please plot pupdat and check which value you should use!')
            
    def do_interpol(self):

        # Check if there is data
        try:
            self.pupdat
        
        except:
            
            print("Please load data first")
        
        else:
            
            #Get eye blinks
            self.get_eyeblinks()
            
            #
            self.plotsmooth=0
                
            #copy
            self.int_pupdat=self.pupdat[:]
            
            #treat first differently when smaller that the window
            if self.interpol_evt_str[0]<self.win_ave:
                
                #temp window length till end of data
                win_ave_end=len(self.pupdat)-self.interpol_evt_str[-1]-1
                
                 # Define interpolation value [average of -X window]
                str_val=self.pupdat[self.interpol_evt_str[0]-1]
                end_val=self.pupdat[self.interpol_evt_end[0]+self.win_ave]
                
                # Define the gap that needs to be filled [half the start window to half the end window]
                gap_val=(self.interpol_evt_end[0]+self.win_ave)-(self.interpol_evt_str[0]-1)
                int_val=(end_val-str_val)/gap_val
                
                # interpolate
                for c_sam in range((self.interpol_evt_str[0]-1),(self.interpol_evt_end[0]+self.win_ave)+1):
                    self.int_pupdat[c_sam]=self.int_pupdat[c_sam-1]+int_val
                
                #remove from the list
                self.interpol_evt_str.pop(0)
                self.interpol_evt_end.pop(0)
            
            #treat last differently when smaller that the window
            if len(self.pupdat)-self.interpol_evt_end[-1]<self.win_ave:
                
                #temp window length till end of data
                win_ave_end=len(self.pupdat)-self.interpol_evt_end[-1]-1
                
                # Define interpolation value [average of -X window]
                str_val=self.pupdat[self.interpol_evt_str[-1]-self.win_ave]
                end_val=self.pupdat[self.interpol_evt_end[-1]+win_ave_end]
                
                # Define the gap that needs to be filled [half the start window to half the end window]
                gap_val=(self.interpol_evt_end[-1]+win_ave_end)-(self.interpol_evt_str[-1]-self.win_ave)
                int_val=(end_val-str_val)/gap_val
            
                # interpolate
                for c_sam in range((self.interpol_evt_str[-1]-self.win_ave),(self.interpol_evt_end[-1]+win_ave_end)+1):
                    self.int_pupdat[c_sam]=self.int_pupdat[c_sam-1]+int_val
                    
                self.interpol_evt_str.pop()
                self.interpol_evt_end.pop()
            
            # Loop over interpolation start values
            for c_evt, n_evt in enumerate(self.interpol_evt_str):
                
                # Define interpolation value [average of -X window]
                str_val=self.pupdat[self.interpol_evt_str[c_evt]-self.win_ave]
                end_val=self.pupdat[self.interpol_evt_end[c_evt]+self.win_ave]
                
                # Define the gap that needs to be filled [half the start window to half the end window]
                gap_val=(self.interpol_evt_end[c_evt]+self.win_ave)-(self.interpol_evt_str[c_evt]-self.win_ave)
                int_val=(end_val-str_val)/gap_val
            
                # interpolate
                for c_sam in range((self.interpol_evt_str[c_evt]-self.win_ave),(self.interpol_evt_end[c_evt]+self.win_ave)+1):
                    self.int_pupdat[c_sam]=self.int_pupdat[c_sam-1]+int_val

            # plot
            self.remove()
            self.plotall()

    def dosmooth(self):
        
        if self.plotsmooth==0:
            self.smoothval, ok = QInputDialog.getInt(self, "Input", "How much smoothing::", self.smoothval, 0,
                                                              20000, 1)
            
            self.smooth_int_pupdat=ndimage.filters.gaussian_filter(self.int_pupdat,self.smoothval)
            
            self.plotsmooth=1
            
        elif self.plotsmooth==1:
            
            self.plotsmooth=0
        
        # Replot
        self.remove()
        self.plotall()

    def changeinterpol(self):

        self.blinkval, ok = QInputDialog.getInt(self, "Input", "Interpol for < val [f.e. 0/-1 == blink]:", self.blinkval, -20000,
                                                20000, 1)

        
        # Replot
        self.remove()
        self.plotall()

    def do_man_interpol(self):

        # get xaxis
        x = self.axes.get_xlim()
        x = list(x)

        # collect area
        self.interpol_evt_str=[int(x[0])]
        self.interpol_evt_end=[int(x[1])]
        
        # only interpolate when data is within the window to prevent errors when
        # zoomed in on the edges
        
        # Loop over interpolation start values
        for c_evt, n_evt in enumerate(self.interpol_evt_str):
            
            # Define interpolation value [average of -X window]
            str_val=self.pupdat[self.interpol_evt_str[c_evt]-self.win_ave]
            end_val=self.pupdat[self.interpol_evt_end[c_evt]+self.win_ave]
            
            # Define the gap that needs to be filled [half the start window to half the end window]
            gap_val=(self.interpol_evt_end[c_evt]+self.win_ave)-(self.interpol_evt_str[c_evt]-self.win_ave)
            int_val=(end_val-str_val)/gap_val
        
            # interpolate
            for c_sam in range((self.interpol_evt_str[c_evt]-self.win_ave),(self.interpol_evt_end[c_evt]+self.win_ave)+1):
                self.int_pupdat[c_sam]=self.int_pupdat[c_sam-1]+int_val

        # Replot
        self.plotsmooth=0
        self.remove()
        self.plotall()

    def do_man_restore(self):

        # get xaxis
        x = self.axes.get_xlim()
        x = list(x)

        # collect area
        self.interpol_evt_str=[int(x[0])]
        self.interpol_evt_end=[int(x[1])]
        
        # only interpolate when data is within the window to prevent errors when
        # zoomed in on the edges
        
        # Loop over interpolation start values
        for c_evt, n_evt in enumerate(self.interpol_evt_str):
            
            # Define interpolation value [average of -X window]
            self.int_pupdat[n_evt:self.interpol_evt_end[c_evt]]=self.pupdat[n_evt:self.interpol_evt_end[c_evt]]

        # Replot
        self.plotsmooth=0
        self.remove()
        self.plotall()
        
    def remove(self):
       
        self.axes.lines=[]

    def plotall(self):

        # Plot
        self.axes.plot(self.pupdat, c='C0')
        self.axes.plot(self.int_pupdat, 'y')
        if self.plotsmooth==1:
            self.axes.plot(self.smooth_int_pupdat, 'C2')
        self.draw()

    def openfile(self, file):
        
        # Extract data from the file
        dat = []
        with open(file) as f:
            print(f)
            for line in f:
                print(line)
                line = line.split('\n')
                dat.append(float(line[0]))
        
        return dat

    def save(self):

        try:

            # Split path and file for saving
            path, file = os.path.split(self.filename[0])

            # Create output directory
            if not os.path.exists(os.path.join(path, 'PupCor_output')):
                os.makedirs(os.path.join(path, 'PupCor_output'))

            # Create file and save in PulseCor_output directory
            newname = os.path.join(path, "PupCor_output", file[:-4] + "_int_pup.txt")
            print(newname)
            thefile = open(newname, 'w')
            for item in self.int_pupdat:
                thefile.write("%s\n" % int(item))
            thefile.close()
            
            newname = os.path.join(path, "PupCor_output", file[:-4] + "_smth_int_pup.txt")
            thefile = open(newname, 'w')
            for item in self.smooth_int_pupdat:
                thefile.write("%s\n" % int(item))
            thefile.close()

        except:
            pass


# Canvas for plotting
class PlotCanvasTrials(FigureCanvas):

    def __init__(self, parent=None, width=5, height=5, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor([.92, .92, .92])  # Color of the plot canvas
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        # Extra settings
        self.trnum = 0
        self.trialsaccepted = []

        # Get data classes
        self.inputdata = pupcor_settings()

    def get_trials(self):

        # Get stimulus onset times
        self.stimonset = self.openfile()

        # Get baseline and stimulus duration in seconds
        self.inputdata.baseline, ok = QInputDialog.getInt(self, "Input", "Baseline in sec:", self.inputdata.baseline, 0,
                                                          20000, 1)
        self.inputdata.stimduur, ok = QInputDialog.getInt(self, "Input", "Stim duration in sec:",
                                                          self.inputdata.stimduur, 0, 20000, 1)

        # Make vector with 1's for accepted trials
        self.trialsaccepted = np.ones(len(self.stimonset))

    def update_trials(self, pupdat, int_pupdat, smooth_int_pupdat):
        """
        Fuction is neccessary to make the 2 plots communicate
        """
        self.pupdat = pupdat
        self.int_pupdat = int_pupdat
        self.smooth_int_pupdat = smooth_int_pupdat

        self.plot_trials()

    def plot_trials(self):

        # Get first trial
        tr_onset = int(self.stimonset[self.trnum] - self.inputdata.Hz * self.inputdata.baseline)
        adj_stimduur = self.inputdata.Hz * self.inputdata.stimduur
        tr_offset = int(self.stimonset[self.trnum] + adj_stimduur)

        # Cut out data
        self.trialdat = self.pupdat[tr_onset:tr_offset]
        self.inttrialdat = self.int_pupdat[tr_onset:tr_offset]
        self.s_inttrialdat = self.smooth_int_pupdat[tr_onset:tr_offset]

        # Clear plot
        self.axes.cla()

        # Plot first trial
        if self.trialsaccepted[self.trnum] == 1:
            self.axes.plot(self.trialdat, c='C0')
        else:
            self.axes.plot(self.trialdat, c='gray')
       
        if self.trialsaccepted[self.trnum] == 1:
            self.axes.plot(self.inttrialdat, 'y')
        else:
            self.axes.plot(self.inttrialdat, 'gray')

        if self.trialsaccepted[self.trnum] == 1:
            self.axes.plot(self.s_inttrialdat, 'C2')
        else:
            self.axes.plot(self.s_inttrialdat, 'gray')
        self.draw()

    def trialup(self):

        try:

            self.trnum += 1

            if self.trnum >= len(self.stimonset):
                self.trnum = len(self.stimonset) - 1

            self.plot_trials()

        except AttributeError:

            pass

    def trialdown(self):

        try:

            self.trnum -= 1

            if self.trnum < 0:
                self.trnum = 0

            self.plot_trials()

        except AttributeError:

            pass

    def accepttrial(self):

        try:

            self.trialsaccepted[self.trnum] = 1
            self.plot_trials()

        except IndexError:

            pass

    def rejecttrial(self):

        try:

            self.trialsaccepted[self.trnum] = 0
            self.plot_trials()

        except IndexError:

            pass

    def openfile(self):

        # Get datafile
        self.filename = QFileDialog.getOpenFileName(self,
                                                    'Open a data file', '.', 'TXT files (*.txt);;All Files (*.*)')

        try:
            # Extract data from the file
            dat = []
            with open(self.filename[0]) as f:
                for line in f:
                    line = line.split('\n')
                    dat.append(float(line[0]))
            return dat

        except:

            pass

    def save(self):

        try:

            path, file = os.path.split(self.filename[0])

            # Create output directory
            if not os.path.exists(os.path.join(path, 'PupeCor_output')):
                os.makedirs(os.path.join(path, 'PupCor_output'))

            # Create file and save in PulseCor_output directory
            newname = os.path.join(path, "PupCor_output", file[:-4] + "_acceptedtrials.txt")
            thefile = open(newname, 'w')
            for item in self.trialsaccepted:
                thefile.write("%s\n" % int(item))
            thefile.close()

        except:

            pass


# RUN
# ------------------------------------------------------------------------------

app = QApplication(sys.argv)
window = Window()
window.show()
app.exec()

