import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

class steps():
	'''
	analyze paw data retrieved from frame class
	'''
	def __init__(self, paw_list, list_size, fps, conversion=108.5, frame_width=None):
		'''
		initialize list of paws, size of list and
		frame per second
		'''
		#print 'Currently performing: Steps init'
		self.conversion = conversion
		self.frame_width =float(frame_width)

		self.FRONT = 1
		self.BACK = 0
		self.RIGHT = 1
		self.LEFT = 0

		# plot value of paw
		self.FR = 2
		self.FL = 3
		self.BR = 1
		self.BL = 4

		self.list_size = list_size
		self.paw_list = paw_list
		self.seconds = list_size/fps

		# number of steps per each paw
		self.front_right_steps = 0
		self.front_left_steps = 0
		self.back_right_steps = 0
		self.back_left_steps = 0

		# create graph per foot and stride length
		print 'starting .....'

		self.FR_list = list()
		self.FL_list = list()
		self.BR_list = list()
		self.BL_list = list()

		# list of stride lengths
		self.FR_stride = list()
		self.FL_stride = list()
		self.BR_stride = list()
		self.BL_stride = list()

		# variability
		self.FR_var = list()
		self.FL_var = list()
		self.BR_var = list()
		self.BL_var = list()

		# cadence
		self.cadence = None

		self.analyze()

	def analyze_front_right(self):
		'''
		count the amount of paw present
		following right paw absence
		'''
		#print 'Currently performing: Steps analyze_front_right'
		paw_found = False
		previous_paw = 0
		current_paw = 0

		for i in xrange(self.list_size):
			try:
				if self.paw_list[i][self.FRONT][self.RIGHT] and not self.paw_list[i-1][self.FRONT][self.RIGHT]:
					# if the paw was previously in the air and is now down
					# increment the number of steps
					self.front_right_steps += 1
					paw_found = True

					# add value to stride length
					paw = self.paw_list[i][self.FRONT][self.RIGHT]
					previous_paw = current_paw
					current_paw = paw[0]
					s_value = current_paw - previous_paw
					self.FR_stride.append(s_value)

				if self.paw_list[i][self.FRONT][self.RIGHT]:
					# if there is a paw present add to graph array
					value = self.FR
					self.FR_list.append(value)

				if not self.paw_list[i][self.FRONT][self.RIGHT]:
					# if there was a paw in previous frame and it's no longer there
					paw_found = False
					value = None
					self.FR_list.append(value)

			except:
				pass

	def analyze_front_left(self):
		'''
		count the amount of paw present
		following left paw absence
		'''
		#print 'Currently performing: Steps analyze_front_left'
		paw_found = False
		previous_paw = 0
		current_paw = 0

		for i in xrange(self.list_size):
			try:
				if self.paw_list[i][self.FRONT][self.LEFT] and not self.paw_list[i-1][self.FRONT][self.LEFT]:
					# if the paw was previously in the air and is now down
					# increment the number of steps
					self.front_left_steps += 1
					paw_found = True

					# add value to stride length
					paw = self.paw_list[i][self.FRONT][self.LEFT]
					previous_paw = current_paw
					current_paw = paw[0]
					s_value = current_paw - previous_paw
					self.FL_stride.append(s_value)

				if self.paw_list[i][self.FRONT][self.LEFT]:
					# if there is paw present add to the graph list
					value = self.FL
					self.FL_list.append(value)

				if not self.paw_list[i][self.FRONT][self.LEFT]:
					# if there was a paw in previous frame and it's no longer there
					paw_found = False
					value = None
					self.FL_list.append(value)

			except:
				pass

	def analyze_back_right(self):
		'''
		count the amount of paw present
		following right paw absence
		'''
		#print 'Currently performing: Steps analyze_back_right'
		paw_found = False
		previous_paw = 0
		current_paw = 0

		for i in xrange(self.list_size):
			try:
				if self.paw_list[i][self.BACK][self.RIGHT] and not self.paw_list[i-1][self.BACK][self.RIGHT]:
					# if the paw was previously in the air and is now down
					# increment the number of steps
					self.back_right_steps += 1
					paw_found = True

					# add value to stride length
					paw = self.paw_list[i][self.BACK][self.RIGHT]
					previous_paw = current_paw
					current_paw = paw[0]
					s_value = current_paw - previous_paw
					self.BR_stride.append(s_value)

				if self.paw_list[i][self.BACK][self.RIGHT]:
					# if there is a paw present add to the paw graph
					value = self.BR
					self.BR_list.append(value)

				if not self.paw_list[i][self.BACK][self.RIGHT]:
					# if there was a paw in previous frame and it's no longer there
					paw_found = False
					value = None
					self.BR_list.append(value)

			except:
				pass

	def analyze_back_left(self):
		'''
		count the amount of paw present
		following left paw absence
		'''
		#print 'Currently performing: Steps analyze_back_left'
		paw_found = False
		previous_paw = 0
		current_paw = 0

		for i in xrange(self.list_size):
			try:
				if self.paw_list[i][self.BACK][self.LEFT] and not self.paw_list[i-1][self.BACK][self.LEFT]:
					# if the paw was previously in the air and is now down
					# increment the number of steps
					self.back_left_steps += 1
					paw_found = True

					# add value to stride length
					paw = self.paw_list[i][self.BACK][self.LEFT]
					previous_paw = current_paw
					current_paw = paw[0]
					s_value = current_paw - previous_paw
					self.BL_stride.append(s_value)

				if self.paw_list[i][self.BACK][self.LEFT]:
					# if there is a paw present add to paw graph
					value = self.BL
					self.BL_list.append(value)

				if not self.paw_list[i][self.BACK][self.LEFT]:
					# if there was a paw in previous frame and it's no longer there
					paw_found = False
					value = None
					self.BL_list.append(value)

			except:
				pass

	def plot_paw(self, linewidth=10):
		#print 'Currently performing: Steps plot_paw'
		# draw a line on a plane representing the paw
		print 'Starting the plot...'
		FR = np.array(self.FR_list)
		FL = np.array(self.FL_list)
		BR = np.array(self.BR_list)
		BL = np.array(self.BL_list)
		s_fr = FR.shape[0]
		s_fl = FL.shape[0]
		s_br = BR.shape[0]
		s_bl = BL.shape[0]
		i_fr = float(self.seconds)/float(s_fr)
		i_fl = float(self.seconds)/float(s_fl)
		i_br = float(self.seconds)/float(s_br)
		i_bl = float(self.seconds)/float(s_bl)
		x_fr = np.arange(0, self.seconds,i_fr)
		x_fl = np.arange(0, self.seconds,i_fl)
		x_br = np.arange(0, self.seconds,i_br)
		x_bl = np.arange(0, self.seconds,i_bl)

		fig, ax = plt.subplots()

		ax.plot(x_fr, FR, '-', label='FR', linewidth=linewidth)
		ax.plot(x_fl, FL, '-', label='FL', linewidth=linewidth)
		ax.plot(x_br, BR, '-', label='BR', linewidth=linewidth)
		ax.plot(x_bl, BL, '-', label='BL', linewidth=linewidth)

		legend = ax.legend(loc='upper right', shadow=True)
		axis = ax.axis([0,self.seconds,0,5])
		title = ax.set_title('Gait Plot')
		x_label = ax.set_xlabel('seconds')
		y_label = ax.set_ylabel('Paw')

		print 'finished....'
		return fig

	def analyze(self):
		#print 'Currently performing: Steps analyze'
		# initialize analysis of paw frame data
		self.analyze_front_right()
		self.analyze_front_left()
		self.analyze_back_right()
		self.analyze_back_left()

		self.set_cadence()
		self.set_variability()
		self.print_info()

	def set_cadence(self):
		#print 'Currently performing: Steps set_cadence'
		# total number of steps per sec
		total_steps = (self.front_left_steps + self.front_right_steps + self.back_left_steps + self.back_right_steps)
		
		self.cadence = total_steps / self.seconds

	def set_variability(self):
		#print 'Currently performing: Steps set_variability'
		# standard div of stride length
		FR = np.array(self.FR_stride)
		FL = np.array(self.FL_stride)
		BR = np.array(self.BR_stride)
		BL = np.array(self.BL_stride)

		# convert stride length to cm
		self.FR_stride = FR
		self.FL_stride = FL
		self.BR_stride = BR
		self.BL_stride = BL

		try:
			self.FR_stride = np.delete(self.FR_stride, 0)
			self.FL_stride = np.delete(self.FL_stride, 0)
			self.BR_stride = np.delete(self.BR_stride, 0)
			self.BL_stride = np.delete(self.BL_stride, 0)
		except:
			pass

		self.FR_var = float(np.std(self.FR_stride))
		self.FL_var = float(np.std(self.FL_stride))
		self.BR_var = float(np.std(self.BR_stride))
		self.BL_var = float(np.std(self.BL_stride))

		self.FR_var = (self.FR_var/self.frame_width)*self.conversion
		self.FL_var = (self.FL_var/self.frame_width)*self.conversion
		self.BR_var = (self.BR_var/self.frame_width)*self.conversion
		self.BL_var = (self.BL_var/self.frame_width)*self.conversion

	def print_info(self):
		#print 'Currently performing: Steps print_info'
		# save test analysis to csv
		np.savetxt('fr_stride',self.FR_stride,delimiter=',')
		np.savetxt('fl_stride',self.FL_stride,delimiter=',')
		np.savetxt('br_stride',self.BR_stride,delimiter=',')
		np.savetxt('bl_stride',self.BL_stride,delimiter=',')

		return len(self.FR_stride), len(self.FL_stride),len(self.BR_stride),len(self.BL_stride)

	def get_variable(self):
		#print 'Currently performing: Steps get_variable'
		# get variable of steps
		return self.cadence, self.FR_var, self.FL_var,self.BR_var,self.BL_var