# -*- coding: utf-8 -*-
"""
This is the main file for a python program used to analyze
paw prints of rats navigating a maze. This file contains the
functions used to start the analysis process. The
batch_management function runs all of the necessary functions
for setup, and then analysis.
"""

# GUI imports
import sys
import os
from PyQt5 import QtGui, QtCore, uic, QtWidgets
import mainGUI

import cv2
import numpy as np
import os.path
import glob
import random
import string
import time

from lib.VideoAnalyzer import VideoAnalyzer
from lib.SetUpManager import SetUpManager
from lib.Rotater import Rotater

"""
Sets up batch videos: gets folder, finds all videos in folder, and initializes
all the instances of read_video, adding them to a SetUpManager. Then it calls
the appropriate methods to complete set up and begin analysis.
You can set what extension of video it should look for. Defaults to .mp4 .
"""
class MyApp(QtWidgets.QStackedWidget,mainGUI.Ui_StackedWidget): 
    def __init__(self, parent=None):
        QtWidgets.QStackedWidget.__init__(self, parent)
        # make sure to add return StackedWidget to mainGUI.py
        StackedWidget = self.setupUi(self)
        self.startButton.clicked.connect(lambda: self.changePage(StackedWidget))

    def changePage(self,StackedWidget):
        StackedWidget.setCurrentIndex(1)
        self.chooseVideoDirButton.clicked.connect(lambda: self.batch_management(StackedWidget))

    def chooseFolder(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self,"Pick a folder")
        return directory

    def batch_management(self, StackedWidget, video_type='.MOV', should_rotate=False):
        directory = self.chooseFolder()

        # Get list of all files of type video_type in that folder
        video_paths = glob.glob(directory + '/*' + video_type)
        print video_paths

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
        
        StackedWidget.setCurrentIndex(2)
        # Set roi and run
        setup_manager.set_rois(StackedWidget)
        setup_manager.run_analyses()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp(None)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()