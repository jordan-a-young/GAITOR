# -*- coding: utf-8 -*-
"""
This is the main file for a python program used to analyze
paw prints of rats navigating a maze. This file contains the
functions used to start the analysis process. The
batch_management function runs all of the necessary functions
for setup, and then analysis.
"""

import cv2
import numpy as np
import Tkinter as tk
import tkFileDialog
import os.path
import glob
import random
import string

from lib.VideoAnalyzer import VideoAnalyzer
from lib.SetUpManager import SetUpManager
from lib.Rotater import Rotater

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
def batch_management(video_type='.MOV', should_rotate=False):
	# Get directory for videos
	folder = pick_folder()
	
	# Get list of all files of type video_type in that folder
	video_paths = glob.glob(folder + '/*' + video_type)

	if len(video_paths) < 1:
		print 'No videos found!'
		return

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
