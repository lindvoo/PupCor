# PupCor
a simple python-based GUI to preprocess and manually correct pupil data 

You just need to download the "PupCor_v3.py" and "defaults_PupCor_v3.py" files and install the dependencies.

It is a very simply nothing fancy, easy to use GUI to get interpolated (and smoothed) pupil data [for the EyeLink (.asc files), Tobii (.tsv files), and already converted SMI red500 (.txt files) eyetrackers for now]. In addition there is an option to go through the time course on a trial-by-trial basis [not yet tested for the Tobii data], for which you need a file containing the times of the markers (eg onset of your stimuli). You can use this to manually accept or reject trial in case the data for that trial is not usable (eg someone closed there eyes for some time).

Notes for Tobii data: I have noticed this contains some high freq noise probably due to limited accuracy in sampling? so when the Tobii data is read in an rolling average is applied to get rid of this and facilitate interpolation. When this setting is set to [1] no rolling average is applied.

Notes for SMI red500: X and Y data seem to be the same so now only one is used but could be changed.

# TIME COURSE
These are the steps you can follow:

1) PupCor requires the pupil data to be in an .asc or .tsv file. You would first need to convert the .edf files to .asc using the edf2asc tool from eyelink

2) The "Get blinks" button can be used to interpolate eye blinks, there is a slider that can be used to change the length of the interpolation [in addition if this does not work well on your data you can change the default setting in the defaults file]. In addition, the "Interpol val" button lets you pick from which value you want to interpolate the data. The default value [which are the blinks] for the Eyelink is [0] and Tobii [-1], but based on the y-axis you can manually change this value using this button as I have noticed somethinges a blink is fe partial so it does not drop to [0]. 

3) "Remove" can be used to manually interpolate a piece of data. Zoom in to the part you would like to interpole and click "Remove"

4) "Restore" can be used to restore the interpolated data to go back to the raw data

5) "Peak frequency" slider can be used to change the distance between peak to be detected, you can use this to see if the peak detection gets better with a different freqiuency. It us adviced to do that before starting with manual correcting

6) "Save" will save the interpolated an smoothed data in a new file in a folder called "Pup_output" which is located in the folder your original file is

> you can save throught the correction and you can even close the file and when re-opening it it will load the interpolated an smoothed data.

# TRIAL DATA
These are the steps you can follow:

1) Select a .txt file that contains one column with times (ie should be in the sample frequency of the time course)

2) With the "<" and ">" arrows you can click though the trials

3) With "Accept" and "Reject" you can accept or reject a trail. If you reject a trial the data will be plotted in gray.

4) "Save" it will output a file with 1 and 0 corresponding with your Accept and Reject decision

This is an example of how the GUI looks like:
![Example 1](Pup_example.png)
