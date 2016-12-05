import cv2
import numpy as np
from arch import get_arch_data
from cv2.cv import CV_CAP_PROP_POS_FRAMES, CV_CAP_PROP_FRAME_COUNT
import matplotlib
from steps import steps as s
class frame():
	'''
	represents a single frame of video
	collects and stores relevant data
	'''
	def __init__(self, top, bot, top_mask, bot_mask, use_profile=False):
		'''
		initialized with a top frame, bottom frame,
		and bottom mask array
		if not 'use_profile', then the frame is always valid
		'''
		#print 'Currently performing: Frame init'
		self.use_profile = use_profile
		self.top_mask = top_mask

		# empty 1x2 array to hold the side position as they are found
		self.side_geom = np.empty([1,2])

		# empty 2x2 array to hold feet positions as they are found
		self.foot_geom = np.empty([2, 2])

		# calculate the critical points
		self.valid_flag = self.calc_critical_points(top_mask) or not use_profile

		# calculate the foot positions if valid
		if self.valid_flag:
			self.calc_side_position(top_mask)
			self.calc_feet_positions(bot_mask)

	def calc_critical_points(self, top):
		'''
		finds the highest point on the rat's body
		returns True only if this is a valid frame

		frames are valid if the entire rat's body is on screen
		'''
		#print 'Currently performing: Frame calc_critical_points'
		# find contours
		contours, hierarchy = cv2.findContours(top, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		# valid frame will have contours
		if not contours:
			self.critical_points = [None, None, None]
			return False

		else:
			# first, find the largest contour
			largest = contours[0]
			for c in contours:
				if len(c) > len(largest):
					largest = c

			# find rightmost and topmost point
			# rat's nose
			front = tuple(largest[largest[:, :, 0].argmax()][0])
			# rat's hunch
			hunch = tuple(largest[largest[:, :, 1].argmin()][0])
			# rats butt
			rear = tuple(largest[largest[:, :, 0].argmin()][0])

			try:
				x_value = hunch[0] - rear[0]
				x_value += hunch[0]
				mid = tuple(largest[np.where(largest[:,:,0] == x_value)][0])

				# rat's feet
				feet = tuple(largest[largest[:,:,1].argmax()][0])
				feet[0] = front[0]

			except:
				mid = front
				feet = front

			front = np.array(front)
			hunch = np.array(hunch)
			rear = np.array(rear)
			feet = np.array(feet)
			mid = np.array(mid)

			# valid frame has the rat's full body visible
			# and at least 10 pixels from the edges of the screen
			h, w = top.shape

			# is this frame valid?
			valid = front[0] < w - 10		# right point must have 10px pad
			valid = valid and rear[0] > 10	# so must rear limit

			if not valid:
				self.critical_points = [[np.nan,np.nan,np.nan,np.nan], [np.nan,np.nan,np.nan,np.nan]]
				return False

			# save values and return
			self.critical_points = [[rear[0],hunch[0],feet[0],mid[0]],[rear[1],hunch[1],feet[1],mid[1]]]

			return True

	def calc_side_position(self, mask):
		#print 'Currently performing: Frame calc_side_position'
		# calculates the position of rat in the side image
		# empty 1x2 array to hold side position as they are found
		self.side_geom = [np.nan, np.nan]
		self.side_contout = [np.nan]
		try:
			# find the rat contour using edge detection
			edge = cv2.Canny(mask, 0, 15)
			cnts, h = cv2.findContours(edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			
			# first, find the largest contour
			cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
			rat = cnts[0]

			self.side_contour = rat
			self.side_geom = get_side_contour(mask)

			# find the moment of contour and use to find centroid
			M = cv2.moments(cnts[0])
			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])

		except:
			pass

	def calc_feet_positions(self, mask):
		'''
		calculates the foot positions relative to each other
		by finding the extreme points of the detected feet in the given
		foot mask
		'''
		#print 'Currently performing: Frame calc_feet_positions'
		# empty 2x2 array to hold feet positions as they are found
		self.foot_geom = [[None,None], [None,None]]
		try:
			rear_limit, topmost, rightmost, _ = self.critical_points[0]

		except:
			pass

		# ignore detected values behind rear line by drawing over them
		# unless not use_profile
		if self.use_profile:
			h, w = mask.shape
			cv2.rectangle(mask, (0, 0), (rear_limit, h), 0, -1)

		# blur, to merge adjacent toes and footpads
		mask = cv2.blur(mask, (10,10))

		# is this still a valid frame?
		if not mask.any():
			return

		# find all the contours
		else: 
			contours,hierarchy = cv2.findContours(mask, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
			center = lambda box: (box[0] + box[2]/2, box[1]+ box[3]/2)
			centers = [center(cv2.boundingRect(cnt)) for cnt in contours]

		# identify feet positions
		dstk = np.dstack(centers)[0]	# rearrange centers [[x's],[y's]]
		rear = np.min(dstk[0])			# rearmost x value
		front = np.max(dstk[0])			# frontmost x value
		left = np.min(dstk[1])			# leftmost y
		right = np.max(dstk[1])			# rightmost y

		for c in centers:
			# distance to frontmost
			front_dist = front - c[0]
			
			# distance to rearmost
			rear_dist = c[0] - rear

			# distance to leftmost
			left_dist = c[1] - left
			
			# distance to rightmost foot
			right_dist = right - c[1]

			# is it closer to the front or the back?
			x = int(front_dist <= rear_dist)

			# is it closer to the left or the right?
			y = int(left_dist <= right_dist)

			# Is there already a foot here?
			old_foot = self.foot_geom[x][y]

			# if so, this value becomes the mean of the old and new feet
			if old_foot:
				new_x = np.mean([c[0], old_foot[0]])
				new_y = np.mean([c[1], old_foot[1]])
			else:
				new_x, new_y = c

			self.foot_geom[x][y] = [new_x, new_y]

	def calc_arch_data(self):
		'''
		calculates the 2nd degree polynomial coefficients
		and the curvature of the rat's back
		coeffs are an empty array and curvature is null if there is no data
		'''
		#print 'Currently performing: Frame calc_arch_data'
		self.arch_angle, self.arch_contour = get_arch_data(self, self.top_mask)

	def get_arch_data(self):
		#print 'Currently performing: Frame get_arch_data'
		# return the angle and the contour fot he rat's back
		self.calc_arch_data()
		return self.arch_angle, self.arch_contour

	def get_critical_points(self):
		#print 'Currently performing: Frame get_critical_points'
		# returns rear_limit, topmost, rightmost
		return self.critical_points

	def get_side_position(self):
		'''
		return a 1x2 array containing the centroid
		of the side position found
		'''
		#print 'Currently performing: Frame get_side_position'
		return self.side_geom

	def get_side_contour(self):
		#print 'Currently performing: Frame get_side_contour'
		# return the entire contour array for side image
		return self.side_contour

	def get_foot_positions(self):
		'''
		returns 2x2 array containing all detected foot positions
		element 0,0 corresponds to rear left foot
		missing feet are None
		'''
		#print 'Currently performing: Frame get_foot_positions'
		return self.foot_geom

	def get_valid_flag(self):
		#print 'Currently performing: Frame get_valid_flag'
		# return if frame is valid
		return self.valid_flag

def get_next_frame(trial):
		'''
		pulls the next frame from a trial video instance
		and returns an instance of frame.

		returns none if there is no data to read
		'''
		#print 'Currently performing: Frame get_next_frame'
		ret, top, bot = trial.read()

		if not ret:
			return None

		top_mask = trial.get_top_mask()
		bot_mask = trial.get_bottom_mask()

		return frame(top, bot,top_mask,bot_mask)

# find largest side contour
def get_side_contour(top_mask):
	#print 'Currently performing: Frame get_side_contour'
	try:
		edged = cv2.Canny(top_mask,0,15)
		cnts,h = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		# first, find the largest contour
		# TODO sort and get first element for nlog(n) time
		cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
		rat = cnts[0]

		# M = cv2.moments(cnts[0])
		M = cv2.moments(rat)
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])
		center = np.array((cx,cy))
		# print 'Trial center:'
		# print center

		return center
	except:
		return np.array([np.nan,np.nan])

def dostuff(i, c, f, o):
	#print 'Currently performing: Frame dostuff'
	# print 'i: ' + str(i)
	# print 'c: ' + str(c)
	if(i >= c):
		print 'doing stuff'
		list_size = len(f)
		steps = s(f,list_size,29)

		c,fr,fl,br,bl = steps.get_variable()
		file = open(o,'w')
		file.write(o)
		file.write('Cadence: '+str(c))
		file.write('/n')
		file.write('FR Variability: '+str(fr))
		file.write('/n')
		file.write('FL Variability: '+str(fl))
		file.write('/n')
		file.write('BR Variability: '+str(br))
		file.write('/n')
		file.write('BL Variability: '+str(bl))
		file.close()
		# plot
		steps.plot_paw()
	else:
		pass
		# print ' not doing stuff'

# unit testing below
def debug(video, output):

		import trial_video
		import numpy as np
		import itertools

		trial = trial_video.trial_video(video,horizon=801,top_thresh=15,bot_thresh=83)
		count = trial.get(CV_CAP_PROP_FRAME_COUNT)


		frame_list = list()
		i = 0
		while 1:
			i +=1
			# print 'i %d2:' %i
			# print 'Count: ' + str(count)
			this_frame = get_next_frame(trial)
			ret, raw = trial.get_raw_frame()

			if not ret:
				break

			feet = this_frame.get_foot_positions()
			# this_frame = get_next_frame(trial)
			if this_frame.get_valid_flag():

				# feet = this_frame.get_foot_positions()
				rat_p = this_frame.get_side_position()
				print 'final pos'
				print rat_p
			else:
				# feet = None
				pass

			# print feet
			frame_list.append(feet)
			top = trial.get_top_mask()
			bot= trial.get_bottom_mask()
			try:
				rat = get_side_contour(top)
				# rat_x,rat = get_side_contour(top)
				# x,y,w,h = rat
				cv2.drawContours(raw,[rat],-1,(0,255,0),3)
				# cv2.rectangle(raw,(x,y),(x+w,y+h),(255,0,0))
			except:
				pass

			# cv2.circle(raw,rat_x[0][0],8,(255,0,255),3)
			# print ' Rat Position: '
			# print rat

			for foot in list(itertools.chain(*feet)):
				if foot:
						try:
								cv2.circle(raw, (foot[0], foot[1] + 801), 20, (0, 255, 0), 5)
						except:
								pass
			raw = trial.resize_frame(raw,500)

			cv2.imshow('frame',raw)

			dostuff(i,int(count),frame_list,output)
			if( i== int(count)):
				break
			if cv2.waitKey(10) & 0xFF == ord('q'):
				break

		trial.release()
		cv2.destroyAllWindows()

if __name__ == '__main__':

		import sys

		video = sys.argv[1]
		output = sys.argv[2]
		debug(video,output)