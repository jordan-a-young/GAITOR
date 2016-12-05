import lib.frame as f
from lib.trial_video import trial_video
from lib.trial_video import TRIAL_TOP_THRESH, TRIAL_BOT_THRESH, TRIAL_HORIZON, BLUR_SIGMA, BLUR_TOP, BLUR_BOT, RET, CROP_UP, CROP_DOWN, TOP_CROP_RIGHT, TOP_CROP_LEFT, BOT_CROP_RIGHT, BOT_CROP_LEFT
from lib.steps import steps as s
from lib.side import side
from PIL import Image, ImageTk
import Tkinter as tk
import ttk as ttk
from cv2.cv import CV_CAP_PROP_POS_FRAMES, CV_CAP_PROP_FRAME_COUNT, CV_CAP_PROP_FPS, CV_CAP_PROP_FRAME_WIDTH
import cv2
import tkFileDialog as tkFile
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import time
import numpy as np
import sys
import lib.arch as arch
import FileDialog
import traceback
import tkMessageBox

class GUI():
	'''
	Creates GUI to use with video analysis
	'''
	def __init__(self, parent):
		# variables
		self.play_video = True
		self.show_data = False
		self.trial_ready = tk.BooleanVar()
		self.increment = 0
		self.number = 0
		self.spam_check = 0

		# some important words
		self.root = parent
		self.n = ttk.Notebook(parent)
		self.n.pack(fill='both', expand='yes')

		# set default values
		self.set_default()

		# add frames
		self.add_pages()

		# create menu and menu items
		self.submenu(parent)

		# setup pages
		self.data_page()
		self.video_page()
		self.crop_page()
		self.help_page()
		
		# lists for calculations
		self.paw_list = list()
		self.side_list = list()
		self.angle_list = list()
		self.angle = None

	def submenu(self, parent):
		# create menu and menu items
		self.menu = tk.Menu(self.n)
		parent.config(menu=self.menu)

		# file
		self.file_submenu = tk.Menu(self.menu)
		self.menu.add_cascade(label='File', menu=self.file_submenu)
		self.file_submenu.add_command(label='Open', command=self.set_filename)
		self.file_submenu.add_command(label='Quit', command=self.quit)

		# edit
		self.edit_submenu = tk.Menu(self.menu)
		self.menu.add_cascade(label='Edit', menu=self.edit_submenu)
		self.edit_submenu.add_command(label='Load Preset', command=self.load_preset)
		self.edit_submenu.add_command(label='Save Preset', command=self.save_preset)
		self.edit_submenu.add_command(label='Default Preset', command=self.default_preset)

		# file dialog options
		self.file_options()

	def load_preset(self):
		# open file to read from
		with open('presets.txt') as myFile:
			values = myFile.read().splitlines()

		# set values
		self.top_thresh_var.set(str(values[0]))
		self.bot_thresh_var.set(str(values[1]))
		self.hor_var.set(str(values[2]))
		self.blur_var.set(str(values[3]))
		self.top_blur_var.set(str(values[4]))
		self.bot_blur_var.set(str(values[5]))
		self.up_crop_var.set(str(values[6]))
		self.down_crop_var.set(str(values[7]))
		self.top_right_crop_var.set(str(values[8]))
		self.top_left_crop_var.set(str(values[9]))
		self.bot_right_crop_var.set(str(values[10]))
		self.bot_left_crop_var.set(str(values[11]))

	def save_preset(self):
		# open and clear file to save to
		myFile = open('presets.txt', 'w')
		myFile.truncate()

		# write to file
		myFile.write(self.top_value.get())
		myFile.write('\n')

		myFile.write(self.bot_value.get())
		myFile.write('\n')

		myFile.write(self.horizon_value.get())
		myFile.write('\n')

		myFile.write(self.blur_value.get())
		myFile.write('\n')

		myFile.write(self.top_blur_value.get())
		myFile.write('\n')

		myFile.write(self.bot_blur_value.get())
		myFile.write('\n')

		myFile.write(self.up_crop_value.get())
		myFile.write('\n')

		myFile.write(self.down_crop_value.get())
		myFile.write('\n')

		myFile.write(self.top_right_crop_value.get())
		myFile.write('\n')

		myFile.write(self.top_left_crop_value.get())
		myFile.write('\n')

		myFile.write(self.bot_right_crop_value.get())
		myFile.write('\n')

		myFile.write(self.bot_left_crop_value.get())
		
		# close file
		myFile.close()

	def default_preset(self):
		# sets values to default
		self.top_thresh_var.set(str(100))
		self.bot_thresh_var.set(str(100))
		self.hor_var.set(str(400))
		self.blur_var.set(str(1))
		self.top_blur_var.set(str(1))
		self.bot_blur_var.set(str(1))
		self.up_crop_var.set(str(1))
		self.down_crop_var.set(str(1))
		self.top_right_crop_var.set(str(1))
		self.top_left_crop_var.set(str(1))
		self.bot_right_crop_var.set(str(1))
		self.bot_left_crop_var.set(str(1))

	def set_default(self):
		# sets values for gui to default
		self.top_thresh_var = tk.StringVar(self.root)	# top threshold
		self.top_thresh_var.set(str(100))

		self.bot_thresh_var = tk.StringVar(self.root)	# bot threshold
		self.bot_thresh_var.set(str(100))

		self.hor_var = tk.StringVar(self.root)			# horizon
		self.hor_var.set(str(500))

		self.blur_var = tk.StringVar(self.root)			# blur
		self.blur_var.set(str(1))

		self.top_blur_var = tk.StringVar(self.root)		# top blur
		self.top_blur_var.set(str(1))

		self.bot_blur_var = tk.StringVar(self.root)		# bot blur
		self.bot_blur_var.set(str(1))

		self.conv_var = tk.StringVar(self.root)			# conversion
		self.conv_var.set(str(108.5))

		self.up_crop_var = tk.StringVar(self.root)		# crop up
		self.up_crop_var.set(1)

		self.down_crop_var = tk.StringVar(self.root)	# crop down
		self.down_crop_var.set(1)

		self.top_right_crop_var = tk.StringVar(self.root)	# crop right
		self.top_right_crop_var.set(1)

		self.top_left_crop_var = tk.StringVar(self.root)	# crop left
		self.top_left_crop_var.set(1)

		self.bot_right_crop_var = tk.StringVar(self.root)	# crop right
		self.bot_right_crop_var.set(1)

		self.bot_left_crop_var = tk.StringVar(self.root)	# crop left
		self.bot_left_crop_var.set(1)

	def file_options(self):
		# file dialog options
		self.file_opt = options = {}
		options['defaultextension'] = ' .MP4'
		options['filetypes'] = [('all files', '.*'), ('text files','.MP4')]
		options['initialdir'] = 'c:\Users\Rod\\'
		options['initialfile'] = ' '
		options['parent'] = self.file_submenu

	def add_pages(self):
		# first page with main
		self.f1 = tk.Frame(self.n) 
		self.f1.pack(fill='both', expand='yes')

		# page with video options
		self.f2 = tk.Frame(self.n) 
		self.f2.pack()

		# page with crop settings
		self.f3 = tk.Frame(self.n)
		self.f3.pack()

		# frame for graph canvas
		self.f4 = tk.Frame(self.n) 
		self.f4.pack()

		# frame for graph canvas
		self.f5 = tk.Frame(self.n) 
		self.f5.pack()

		# frame for graph canvas
		self.f6 = tk.Frame(self.n) 
		self.f6.pack()

		# frame for help
		self.f7 = tk.Frame(self.n)
		self.f7.pack()	

		# page labels
		self.page_labels()

	def page_labels(self):
		# adds label to pages
		self.n.add(self.f1, text='Data')
		self.n.add(self.f2, text='Video')
		self.n.add(self.f3, text='Crop')
		self.n.add(self.f4, text='Step Plot')
		self.n.add(self.f5, text='Velocity')
		self.n.add(self.f6, text='Arch')
		self.n.add(self.f7, text='Help')

	def data_page(self):
		# labels for 1st frame
		self.canvas = tk.Canvas(self.f1)
		self.canvas.grid(column=0, row=0, columnspan=1, rowspan=5)

		# cadence
		self.cadence_label = tk.Label(text='Cadence: ', master=self.f1)
		self.cadence_value = tk.Label(text='0', master=self.f1)
		self.cadence_label.grid(column=1, row=0)
		self.cadence_value.grid(column=2, row=0)
		self.cadence_label.columnconfigure(1, weight=1)
		self.cadence_value.columnconfigure(1, weight=1)

		# front right label
		self.FR_label = tk.Label(text='FR Var(cm): ', master=self.f1)
		self.FR_value = tk.Label(text='0', master=self.f1)
		self.FR_label.grid(column=1, row=1)
		self.FR_value.grid(column=2, row=1)
		self.FR_label.columnconfigure(1, weight=1)
		self.FR_value.columnconfigure(1, weight=1)

		# front left label
		self.FL_label = tk.Label(text='FL Var(cm): ', master=self.f1)
		self.FL_value = tk.Label(text='0', master=self.f1)
		self.FL_label.grid(column=1, row=2)
		self.FL_value.grid(column=2, row=2)
		self.FL_label.columnconfigure(1, weight=1)
		self.FL_value.columnconfigure(1, weight=1)

		# back right label
		self.BR_label = tk.Label(text='BR Var(cm): ', master=self.f1)
		self.BR_value = tk.Label(text='0', master=self.f1)
		self.BR_label.grid(column=1, row=3)
		self.BR_value.grid(column=2, row=3)
		self.BR_label.columnconfigure(1, weight=1)
		self.BR_value.columnconfigure(1, weight=1)

		# back left label
		self.BL_label = tk.Label(text='BL Var(cm): ', master=self.f1)
		self.BL_value = tk.Label(text='0', master=self.f1)
		self.BL_label.grid(column=1, row=4)
		self.BL_value.grid(column=2, row=4)
		self.BL_label.columnconfigure(1, weight=1)
		self.BL_value.columnconfigure(1, weight=1)

		# velocity
		self.V_label = tk.Label(text='Mean Velocity(cm/sec): ', master=self.f1)
		self.V_value = tk.Label(text='0', master=self.f1)
		self.V_label.grid(column=1, row=5)
		self.V_value.grid(column=2, row=5)
		self.V_label.columnconfigure(1, weight=1)
		self.V_value.columnconfigure(1, weight=1)

	def help_page(self):
		# creates page for help
		# list to store help options
		help_options = list()
		help_options.append('1) Make sure horizon line splits video correctly.')
		help_options.append('2) Only thing on bottom image should be feet.')
		help_options.append('3) Top video: start threshold high to low. You are thresholding for dark image.')
		help_options.append('4) Bottom video: start threshold low to high.')
		help_options.append('5) Should only be able to see the body of the rat.')
		help_options.append('6) Adjust blur settings to find contour.')

		# tips
		help_tips = list()
		help_tips.append('Horizon: 0 -> 1000')
		help_tips.append('Threshold Values: 0 -> 255')
		help_tips.append('Blur Values: 1 -> 100')
		help_tips.append('Track Length: 0 -> 200')

		# create labels to display help options
		self.help_label = tk.Label(text='Tips for setting up video.', master=self.f7)
		self.help_label0 = tk.Label(text=help_options[0], master=self.f7)
		self.help_label1 = tk.Label(text=help_options[1], master=self.f7)
		self.help_label2 = tk.Label(text=help_options[2], master=self.f7)
		self.help_label3 = tk.Label(text=help_options[3], master=self.f7)
		self.help_label4 = tk.Label(text=help_options[4], master=self.f7)
		self.help_label5 = tk.Label(text=help_options[5], master=self.f7)

		# create labels for tips
		self.help_tip_label0 = tk.Label(text=help_tips[0], master=self.f7)
		self.help_tip_label1 = tk.Label(text=help_tips[1], master=self.f7)
		self.help_tip_label2 = tk.Label(text=help_tips[2], master=self.f7)
		self.help_tip_label3 = tk.Label(text=help_tips[3], master=self.f7)

		# grid positions 
		self.help_label.grid(column=1, row=1, pady=10)
		self.help_label0.grid(column=1, row=2, pady=10)
		self.help_label1.grid(column=1, row=3, pady=10)
		self.help_label2.grid(column=1, row=4, pady=10)
		self.help_label3.grid(column=1, row=5, pady=10)
		self.help_label4.grid(column=1, row=6, pady=10)
		self.help_label5.grid(column=1, row=7, pady=10)

		self.help_tip_label0.grid(column=2, row=1, pady=10)
		self.help_tip_label1.grid(column=2, row=2, pady=10)
		self.help_tip_label2.grid(column=2, row=3, pady=10)
		self.help_tip_label3.grid(column=2, row=4, pady=10)

		# columnconfigure
		self.help_label0.columnconfigure(1, weight=1)
		self.help_label1.columnconfigure(1, weight=1)
		self.help_label2.columnconfigure(1, weight=1)
		self.help_label3.columnconfigure(1, weight=1)
		self.help_label4.columnconfigure(1, weight=1)
		self.help_label5.columnconfigure(1, weight=1)

		self.help_tip_label0.columnconfigure(1, weight=1)
		self.help_tip_label1.columnconfigure(1, weight=1)
		self.help_tip_label2.columnconfigure(1, weight=1)
		self.help_tip_label3.columnconfigure(1, weight=1)

	def video_page(self):
		# creates page for video settings
		# canvas for videos
		self.top_canvas = tk.Canvas(self.f2, width=100, height=100)
		self.top_mask_canvas = tk.Canvas(self.f2, width=100, height=100)
		self.bot_canvas = tk.Canvas(self.f2, width=100, height=100)

		# labels for entry fields
		self.horizon_label = tk.Label(text='Horizon: ', master=self.f2)
		self.top_label = tk.Label(text='Top Threshold: ', master=self.f2)
		self.bot_label = tk.Label(text='Bot Threshold: ', master=self.f2)
		self.blur_label = tk.Label(text='Blur: ', master=self.f2)
		self.top_blur_label = tk.Label(text='Top Blur: ', master=self.f2)
		self.bot_blur_label = tk.Label(text='Bot Blur: ', master=self.f2)

		# entry fields for inputs
		self.horizon_value = tk.Spinbox(self.f2)
		self.top_value = tk.Spinbox(self.f2)
		self.bot_value = tk.Spinbox(self.f2)
		self.blur_value = tk.Spinbox(self.f2)
		self.top_blur_value = tk.Spinbox(self.f2)
		self.bot_blur_value = tk.Spinbox(self.f2)
		self.conv_value = tk.Spinbox(self.f2)

		# configure entry fields
		self.horizon_value.configure(from_=0, to=1000, increment=1, width=4, textvariable=self.hor_var)			# horizon
		self.horizon_value.configure(font=('San', '18', 'bold'))
		
		self.top_value.configure(from_=0, to=255, increment=1, width=4, textvariable=self.top_thresh_var)		# top thresh
		self.top_value.configure(font=('San', '18', 'bold'))
		
		self.bot_value.configure(from_=0, to=255, increment=1, width=4, textvariable=self.bot_thresh_var)		# bot thresh
		self.bot_value.configure(font=('San', '18', 'bold'))
		
		self.blur_value.configure(from_=1, to=100, increment=1, width=4, textvariable=self.blur_var)			# blur
		self.blur_value.configure(font=('San', '18', 'bold'))
		
		self.top_blur_value.configure(from_=1, to=100, increment=1, width=4, textvariable=self.top_blur_var)	# top blur
		self.top_blur_value.configure(font=('San', '18', 'bold'))
		
		self.bot_blur_value.configure(from_=1, to=100, increment=1, width=4, textvariable=self.bot_blur_var)	# bot blur
		self.bot_blur_value.configure(font=('San', '18', 'bold'))
		
		self.conv_value.configure(from_=0, to=200, increment=0.01, width=6, textvariable=self.conv_var)			# conversion
		self.conv_value.configure(font=('San', '18', 'bold'))

		# trial ready button and grid position
		self.trial_ready_checkbox = tk.Checkbutton(self.f2,text='Trial Ready',variable=self.trial_ready,command=self.set_trial_ready)
		self.trial_ready_checkbox.grid(column=5, row=3, pady=10)

		# conversion label and grid position
		self.conv_label = tk.Label(text='Track Length (cm)', master=self.f2)
		self.conv_label.grid(column=2, row=3, pady=10)

		# grid position for video canvases
		self.top_mask_canvas.grid(column=0, row=1, columnspan=2, pady=5)
		self.top_canvas.grid(column=0, row=2, columnspan=2, pady=5)
		self.bot_canvas.grid(column=0, row=3, columnspan=2, pady=5)

		# grid position for labels
		self.horizon_label.grid(column=2, row=0, pady=10)
		self.top_label.grid(column=2, row=1, pady=10)
		self.bot_label.grid(column=2, row=2, pady=10)
		self.blur_label.grid(column=4, row=0, pady=10)
		self.top_blur_label.grid(column=4, row=1, pady=10)
		self.bot_blur_label.grid(column=4, row=2, pady=10)

		# grid position for entry fields
		self.horizon_value.grid(column=3, row=0, pady=10)
		self.top_value.grid(column=3, row=1, pady=10)
		self.bot_value.grid(column=3, row=2, pady=10)
		self.blur_value.grid(column=5, row=0, pady=10)
		self.top_blur_value.grid(column=5,row=1, pady=10)
		self.bot_blur_value.grid(column=5, row=2, pady=10)
		self.conv_value.grid(column=3, row=3, pady=10)

	def crop_page(self):
		# creates page for crop settings
		# labels
		self.up_crop_label = tk.Label(text='Up Crop: ', master=self.f3)
		self.down_crop_label = tk.Label(text='Down Crop: ', master=self.f3)
		self.top_right_crop_label = tk.Label(text='Top Right Crop: ', master=self.f3)
		self.top_left_crop_label = tk.Label(text='Top Left Crop: ', master=self.f3)
		self.bot_right_crop_label = tk.Label(text='Bot Right Crop: ', master=self.f3)
		self.bot_left_crop_label = tk.Label(text='Bot Left Crop: ', master=self.f3)

		# entry fields
		self.up_crop_value = tk.Spinbox(self.f3)
		self.down_crop_value = tk.Spinbox(self.f3)
		self.top_right_crop_value = tk.Spinbox(self.f3)
		self.top_left_crop_value = tk.Spinbox(self.f3)
		self.bot_right_crop_value = tk.Spinbox(self.f3)
		self.bot_left_crop_value = tk.Spinbox(self.f3)

		# canvas for video
		self.crop_top_canvas = tk.Canvas(self.f3, width=100, height=100)
		self.crop_bot_canvas = tk.Canvas(self.f3, width=100, height=100)		

		# configure entry fields
		self.up_crop_value.configure(from_=1, to=100, increment=1, width=4, textvariable=self.up_crop_var)		# up crop
		self.up_crop_value.configure(font=('San', '18', 'bold'))

		self.down_crop_value.configure(from_=1, to=100, increment=1, width=4, textvariable=self.down_crop_var)	# down crop
		self.down_crop_value.configure(font=('San', '18', 'bold'))

		self.top_right_crop_value.configure(from_=1, to=100, increment=1, width=4, textvariable=self.top_right_crop_var)# right crop
		self.top_right_crop_value.configure(font=('San', '18', 'bold'))

		self.top_left_crop_value.configure(from_=1, to=100, increment=1, width=4, textvariable=self.top_left_crop_var)	# left crop
		self.top_left_crop_value.configure(font=('San', '18', 'bold'))

		self.bot_right_crop_value.configure(from_=1, to=100, increment=1, width=4, textvariable=self.bot_right_crop_var)# right crop
		self.bot_right_crop_value.configure(font=('San', '18', 'bold'))

		self.bot_left_crop_value.configure(from_=1, to=100, increment=1, width=4, textvariable=self.bot_left_crop_var)	# left crop
		self.bot_left_crop_value.configure(font=('San', '18', 'bold'))

		# grid position for canvases
		self.crop_top_canvas.grid(column=0, row=1, columnspan=2, pady=5)
		self.crop_bot_canvas.grid(column=0, row=2, columnspan=2, pady=5)

		# grid position for labels
		self.up_crop_label.grid(column=2, row=0, pady=10)
		self.down_crop_label.grid(column=4, row=0, pady=10)
		self.top_right_crop_label.grid(column=4, row=1, pady=10)
		self.top_left_crop_label.grid(column=2, row=1, pady=10)
		self.bot_right_crop_label.grid(column=4, row=2, pady=10)
		self.bot_left_crop_label.grid(column=2, row=2, pady=10)

		# grid position for entry fields
		self.up_crop_value.grid(column=3, row=0, pady=10)
		self.down_crop_value.grid(column=5, row=0, pady=10)
		self.top_right_crop_value.grid(column=5, row=1, pady=10)
		self.top_left_crop_value.grid(column=3, row=1, pady=10)
		self.bot_right_crop_value.grid(column=5, row=2, pady=10)
		self.bot_left_crop_value.grid(column=3, row=2, pady=10)

	def update_video(self):
		# get raw frame and resize
		raw = self.trial.get_raw_frame()[1]
		raw = self.trial.resize_frame(raw, 500)

		# config, get bgr, get array, convert to image
		self.canvas.config(width=raw.shape[1], height=raw.shape[0])
		self.bgr = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
		self.bgr_array = Image.fromarray(self.bgr)
		self.bgr_image = ImageTk.PhotoImage(image=self.bgr_array)
		self.canvas.create_image(0, 0, image=self.bgr_image, anchor=tk.NW)
		self.increment += 1
		self.root.update()
		this_frame = f.get_next_frame(self.trial)

		# get top mask
		top_mask = self.trial.get_top_mask()
		top_mask_copy = top_mask.copy()
		self.number += 1

		try:
			if this_frame is None:
				self.trial_ready.set(False)
				print 'None'

			elif this_frame.get_valid_flag():
				# get the feet data
				self.feet = this_frame.get_foot_positions()
				self.paw_list.append(self.feet)

				# get the rats position
				self.side_pos = f.get_side_contour(top_mask_copy)
				self.side_list.append(self.side_pos)
				
				# calculate the arch data
				self.angle, _ = this_frame.get_arch_data()
				self.angle_list.append(self.angle)

				if self.spam_check == 0:
					print 'Starting analysis'
					self.spam_check = 1

		except Exception, e:
			traceback.print_exc()

		self.publish_data()
		self.root.after(5, self.update_main)

	def update_main(self):
		# update main tab
		if self.play_video and self.trial_ready.get():
			# print 'i am playing video'
			self.update_video()

		if not self.trial_ready.get():
			# print 'i am looping main'
			self.visual_threshold()

	def publish_data(self):
		# update from with analyzed data
		#print 'Currently performing: GUI publish_data'
		fps = self.trial.get(CV_CAP_PROP_FPS)
		frame_width = self.trial.get(CV_CAP_PROP_FRAME_WIDTH)
		
		if (self.increment >= self.count) and (self.show_data == False):
			list_size = len(self.paw_list)
			self.side_list = np.array(self.side_list, dtype=np.float)
			self.angle_list = np.array(self.angle_list, dtype=np.float)
			sideprofile = side(self.side_list,self.angle_list,fps,conversion=float(self.conv_value.get()),frame_width=frame_width)
			self.steps = s(self.paw_list, list_size, fps, frame_width=frame_width)

			# calculate step data
			c,fr,fl,br,bl = self.steps.get_variable()

			# set label value
			self.cadence_value['text'] = str(c)
			self.FR_value['text'] = str(fr)
			self.FL_value['text'] = str(fl)
			self.BR_value['text'] = str(br)
			self.BL_value['text'] = str(bl)

			figure = self.steps.plot_paw()

			# calculate side data
			vel = sideprofile.get_Xvel()
			self.V_value['text'] = str(vel)

			# create figure for velocity plot
			figure2 = sideprofile.plot()

			# create arch angle plot
			figure3 = sideprofile.plot2()

			# show graphs
			self.graph(figure)
			self.graph2(figure2)
			self.graph3(figure3)

			# publish data
			frs, fls, brs, bls = self.steps.print_info()
			self.data_file(c, fr, fl, br, bl, frs, fls, brs, bls, vel)

			self.show_data = True
			self.play_video = False

	def do_nothing(self):
		# filler function
		pass

	def set_filename(self):
		# return name of the open file
		file_name = tkFile.askopenfilename(**self.file_opt)
		self.file_name = file_name

		# create new trial video
		self.trial = trial_video(self.file_name, horizon=int(self.horizon_value.get()))
		self.trial.read()
		self.count = self.trial.get(CV_CAP_PROP_FRAME_COUNT)
		print 'Frame Count: %02d' % self.count

		# reset windows
		self.trial_ready.set(False)
		self.play_video = True
		self.set_trial_ready()
		self.reset_video()

		# update the video
		self.update_main()

	def graph(self, figure):
		# embed matplot graph to tkinter canvas
		self.graph_canvas = tk.Canvas(self.f4, width=640, height=480)
		self.graph_canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.canvas2 = FigureCanvasTkAgg(figure, self.graph_canvas)
		self.canvas2.show()
		self.canvas2.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.toolbar = NavigationToolbar2TkAgg(self.canvas2, self.f4)
		self.toolbar.update()
		self.canvas2._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

	def graph2(self, figure):
		# embed matplot graph to tkinter canvas
		self.graph_canvas2 = tk.Canvas(self.f5, width=640, height=480)
		self.graph_canvas2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.canvas22 = FigureCanvasTkAgg(figure, self.graph_canvas2)
		self.canvas22.show()
		self.canvas22.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.toolbar2 = NavigationToolbar2TkAgg(self.canvas22, self.f5)
		self.toolbar2.update()
		self.canvas22._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

	def graph3(self, figure):
		# embed matplot graph to tkinter canvas
		self.graph_canvas3 = tk.Canvas(self.f6, width=640, height=480)
		self.graph_canvas3.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.canvas3 = FigureCanvasTkAgg(figure, self.graph_canvas3)
		self.canvas3.show()
		self.canvas3.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.toolbar3 = NavigationToolbar2TkAgg(self.canvas3, self.f6)
		self.toolbar3.update()
		self.canvas3._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

	def reset_video(self):
		'''
		set frame current frame to 0
		reset all data variables
		'''
		self.trial.set(CV_CAP_PROP_POS_FRAMES,0)
		self.increment = 0
		self.paw_list[:] = []
		self.side_list[:] = []
		self.angle_list[:] = []
		self.show_data = False

		# reset labels
		self.cadence_value['text'] = ''
		self.FR_value['text'] = ''
		self.FL_value['text'] = ''
		self.BR_value['text'] = ''
		self.BL_value['text'] = ''
		self.V_value['text'] = ''

		# reset graph canvas
		try:
			self.graph_canvas.destroy()
			self.toolbar.destroy()

			self.graph_canvas2.destroy()
			self.toolbar2.destroy()

		except:
			pass

	def visual_threshold(self):
		# visual for advanced setting
		try:
			frame = f.get_next_frame(self.trial)

			# get top mask and top raw mat
			top_mask = self.trial.get_top_mask()
			top_mat = self.trial.get_top_mat()
			top_mask_copy = top_mask.copy()

			# get and draw contour
			side_contour = f.get_side_contour(top_mask_copy)
			contour = frame.get_side_contour()
			side_pos = frame.get_side_position()
			cv2.drawContours(top_mat, contour, -1, (0,255,0), 3)
			cv2.waitKey(1)

			# resize
			top_mask = self.trial.resize_frame(top_mask, 400)
			top_mat = self.trial.resize_frame(top_mat, 400)

			# config
			self.top_canvas.config(width=top_mask.shape[1], height=top_mask.shape[0])
			self.top_mask_canvas.config(width=top_mask.shape[1], height=top_mask.shape[0])
			self.crop_top_canvas.config(width=top_mask.shape[1], height=top_mask.shape[0])

			# get array
			self.top_mask_array = Image.fromarray(top_mask)
			self.top_mat_array = Image.fromarray(top_mat)

			# convert to image
			self.top_mask_image = ImageTk.PhotoImage(image=self.top_mask_array)
			self.top_mat_image = ImageTk.PhotoImage(image=self.top_mat_array)
			self.top_canvas.create_image(0, 0, image=self.top_mat_image, anchor=tk.NW)
			self.top_mask_canvas.create_image(0, 0, image=self.top_mask_image, anchor=tk.NW)
			self.crop_top_canvas.create_image(0, 0, image=self.top_mask_image, anchor=tk.NW)

			# get bot mask
			bot = self.trial.get_bottom_mask()
			bot = self.trial.resize_frame(bot, 400)

			# config, get array, convert to image
			self.bot_canvas.config(width=bot.shape[1], height=bot.shape[0])
			self.crop_bot_canvas.config(width=bot.shape[1], height=bot.shape[0])
			self.bot_array = Image.fromarray(bot)
			self.bot_image = ImageTk.PhotoImage(image=self.bot_array)
			self.bot_canvas.create_image(0, 0, image=self.bot_image, anchor=tk.NW)
			self.crop_bot_canvas.create_image(0, 0, image=self.bot_image, anchor=tk.NW)

			# print the arch data
			angle, _ = frame.get_arch_data()

		except:
			pass

		# reset video if no more frames
		try:
			if self.trial.get(23) == False:
				self.trial.set(CV_CAP_PROP_POS_FRAMES, 0)
		except:
			pass

		# update canvas
		self.root.update()

		# update values
		try:
			self.trial.set(TRIAL_TOP_THRESH, float(self.top_value.get()))
			self.trial.set(TRIAL_BOT_THRESH, float(self.bot_value.get()))
			self.trial.set(TRIAL_HORIZON, float(self.horizon_value.get()))
			self.trial.set(BLUR_SIGMA, int(self.blur_value.get()))
			self.trial.set(BLUR_TOP, int(self.top_blur_value.get()))
			self.trial.set(BLUR_BOT, int(self.bot_blur_value.get()))
			self.trial.set(CROP_UP, int(self.up_crop_value.get()))
			self.trial.set(CROP_DOWN, int(self.down_crop_value.get()))
			self.trial.set(TOP_CROP_RIGHT, int(self.top_right_crop_value.get()))
			self.trial.set(TOP_CROP_LEFT, int(self.top_left_crop_value.get()))
			self.trial.set(BOT_CROP_RIGHT, int(self.bot_right_crop_value.get()))
			self.trial.set(BOT_CROP_LEFT, int(self.bot_left_crop_value.get()))

		except:
			pass

		try:
			frame = f.get_next_frame(self.trial)
		
		except:
			pass

		if not self.trial_ready.get():
			self.root.after(5, self.visual_threshold)
		else:
			self.root.after(5, self.update_main)

	def set_trial_ready(self):
		# change the state of trial ready
		if self.trial_ready.get() == False:
			self.top_value.configure(state='normal')
			self.bot_value.configure(state='normal')
			self.horizon_value.configure(state='normal')
			self.blur_value.configure(state='normal')
			self.top_blur_value.configure(state='normal')
			self.bot_blur_value.configure(state='normal')
			self.conv_value.configure(state='normal')
			self.up_crop_value.configure(state='normal')
			self.down_crop_value.configure(state='normal')
			self.top_right_crop_value.configure(state='normal')
			self.top_left_crop_value.configure(state='normal')
			self.bot_right_crop_value.configure(state='normal')
			self.bot_left_crop_value.configure(state='normal')
		else:
			self.top_value.configure(state='disabled')
			self.bot_value.configure(state='disabled')
			self.horizon_value.configure(state='disabled')
			self.blur_value.configure(state='disabled')
			self.top_blur_value.configure(state='disabled')
			self.bot_blur_value.configure(state='disabled')
			self.conv_value.configure(state='disabled')
			self.up_crop_value.configure(state='disabled')
			self.down_crop_value.configure(state='disabled')
			self.top_right_crop_value.configure(state='disabled')
			self.top_left_crop_value.configure(state='disabled')
			self.bot_right_crop_value.configure(state='disabled')
			self.bot_left_crop_value.configure(state='disabled')
			
			self.reset_video()
			self.update_video()

	def data_file(self, c, FR, FL, BR, BL, FRs, FLs, BRs, BLs, vel):
		'''
		create a txt file using the cadence & variability of rat
		and also the steps per each paw
		'''
		# open file to write to
		split = self.file_name.split('\\')
		name = split[len(split)-1]
		name = self.file_name + '_data.txt'
		name = name.replace('.mp4', '')
		myFile = open(name, 'w')
		myFile.truncate()

		# write to file
		myFile.write('Cadence: ' +str(c)+ '\n')
		myFile.write('\n')
		myFile.write('-Stride Length Variability-\n')
		myFile.write('Front Right: '+str(FR) +' cm\n')
		myFile.write('Hind Right: '+str(BR) +' cm\n')
		myFile.write('Front Left: '+str(FL) +' cm\n')
		myFile.write('Hind Left: '+str(BL) +' cm\n')
		myFile.write('\n')
		myFile.write('-Steps Taken by Each Paw-\n')
		myFile.write('Front Right: '+str(FRs)+'\n')
		myFile.write('Hind Right: '+str(BRs)+'\n')
		myFile.write('Front Left: '+str(FLs)+'\n')
		myFile.write('Hind Left: '+str(BLs)+'\n')
		myFile.write('\n')
		myFile.write('Mean Velocity: ' +str(vel)+' cm/sec')

		# close file
		myFile.close()

	def quit(self):
		# destroy all GUI items
		try:
			if tkMessageBox.askokcancel('Quit', 'Do you want to exit?'):
				self.root.quit()
		except:
			pass