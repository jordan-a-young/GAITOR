# -*- coding: utf-8 -*-
"""
Created on Wed Mar 09 20:52:23 2016

Takes a single folder full of videos of the gait analysis set up and scores
them. Is not able to detect pauses, so videos with those should be manually
eliminated before or after this script. If the rat behaves strangely - turning
around, pausing, placing its tail on the ground, ect, the scoring can become
quite messy and get rather slow. A video can be exited without finishing
scoring at any time by pressing 'q'. Used to run faster before I reduced
the combining area, but some sacrifices must be made for accuracy. This is
fairly well commented, but not as thoroughly as some of the labs other
scripts as it's very long. Areas you may want to change include: turning on
rotation - if you want the option to rotate the videos (if you recorded at
an angle), you can set that in the call under main. If you want to set all rois
separately for each video, call set_rois with the additional set_separate = True.
If you want to change the distance for contours to be considered part of the
same paw, which might be necessary if recording at a different size or maybe
if recording with much different size rats, ect, that should be changed in
the call to find_if_close in the analyze method of VideoAnalyzer. Changing the
threshold for edge detections can also be done in the analyze method. This
could allow you to put the numbers higher if you're getting detection of light
objects you don't want, or to put them lower if you're missing detection
of lighter objects you do want. The first number indicates the number below
which something is considered definitely not an edge, and the second number
indicates the number above which something is considered definitely an edge.
Numbers in the middle are only counted as edges if they're connected to something
higher than the second number.

@author: Hayley Bounds
"""

import cv2
import numpy as np
import Tkinter as tk
import tkFileDialog
import os.path
import glob
import random
import string

from VideoAnalyzer import VideoAnalyzer
from SetUpManager import SetUpManager
from Rotater import Rotater

"""
Lets the user pick a folder that will contain all the videos to be
analyzed. The root manipulations are necessary for a clean close-out.

Output: a string that is the full path to the folder the user chooses.
"""
def pick_folder():
	# Use tk to create file dialog to select directory
	root = tk.Tk()
	root.update()
	folder = tkFileDialog.askdirectory(title='Choose a Folder')
	root.destroy()
	return folder

"""
Sets up batch videos: gets folder, finds all videos in folder, and initializes
all the instances of read_video, adding them to a SetUpManager. Then it calls
the appropriate methods to complete set up and begin analysis.
You can set what extension of video it should look for. Defaults to .mp4 .
"""
def batch_management(video_type='.mp4', should_rotate=False):
	# Get directory for videos
	folder = pick_folder()
	
	# Get list of all files of type video_type in that folder
	video_paths = glob.glob(folder + '/*' + video_type)
	
	if len(video_paths) < 1:
		print 'No videos found!'
		return

	np.random.shuffle(video_paths)
	setup_manager = SetUpManager()

	# Initialize and add analyzer
	for path in video_paths:
		video_analyzer = VideoAnalyzer(path)
		setup_manager.add_analyzer(video_analyzer, video_analyzer.get_ff())

	# Rotate if needed
	if should_rotate:
		setup_manager.do_rotations()
	
	# Set roi and run
	setup_manager.set_rois()
	setup_manager.run_analyses()


if __name__ == '__main__':
	batch_management()
