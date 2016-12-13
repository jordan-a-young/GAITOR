import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.ndimage.filters import gaussian_filter as flt

class side():
	'''
	analysis of rodent side frame
	calculates position and velocity
	'''
	def __init__(self, side_position, angle, fps, conversion=108.5, frame_width=None):
		print 'Currently performing: Side init'
		# get the x values for the side position
		self.side_x = [s[0] for s in side_position]
		frames = len(self.side_x)

		self.angle = angle
		self.conversion = conversion
		self.frame_width = frame_width

		# convert pixels to cm
		self.convert_to_cm()

		# find the amount of seconds for video
		self.seconds = float(frames/fps)

		# set bin size for velocity analysis
		self.calc_bin_size()

		self.calc_vel_pos()
		self.calc_bin_vel_pos()
		self.calc_Xvel()

	def show(self):
		print 'Currently performing: Side show'
		plt.show()

	def calc_bin_size(self):
		print 'Currently performing: Side calc_bin_size'
		# set bin_size based for conversion of values into average
		self.bin_size = 2

	def calc_vel_pos(self):
		'''
		create an array for velocity,position and angle
		using the average of 2 values
		'''
		print 'Currently performing: Side calc_vel_pos'
		displacement = list()
		position = list()
		angle = list()

		for i in range(len(self.side_x)):
			if ((i + 1) % 2) == 0:
				current = float(self.side_x[i])
				previous = float(self.side_x[i-1])
				change = current - previous
				avg = current + previous
				avg = avg/2
				displacement.append(change)
				position.append(avg)

				# calculate the average of the angle
				a2 = float(self.angle[i])
				a1 = float(self.angle[i-1])
				a_avg = (a2+a1)/2
				angle.append(a_avg)

			else:
				pass

		disp = np.array(displacement)

		self.position = np.array(position)

		time_increment = float(self.seconds)/float(len(self.side_x))

		# set velocity array
		vel = [float(d)/(2.0*time_increment) for d in disp]
		self.velocity = np.array(vel)

		# set the angle array
		self.angle = np.array(angle)

	def calc_bin_vel_pos(self):
		print 'Currently performing: Side calc_bin_vel_pos'
		# return the figure for displacement by velocity
		vel_size = len(self.velocity)
		remainder = vel_size%self.bin_size
		new_vel = [ v for v in self.velocity]
		new_pos = [p for p in self.position]

		for i in range(remainder):
			new_vel.append(0)
			new_pos.append(0)

		vel = np.array(new_vel)
		pos = np.array(new_pos)
		row = len(vel)/self.bin_size

		vel = np.reshape(vel,(row,self.bin_size))
		pos = np.reshape(pos,(row,self.bin_size))

		self.bin_velocity = np.mean(vel,axis=1)
		self.bin_position = np.mean(pos,axis=1)
		# print 'Bin Vel: ' + str(len(self.bin_velocity)) +'Pos Size' + str(len(self.bin_position))

	def calc_Xvel(self):
		print 'Currently performing: Side calc_Xvel'
		# calculate the average velocity
		new_vel = self.velocity[~np.isnan(self.velocity)]
		self.mean_vel = np.mean(new_vel)

	def get_Xvel(self):
		print 'Currently performing: Side get_Xvel'
		return self.mean_vel

	def convert_to_cm(self):
		print 'Currently performing: Side convert_to_cm'
		# convert pixels to cm
		if self.frame_width:
			maxPixel = self.frame_width
			temp = self.side_x
			self.side_x = [(float(d)/float(maxPixel))*self.conversion for d in temp ]
			# print self.side_x
		else:
			pass

	def plot(self):
		print 'Currently performing: Side plot'
		# plot velocity by angle
		x = np.nan_to_num(self.position)
		y = np.nan_to_num(self.velocity)

		x = self.error_corr(x)
		y = self.error_corr_v(y)

		# gaussian smooth velocity
		y_b = flt(y, sigma=5)
		y = y_b

		fig, ax = plt.subplots()

		ax.plot(x,y)
		ax.scatter(x,y)

		title = ax.set_title('Velocity Plot')
		ax.set_xlabel('Position(cm)')
		ax.set_ylabel('Velocity(cm/sec)')

		return fig

	def plot2(self):
		print 'Currently performing: Side plot2'
		# plot velocity by angle
		y = np.nan_to_num(self.angle)
		x = np.nan_to_num(self.velocity)

		# print ' size of angle: ' + str(len(y))
		# print 'size of veloc: ' + str(len(x))

		# x = self.error_corr(x)
		x = self.error_corr_v(x)

		# gaussian smooth velocity
		x_b = flt(x, sigma=5)
		x = x_b

		fig, ax = plt.subplots()

		# ax.plot(x,y)
		ax.scatter(x,y)

		title = ax.set_title('Arch Plot')
		ax.set_xlabel('Velocity(cm/sec)')
		ax.set_ylabel('Arch Angle(radians)')

		return fig

	def error_corr(self, p):
		print 'Currently performing: Side error_corr'
		# replace invalid positions
		for i, x in enumerate(p):
			try:
				if (x < p[i-1]) and (i > 0):
					p[i] = p[i-1]
				else:
					pass

			except:
				pass
		return p

	def error_corr_v(self, v):
		print 'Currently performing: Side error_corr_v'
		# replace invalid positions
		for i, x in enumerate(v):
			try:
				if (x < 0) and (i > 0):
					v[i] = v[i-1]
				if (x < 0) and (i == 0):
					v[0] = v[1]

				else:
					pass

			except:
				pass

		return v

	def outlier(self, v):
		print 'Currently performing: Side outlier'
		# remove outliers that are beyond 2 standard dev
		v1 = [v[i] if abs(x-np.mean(v))<2*np.std(v) else v[i-1] for i,x in enumerate(v)]

		return v1