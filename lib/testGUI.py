import lib.frame as f
from lib.trial_video import trial_video
from lib.trial_video import TRIAL_SIDE_THRESH, TRIAL_BOT_THRESH , TRIAL_HORIZON ,BLUR_SIGMA,BLUR_TOP,BLUR_BOT,RET
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
	def __init__(self, top, bot, hor, parent):
		print 'Currently performing: GUI Init'

		# boolean variables
		self.play_video = True
		self.show_data = False
		self.trial_ready = tk.BooleanVar()

		# some important words
		self.root = parent
		self.n = ttk.Notebook(parent)
		self.n.pack(fill='both', expand='yes')

		self.f1 = tk.Frame(self.n) # first page with main
		self.f1.pack(fill='both', expand='yes')
		self.canvas = tk.Canvas(self.f1)
		self.canvas.grid(column=0, row=0, columnspan=1, rowspan=5)

		self.f2 = tk.Frame(self.n) # second page with advanced options
		self.f2.pack()

		self.f3 = tk.Frame(self.n) # frame for graph canvas
		self.f3.pack()

		self.f4 = tk.Frame(self.n) # frame for graph canvas
		self.f4.pack()

		self.f5 = tk.Frame(self.n) # frame for graph canvas
		self.f5.pack()

		self.n.add(self.f1, text='Main')
		self.n.add(self.f2, text='Advanced')
		self.n.add(self.f3, text='Step Plot')
		self.n.add(self.f4, text='Velocity')
		self.n.add(self.f5, text='Arch')

		# create menu and menu items
		self.menu = tk.Menu(self.n)
		parent.config(menu=self.menu)
		self.submenu = tk.Menu(self.menu)
		self.menu.add_cascade(label='file', menu=self.submenu)
		self.submenu.add_command(label='Open', command = self.set_filename)
		self.submenu.add_command(label='Quit', command=self.quit)

		# file dialog options
		self.file_opt = options = {}
		options['defaultextension'] = ' .MP4'
		options['filetypes'] = [('all files', '.*'),('text files','.MP4')]
		options['initialdir'] = 'c:\Users\Rod\Source\Repos\swag\\'
		options['initialfile'] = ' '
		options['parent'] = self.submenu

		# file name
		self.file_name = file_name = tkFile.askopenfilename(**self.file_opt)

		# labels for 1st frame
		self.cadence_label = tk.Label(text='Cadence: ', master= self.f1)
		self.cadence_label.grid(column=1, row=0)
		self.cadence_value = tk.Label(text='0', master=self.f1)
		self.cadence_value.grid(column=2, row=0)
		self.cadence_label.columnconfigure(1,weight=1)
		self.cadence_value.columnconfigure(1,weight=1)

		self.FR_label = tk.Label(text='FR Var(cm): ', master= self.f1)
		self.FR_label.grid(column=1, row=1)
		self.FR_value = tk.Label(text='0', master=self.f1)
		self.FR_value.grid(column=2, row=1)
		self.FR_label.columnconfigure(1,weight=1)
		self.FR_value.columnconfigure(1,weight=1)

		self.FL_label = tk.Label(text='FL Var(cm): ', master= self.f1)
		self.FL_label.grid(column=1, row=2)
		self.FL_value = tk.Label(text='0', master=self.f1)
		self.FL_value.grid(column=2, row=2)
		self.FL_label.columnconfigure(1,weight=1)
		self.FL_value.columnconfigure(1,weight=1)

		self.BR_label = tk.Label(text='BR Var(cm): ', master= self.f1)
		self.BR_label.grid(column=1, row=3)
		self.BR_value = tk.Label(text='0', master=self.f1)
		self.BR_value.grid(column=2, row=3)
		self.BR_label.columnconfigure(1,weight=1)
		self.BR_value.columnconfigure(1,weight=1)

		self.BL_label = tk.Label(text='BL Var(cm): ', master= self.f1)
		self.BL_label.grid(column=1, row=4)
		self.BL_value = tk.Label(text='0', master=self.f1)
		self.BL_value.grid(column=2, row=4)
		self.BL_label.columnconfigure(1,weight=1)
		self.BL_label.columnconfigure(1,weight=1)

		self.V_label = tk.Label(text='Mean Velocity(cm/sec): ', master= self.f1)
		self.V_label.grid(column=1, row=5)
		self.V_value = tk.Label(text='0', master=self.f1)
		self.V_value.grid(column=2, row=5)
		self.V_label.columnconfigure(1,weight=1)
		self.V_label.columnconfigure(1,weight=1)

		# trialvideo
		self.increment = 0
		self.number = 0

		self.trial = trial_video(self.file_name, horizon=hor)
		self.trial.read()
		self.count = self.trial.get(CV_CAP_PROP_FRAME_COUNT)
		print 'Frame Count: %02d' % self.count
		self.trial.set_horizon(hor)
		# self.trial.set_thresh_vals(top,bot)
		self.paw_list = list()
		self.side_list = list()
		self.angle_list = list()
		self.angle = None

		# get height ratio needed for horizon line
		# self.trial.set(CV_CAP_PROP_POS_FRAMES,self.count/2)
		self.top = self.trial.get_top_mask()
		# self.height_i = self.top.shape[0]
		# self.top = self.trial.resize_frame(self.top, 100)
		# self.height_f = self.top.shape[0]
		# self.h_ratio = self.height_f / self.height_i

		# default threshold values
		self.d_side = top
		self.d_bot = bot
		self.d_hor = hor
		self.d_blur = self.trial.get(BLUR_SIGMA)
		self.td_blur = self.trial.get(BLUR_TOP)
		self.bd_blur = self.trial.get(BLUR_BOT)
		
		self.advanced_settings(self.d_side,self.d_bot,self.d_hor,self.d_blur,self.td_blur,self.bd_blur)

	def update_video(self):
		print 'Currently performing: GUI update_video'
		# do more stuff
		raw = self.trial.get_raw_frame()[1]
		raw = self.trial.resize_frame(raw,500)
		self.canvas.config(width=raw.shape[1], height=raw.shape[0])
		self.bgr = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
		self.a = Image.fromarray(self.bgr)
		self.b = ImageTk.PhotoImage(image= self.a)
		self.canvas.create_image(0,0,image=self.b, anchor=tk.NW)
		self.increment += 1
		self.root.update()
		this_frame = f.get_next_frame(self.trial)

		top = self.trial.get_top_mask()
		c1_top = top.copy()
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
				self.side_pos = f.get_side_contour(c1_top)
				self.side_list.append(self.side_pos)
				# print 'side_pos:' + str(self.side_pos)

				# calculate the arch data
				self.angle,_ = this_frame.get_arch_data()
				self.angle_list.append(self.angle)

				# print ' position: ' + str(self.side_pos)+ 'Angle: ' + str(self.angle)+ ' ' + str(self.number)
				print 'Not None'

		except Exception, e:
			# print str(e) +'position'+ str(self.side_pos) + ' angle: ' + str(self.angle)
			traceback.print_exc()

		self.publish_data()
		# print 'updated form'
		# self.root.after(5, self.update_video)
		self.root.after(5, self.update_main)

	def update_main(self):
		print 'Currently performing: GUI update_main'
		# update main tab
		if self.play_video and self.trial_ready.get():
			# print 'i am playing video'
			self.update_video()

		if not self.trial_ready.get():
			# print 'i am looping main'
			self.visual_threshold()

	def publish_data(self):
		'''
		update from with analyzed data
		'''
		print 'Currently performing: GUI publish_data'
		fps = self.trial.get(CV_CAP_PROP_FPS)
		frame_width = self.trial.get(CV_CAP_PROP_FRAME_WIDTH)
		
		if (self.increment >= self.count) and (self.show_data == False):
			list_size = len(self.paw_list)
			self.side_list = np.array(self.side_list, dtype=np.float)
			self.angle_list = np.array(self.angle_list, dtype=np.float)
			sideprofile = side(self.side_list,self.angle_list,fps,conversion=float(self.conv_value.get()),frame_width=frame_width)

			# print 'i got past this'
			self.steps = s(self.paw_list,list_size,fps, frame_width=frame_width)
			# steps.get_FR()

			# calculate step data
			c,fr,fl,br,bl = self.steps.get_variable()

			# set label value
			self.cadence_value['text'] = str(c)
			self.FR_value['text'] = str(fr)
			self.FL_value['text'] = str(fl)
			self.BR_value['text'] = str(br)
			self.BL_value['text'] = str(bl)

			figure =self.steps.plot_paw()

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

			# sideprofile.show()
			frs,fls,brs,bls = self.steps.print_info()
			self.data_file(c,fr,fl,br,bl,frs,fls,brs,bls,vel)

			self.show_data = True
			self.play_video = False

	def do_nothing(self):
		pass

	def set_filename(self):
		print 'Currently performing: GUI set_filename'
		# return name of the open file

		file_name = tkFile.askopenfilename(**self.file_opt)
		self.file_name = file_name

		# create new trial video
		self.trial = trial_video(self.file_name, horizon=int(self.horizon_value.get()))
		self.trial.read()
		self.count = self.trial.get(CV_CAP_PROP_FRAME_COUNT)

		# reset windows
		self.trial_ready.set(False)
		self.play_video = True
		self.set_trial_ready()
		self.reset_video()

		# update the video
		self.update_main()

	def graph(self, figure):
		# embed matplot graph to tkinter canvas
		self.graph_canvas = tk.Canvas(self.f3, width=640, height=480)
		self.graph_canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.canvas2 = FigureCanvasTkAgg(figure, self.graph_canvas)
		self.canvas2.show()
		self.canvas2.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.toolbar = NavigationToolbar2TkAgg(self.canvas2, self.f3)
		self.toolbar.update()
		self.canvas2._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

	def graph2(self, figure):
		# embed matplot graph to tkinter canvas
		self.graph_canvas2 = tk.Canvas(self.f4, width=640, height=480)
		self.graph_canvas2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.canvas22 = FigureCanvasTkAgg(figure, self.graph_canvas2)
		self.canvas22.show()
		self.canvas22.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.toolbar2 = NavigationToolbar2TkAgg(self.canvas22, self.f4)
		self.toolbar2.update()
		self.canvas22._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

	def graph3(self, figure):
		# embed matplot graph to tkinter canvas
		self.graph_canvas3 = tk.Canvas(self.f5, width=640, height=480)
		self.graph_canvas3.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.canvas3 = FigureCanvasTkAgg(figure, self.graph_canvas3)
		self.canvas3.show()
		self.canvas3.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.toolbar3 = NavigationToolbar2TkAgg(self.canvas3, self.f5)
		self.toolbar3.update()
		self.canvas3._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

	def reset_video(self):
		'''
		set frame current frame to 0
		reset all data variables
		'''
		print 'Currently performing: GUI reset_video'
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

	def advanced_settings(self, t, b, h, bl, t_b, b_b):
		'''
		GUI for user setting, contains
		canvas for horizon , top and bot thresh
		also slider and label button to set trial_ready
		'''
		print 'Currently performing: GUI advanced_settings'
		t_var = tk.StringVar(self.root)
		t_var.set(str(t))

		b_var = tk.StringVar(self.root)
		b_var.set(str(b))

		h_var = tk.StringVar(self.root)
		h_var.set(str(h))

		bl_var = tk.StringVar(self.root)
		bl_var.set(str(bl))

		tb_var = tk.StringVar(self.root)
		tb_var.set(str(t_b))

		bb_var = tk.StringVar(self.root)
		bb_var.set(str(b_b))

		conv_var = tk.StringVar(self.root)
		conv_var.set(str(116.84))

		self.top_canvas = tk.Canvas(self.f2, width=100, height=100)
		self.top_canvas2 = tk.Canvas(self.f2, width=100, height=100)
		self.bot_canvas = tk.Canvas(self.f2, width=100, height=100)

		self.horizon_label = tk.Label(text='Horizon Value: ', master= self.f2)
		self.top_label = tk.Label(text='Top_Thresh Value: ', master= self.f2)
		self.bot_label = tk.Label(text='Bot_Thresh Value: ', master= self.f2)
		self.blur_label = tk.Label(text='Blur : ', master=self.f2)
		self.t_blur_label = tk.Label(text='Blur_Top: ', master=self.f2)
		self.b_blur_label = tk.Label(text='Blur_Bot: ', master=self.f2)

		self.horizon_value = tk.Spinbox(self.f2)	# reset advance setting values
		self.horizon_value.configure(from_=0,to =1000, increment = 1, width=5, textvariable=h_var)
		self.horizon_value.configure(font=('San', '18', 'bold'))

		self.top_value = tk.Spinbox(self.f2)
		self.top_value.configure(from_ =0, to = 255, increment=1, width=5, textvariable=t_var)
		self.top_value.configure(font=('San', '18', 'bold'))

		self.bot_value = tk.Spinbox(self.f2)
		self.bot_value.configure(from_ =0, to=255, increment=1, width=5,textvariable=b_var)
		self.bot_value.configure(font=('San', '18', 'bold'))

		self.blur_value = tk.Spinbox(self.f2)
		self.blur_value.configure(from_ =1, to=100, increment=1, width=5, textvariable=bl_var)
		self.blur_value.configure(font=('San', '18', 'bold'))

		self.t_blur_value = tk.Spinbox(self.f2)
		self.t_blur_value.configure(from_ =1, to=100, increment=1, width=5, textvariable=tb_var)
		self.t_blur_value.configure(font=('San', '18', 'bold'))

		self.b_blur_value = tk.Spinbox(self.f2)
		self.b_blur_value.configure(from_ =1, to=100, increment=1, width=5, textvariable=bb_var)
		self.b_blur_value.configure(font=('San', '18', 'bold'))

		self.conv_value = tk.Spinbox(self.f2)
		self.conv_value.configure(from_ =0, to=200, increment=0.01, width=6, textvariable=conv_var)
		self.conv_value.configure(font=('San', '18', 'bold'))

		self.top_canvas.grid(column=0, row=1, columnspan=2)
		self.top_canvas2.grid(column=0, row=2, columnspan=2)
		self.bot_canvas.grid(column=0, row=3, columnspan=2)

		self.horizon_label.grid(column=2, row=0, pady=10)
		self.top_label.grid(column=2, row=1)
		self.bot_label.grid(column=2, row=2)
		self.blur_label.grid(column=4, row=0, pady=10)
		self.t_blur_label.grid(column=4, row=1, pady=10)
		self.b_blur_label.grid(column=4, row=2, pady=10)

		self.trial_ready_checkbox = tk.Checkbutton(self.f2,text='Trial Ready',variable=self.trial_ready, command=self.set_trial_ready)
		self.trial_ready_checkbox.grid(column=5, row=3)

		self.conv_label = tk.Label(text='Track Length (cm)', master= self.f2)
		self.conv_label.grid(column=2, row=3)

		self.horizon_value.grid(column=3, row=0, pady=10)
		self.top_value.grid(column=3, row=1)
		self.bot_value.grid(column=3, row=2)
		self.blur_value.grid(column=5, row=0, pady=10)
		self.t_blur_value.grid(column=5,row=1, pady=10)
		self.b_blur_value.grid(column=5, row=2, pady=10)
		self.conv_value.grid(column=3, row=3)

	def visual_threshold(self):
		'''
		visual for advanced setting
		'''
		print 'Currently performing: GUI visual_threshold'
		try:
			frame = f.get_next_frame(self.trial)

			# set top threshold
			top = self.trial.get_top_mask()
			c_top = self.trial.get_top_mat()
			c1_top = top.copy()
			c_side = f.get_side_contour(c1_top)

			c = frame.get_side_contour()
			c2 = frame.get_side_position()
			# print c2
			cv2.drawContours(c_top, c, -1, (0,255,0), 3)
			# cv2.imshow('',c_top)
			cv2.waitKey(1)
			top = self.trial.resize_frame(top, 300)
			c_top = self.trial.resize_frame(c_top, 300)

			self.top_canvas.config(width=top.shape[1], height=top.shape[0])
			self.top_canvas2.config(width=top.shape[1], height=top.shape[0])
			self.a = Image.fromarray(top)
			self.c_a = Image.fromarray(c_top)
			self.b = ImageTk.PhotoImage(image=self.a)
			self.c_b = ImageTk.PhotoImage(image=self.c_a)
			self.top_canvas.create_image(0, 0, image=self.b, anchor=tk.NW)
			self.top_canvas2.create_image(0, 0, image=self.c_b, anchor=tk.NW)

			# set bot threshold
			bot = self.trial.get_bottom_mask()
			bot = self.trial.resize_frame(bot, 300)
			self.bot_canvas.config(width=bot.shape[1], height=bot.shape[0])
			self.a_b = Image.fromarray(bot)
			self.b_b = ImageTk.PhotoImage(image=self.a_b)
			self.bot_canvas.create_image(0, 0, image=self.b_b, anchor=tk.NW)

			'''Print the arch data'''
			angle, _ = frame.get_arch_data()
			# print 'angle: ' + str(angle)

		except:
			pass

		# reset video if no more frames
		if self.trial.get(23) == False:
			self.trial.set(CV_CAP_PROP_POS_FRAMES,0)

		# update canvas
		self.root.update()

		# update threshold value
		try:
			self.trial.set(TRIAL_SIDE_THRESH,float(self.top_value.get()))
			self.trial.set(TRIAL_BOT_THRESH,float(self.bot_value.get()))
			self.trial.set(TRIAL_HORIZON,float(self.horizon_value.get()))
			self.trial.set(BLUR_SIGMA,int(self.blur_value.get()))
			self.trial.set(BLUR_TOP,int(self.t_blur_value.get()))
			self.trial.set(BLUR_BOT,int(self.b_blur_value.get()))

		except:
			pass

		frame = f.get_next_frame(self.trial)
		# self.root.after(33,self.visual_threshold)

		if not self.trial_ready.get():
			self.root.after(5, self.visual_threshold)
		else:
			self.root.after(5, self.update_main)

	def set_trial_ready(self):
		print 'Currently performing: GUI set_trial_ready'
		# change the state of trial ready
		if self.trial_ready.get() == False:
			self.top_value.configure(state ='normal')
			self.bot_value.configure(state='normal')
		else:
			self.top_value.configure(state ='disabled')
			self.bot_value.configure(state='disabled')
			self.reset_video()
			self.update_video()

	def data_file(self, c, FR, FL, BR, BL, FRs ,FLs ,BRs ,BLs , vel):
		'''
		create a txt file using the cadence & variability of rat
		and also the steps per each paw
		'''
		print 'Currently performing: GUI data_file'
		split = self.file_name.split('\\')
		name = split[len(split)-1]
		name = self.file_name + '_data.txt'
		f = open(name, 'a')

		f.write('Cadence: ' +str(c) + '\n')
		f.write('\n')
		f.write('-Stride Length Variability-\n')
		f.write('Front Right: '+str(FR) +' cm\n')
		f.write('Hind Right: '+str(BR) +' cm\n')
		f.write('Front Left: '+str(FL) +' cm\n')
		f.write('Hind Left: '+str(BL) +' cm\n')
		f.write('\n')
		f.write('-Steps Taken by Each Paw-\n')
		f.write('Front Right: '+str(FRs) +'\n')
		f.write('Hind Right: '+str(BRs) +'\n')
		f.write('Front Left: '+str(FLs) +'\n')
		f.write('Hind Left: '+str(BLs) +'\n')
		f.write('\n')
		f.write('Mean Velocity: ' +str(vel)+' cm/sec')

		f.close()

	def quit(self):
		# destroy all GUI items
		try:
			self.root.destroy()
		except:
			pass