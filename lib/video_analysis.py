import frame
from trial_video import trial_video
from steps import steps as s
import itertools
import numpy as np
import cv2
from PIL import Image, ImageTk
import Tkinter as tk
from cv2.cv import CV_CAP_PROP_POS_FRAMES, CV_CAP_PROP_FRAME_COUNT

class video_analysis():
	'''
	analyze video using frame and steps classes
	'''
	def __init__(self,video,top,bot,hor,cap,root,canvas):
		# create the GUI
		print 'Currently performing: VA init'
		self.trial = trial_video(video)
		self.count = self.trial.get(CV_CAP_PROP_FRAME_COUNT)
		print 'Frame Count %02d' % self.count
		self.trial.set_horizon(hor)
		self.trial.set_thresh_vals(top,bot)
		self.cap = cap 
		self.root = root
		self.canvas =canvas
		self.frame_list = list()
		self.increment = 0

	def update_video(self):
		print 'Currently performing: VA update_video'
		raw = self.trial.get_raw_frame() 
		self.bgr = cv2.cvtColor( raw[1], cv2.COLOR_RGB2BGR)
		self.a = Image.fromarray(self.bgr)
		self.b = ImageTk.PhotoImage(image=self.a)
		self.canvas.create_image(0, 0, image=self.b, anchor=tk.NW)
		self.increment += 1
		self.root.update()
		self.this_frame = frame.get_next_frame(self.trial)
		
		try:
			if self.this_frame.get_valid_flag():
				self.feet = self.this_frame.get_foot_positions()
				self.frame_list.append(self.feet)
			
		except:
			pass
			
		self.dostuff()
		self.root.after(33, self.update_video)

	def dostuff(self):
		print 'Currently performing: VA dostuff'
		if self.increment >= self.count:
			list_size = len(self.frame_list)
			print 'i got past this'
			self.steps = s(self.frame_list,list_size,29)
			# steps.get_FR()
			self.steps.printInfo()
			self.steps.plot_paw()