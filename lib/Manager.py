import cv2
import Tkinter as tk
import tkFileDialog as tkFile
from ROIManager import ROIManager
import numpy as np

class Manager():
	def __init__(self):
		self.first_frame = self.get_first_frame()
		self.roi_manager = ROIManager(self.first_frame)
		self.tracker = Tracker()
		self.create_trackbars()
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
		file_name = tkFile.askopenfilename(**file_opt)

		root.destroy()
		return file_name

	def select_roi(self):
		return self.roi_manager.set_roi()

	def get_roi(self):
		return self.roi_manager.get_roi() 

	def get_first_frame(self):
		file_name = self.select_video()
		print "File chosen: %s" % file_name

		cap = cv2.VideoCapture(file_name)
		frame = None

		while True:
			ret, frame = cap.read()

			if not ret:
				print "Video could not be loaded."
				break
			if frame.any():
				print "Frame found."
				break

		return frame

	def nothing(self, x):
		# Filler for trackbars
		pass

	def create_trackbars(self):
		self.trackbar_window = cv2.namedWindow("Trackbars")
		cv2.createTrackbar('Median', 'Trackbars', 0, 255, nothing)
		cv2.createTrackbar('Blur', 'Trackbars', 1, 99, nothing)
		cv2.createTrackbar('Thresh', 'Trackbars', 0, 255, nothing)
		cv2.createTrackbar('Save', 'Trackbars', 0, 1, nothing)
		cv2.createTrackbar('Load', 'Trackbars', 0, 1, nothing)
		cv2.createTrackbar('Reset', 'Trackbars', 0, 1, nothing)

		self.default_values()

	def merge(self, frames):
		filler = frames['track'].copy()
		filler[:] = 155
		merged = np.vstack((frames['track'], filler, frames['bw'], filler, frames['final']))

		return merged
		
	def default_values(self):
		# Set default values
		median_value = cv2.setTrackbarPos('Median', 'Trackbars', 100)
		blur_value = cv2.setTrackbarPos('Blur', 'Trackbars', 1)
		thresh_value = cv2.setTrackbarPos('Thresh', 'Trackbars', 25)

	def load_preset(self):
		# Open file to read from
		with open('presets.txt') as f:
			values = f.read().splitlines()

		setTrackbarValues(int(values[0]), int(values[1]), int(values[2]), int(values[3]), int(values[4]), int(values[5]), int(values[6]))
		
	def save_preset(self):
		median, blur, thresh, x, y, w, h, r = getTrackbarValues()
		
		# Open file and clear
		target = open('presets.txt', 'w')
		target.truncate()

		# Write to file
		target.write(str(median))
		target.write('\n')

		target.write(str(blur))
		target.write('\n')

		target.write(str(thresh))
		target.write('\n')

		target.write(str(x))
		target.write('\n')

		target.write(str(y))
		target.write('\n')

		target.write(str(w))
		target.write('\n')

		target.write(str(h))

		# Close File
		target.close()
