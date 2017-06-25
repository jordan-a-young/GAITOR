import cv2
import Tkinter as tk
import tkFileDialog as tkFile
import os.path
from ROIManager import ROIManager


class Manager():
	def __init__(self, frame):
		self.roi_manager = ROIManager(self.get_first_frame)
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

	"""
	Purpose: Uses string and path manipulations to create the output filenames for
	the different outputs of the program.
	Input: 	inputfile: the full filepath of the video being analyzed
			filetype: the type of file being written
			add_text: any additional text, defaults to empty string
	Output: a unique filepath for the output file to be written to.
	"""
	def make_file_path(self, input_file, file_type, add_text=''):
		#add a space to additional text if it exists for formatting purposes
		if len(add_text) > 0:
			add_text = ' ' + add_text
		
		#splits the filepath into directory + the files name
		splitpath = os.path.split(input_file)
		newpath = (splitpath[0] + '/' + splitpath[1].split('.')[0] +
				  ' automated scoring' + add_text + file_type)

		#If file already exists append numbers to its name until it doesn't exist
		counter = 1
		while os.path.exists(newpath):
			counter += 1
			newpath = (splitpath[0] + '/' + splitpath[1].split('.')[0] +
					  ' automated scoring' + add_text + ' (' + str(counter) + ')' +
					  file_type)

		return newpath

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
