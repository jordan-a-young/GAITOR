import cv2
import numpy as np
from ROIManager import ROIManager

"""
This class is used to setup the videos for analysis. It handles
ROI selection as well as adding the VideoAnalysis object for
each video to list of analyzers.
"""
class SetUpManager():
	def __init__(self):
		# A list that stores analyzers
		self.analyzers = []

	def add_analyzer(self, analyzer, firstframe):
		# Add analyzer to list of analyzers
		self.analyzers.append([analyzer, firstframe])

	def do_rotations(self):
		for pair in self.analyzers:
			# Get rotation matrix and set it for analyzer
			mat = Rotater(pair[1]).rotate_image()
			pair[0].set_rotation_matrix(mat)
			
			# Perform rotation based on matrix
			rows, cols = pair[1].shape
			pair[1] = cv2.warpAffine(pair[1], mat, (cols, rows))

	def set_rois(self, StackedWidget, set_separate=False):
		# Call ROIManager to set roi for first element in analyzer
		# roi = ROIManager(self.analyzers[0][1], StackedWidget).set_roi()
		roiMgr = ROIManager(self.analyzers[0][1], StackedWidget)
		roiMgr.set_roi()
		roi = roiMgr.get_roi()
		
		# set_separate toggles whether the batch will all have the same roi
		for pair in self.analyzers:
			if set_separate:
				# roi = ROIManager(pair[1], StackedWidget).set_roi()
				roiMgr = ROIManager(pair[1], StackedWidget)
				roiMgr.set_roi()
				roi = roiMgr.get_roi()
			
			pair[0].set_roi(roi)

	def run_analyses(self):
		# Run analyses for each analyzer
		for pair in self.analyzers:
			quitPressed = pair[0].analyze()
