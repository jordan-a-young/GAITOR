import cv2
import numpy as np
from ROIManager import ROIManager

"""
This object is given all the information it needs from the VideoAnalyzers.
It stores this info (the frames and the instances of video analyzer), then it
allows the user to go through all the rotations and roi settings. It sends the info
to the relevant analyzer as soon as it's completed. Once it's finished, main will
tell the video analyzers to begin analysis.

Pairs of analyzers with the first frames of their videos are added to the
analyzers list. do_rotations() does rotations for each video, saving the
rotated frame of the roi
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

	def set_rois(self, set_separate=False):
		# Call ROIManager to set roi for first element in analyzer
		roi = ROIManager(self.analyzers[0][1]).set_roi()
		
		# set_separate toggles whether batch will all have the same roi
		for pair in self.analyzers:
			if set_separate:
				roi = ROIManager(pair[1]).set_roi()
			
			pair[0].set_roi(roi)

	def run_analyses(self):
		# Run analyses for each analyzer
		for pair in self.analyzers:
			pair[0].analyze()
