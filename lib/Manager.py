import cv2
import Tkinter as tk
import tkFileDialog as tkFile
from ROIManager import ROIManager
from Tracker import Tracker
import numpy as np

class Manager():
	def __init__(self):
		# Get first frame, file_name, and setup roi
		self.first_frame = self.get_first_frame()
		self.roi_manager = ROIManager(self.first_frame)
		self.select_roi()
		
		# Init tracker and start reading
		self.tracker = Tracker(self.file_name, self.get_roi())

		print 'Manager class initialized'

	"""
	Purpose: Lets the user pick a folder that contains videos
	Output: a string that is the full path to the folder the user chooses.
	"""
	def select_folder(self):
		root = tk.Tk()
		root.update()
		folder = tkFileDialog.askdirectory(title='Choose a Folder')
		root.destroy()
		return folder

	"""
	Purpose: Let the user select a video to be used
	Output: a string with the file name to be used
	"""
	def select_video(self):
		root = tk.Tk()
		root.update()

		file_opt = {}
		file_opt['defaultextension'] = ' .MP4'
		file_opt['filetypes'] = [('all files', '.*'),('text files','.MP4')]
		file_opt['initialdir'] = 'c:\Users\\'
		file_opt['initialfile'] = ' '

		# file name
		self.file_name = tkFile.askopenfilename(**file_opt)
		print "File chosen: %s" % self.file_name

		root.destroy()
		return self.file_name

	def select_roi(self):
		return self.roi_manager.set_roi()

	def get_roi(self):
		return self.roi_manager.get_roi()

	def get_file_name(self):
	 	return self.file_name

	def get_first_frame(self):
		self.select_video()
		cap = cv2.VideoCapture(self.file_name)
		frame = None

		while True:
			ret, frame = cap.read()

			if not ret:
				print "Video could not be loaded."
				break
			if frame.any():
				print "Frame found."
				break

		cap.release()
		return frame

	def start_tracker(self):
		self.tracker.read_video()