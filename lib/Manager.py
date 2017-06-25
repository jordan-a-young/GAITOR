import cv2
import Tkinter as tk
import tkFileDialog
import os.path


class Manager():
	def __init__(self):
		print 'Manager class'

	"""
	Purpose: Lets the user pick a folder that will contain all
	the videos to be analyzed. The root manipulations are necessary for
	a clean close-out.
	Output: a string that is the full path to the folder the user chooses.
	"""
	def pick_folder():
		root = tk.Tk()
		root.update()
		folder = tkFileDialog.askdirectory(title='Choose a Folder')
		root.destroy()
		return folder

	"""
	Purpose: Uses string and path manipulations to create the output filenames for
	the different outputs of the program.
	Input: inputfile: the full filepath of the video being analyzed, filetype: the
	type of file being written, and add_text: any additional text, defaults to empty
	string
	Output: a unique filepath for the output file to be written to.
	"""
	def make_file_path(input_file, file_type, add_text=''):
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
