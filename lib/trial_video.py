from random import sample
import cv2
import numpy as np
from cv2.cv import CV_CAP_PROP_FRAME_HEIGHT, CV_CAP_PROP_FRAME_WIDTH
from cv2.cv import CV_CAP_PROP_POS_FRAMES, CV_CAP_PROP_FRAME_COUNT

'''
# usage example

# read in green_bg.mp4 with horizon 200 pixels down
trial = trial_video.('green_bg.mp4', horizon=200)

# read status, top, and bottom of frame
ret, bot, top = trial.read()
'''

# get/set attribute values
TRIAL_HORIZON = 19
TRIAL_SIDE_THRESH = 20
TRIAL_BOT_THRESH = 21
BLUR_SIGMA = 22
BLUR_TOP = 1023
BLUR_BOT = 1024
RET = 1025

class trial_video():
	'''
	represents an instance of a gait tracking trial
	from a given video stream
	'''
	def __init__(self, video_stream, horizon=None, side_thresh=0, bot_thresh=160, blur=1, tblur=1, bblur=1):
		'''
		Initialize with a video stream (filename or device number),
		and a 'horizon line' tuple

		top and bottom thresholds are percentile brightness thresholds
		'''
		print 'Currently performing: TV init'
		# to store last read value and unmodified video frame
		self.ret = None
		self.raw_frame = None

		# last read top and bottom views
		self.top = None
		self.bot = None

		self.fgbg = cv2.BackgroundSubtractorMOG2()

		# initialize capture with video_stream (filename or device number)
		self.video_capture = cv2.VideoCapture(video_stream)

		'''
		horizon is a tuple of two points, who when connected divide
		the mirror from the side view

		If no horizon is given, horizon line will partition image
		horizontally in half
		'''

		# how much to blur?
		self.blur_sigma = blur
		self.blur_top = tblur
		self.blur_bot = bblur

		self.horizon = horizon
		if not horizon:
			# create points from left to right at half of the height
			self.horizon = self.video_capture.get(CV_CAP_PROP_FRAME_HEIGHT) / 2

		if side_thresh and bot_thresh:
			# set brightness threshold based on random samples
			self.set_thresh_vals(side_thresh, bot_thresh)

		else:
			# just use 0 (pure black) caller wants to set thresh later
			self.side_thresh_val = 0
			self.bot_thresh_val = 0
			self.top_thresh_percent = 100
			self.bot_thresh_percent = 100

	def resize_frame(self, frame, pixel=None):
		# resize the frame to specified pixel area or 1000 if no pixel value specified
		print 'Currently performing: TV resize_frame'
		# maintain aspect ratio of the image = keep image from distorting
		if not pixel:
			r = 1000.0 / frame.shape[1]
			dim = (1000, int(frame.shape[0]*r))
		else:
			r = (float)(pixel) / frame.shape[1]
			dim = (pixel, int(frame.shape[0]*r))

		# re-sizing the image
		resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

		return resized

	def read(self):
		'''
		returns a retval, the top half of the image, and the bottom
		half of the image according to the horizon value
		'''
		print 'Currently performing: TV read'
		# read the next frame
		ret, frame = self.video_capture.read()
		# print 'ret: ' + str(ret)

		self.ret = ret
		if not ret:# nothing to read, end of file or error
			return ret, None, None

		# blur image to reduce noise
		if self.blur_sigma:
			frame = cv2.blur(frame, (self.blur_sigma, self.blur_sigma))

		# frame and read status after blur
		self.raw_frame = frame

		# remove background
		bg = self.fgbg.apply(frame)
		frame[np.where(bg == 0)] = (0,0,0)

		# get width and height of
		height = self.video_capture.get(CV_CAP_PROP_FRAME_HEIGHT)
		width = self.video_capture.get(CV_CAP_PROP_FRAME_WIDTH)

		# top half of image
		top_mat = frame.copy()[0:self.horizon, 0:width]
		if self.blur_top:
			top_mat = cv2.blur(top_mat, (self.blur_top, self.blur_top))

		# bottom half of image
		bottom_mat = frame.copy()[self.horizon:height, 0:width]
		if self.blur_bot:
			bottom_mat = cv2.blur(bottom_mat, (self.blur_bot, self.blur_bot))

		# update last read frames
		self.top = top_mat
		self.bot = bottom_mat

		return ret, top_mat, bottom_mat

	def set_thresh_vals(self, top_thresh_percent, bot_thresh_percent, n=None, use_percentile=False):
		'''
		sets the value of the top and bottom threshold values based on
		given percentiles, using a random sample of video frames

		calling this function resets the video capture to frame zero

		n specifies sample size (frames),
		default size is 8% of total frame count
		custom n-value is used for testing
		'''
		print 'Currently performing: TV set_thresh_vals'
		if not use_percentile:
			'''
			in this case thresh_percent arguments represent
			explicit brightness values
			'''

			self.side_thresh_val = top_thresh_percent
			self.bot_thresh_val = bot_thresh_percent
			return

		# get current frame number, to reset
		current_frame = int(self.video_capture.get(CV_CAP_PROP_POS_FRAMES))

		# get sample frame counts
		frame_count = int(self.video_capture.get(CV_CAP_PROP_FRAME_COUNT))
		if not n: # then use default size
			n = int(frame_count * .08) # 8 percent of total frames
		
		sample_index = np.linspace(1, frame_count - 1, n)

		# calculate mean percentile over n frames
		bot_vals = []
		top_vals = []

		for i in sample_index:
			# set capture to frame i
			self.video_capture.set(CV_CAP_PROP_POS_FRAMES, int(i))
			# read top and bottom frame
			ret, top, bot = self.read()

			# attempt to calculate percentile from top and bottom
			# append percentile to list
			if ret:
				# to catch the condition where the horizon is at
				# the top or bottom of the frame
				try:
					top_val = np.percentile(top, top_thresh_percent)
				except:
					 top_val = 0
				try:
					bot_val = np.percentile(bot, bot_thresh_percent)
				except:
					bot_val = 0

				bot_vals.append(bot_val)
				top_vals.append(top_val)

		# set instance variables for reference
		self.top_thresh_percent = top_thresh_percent
		self.bot_thresh_percent = bot_thresh_percent

		# set thresh values to mean percentile
		self.side_thresh_val = int(np.mean(top_vals))
		self.bot_thresh_val = int(np.mean(bot_vals))

		# 'rewind' video
		self.video_capture.set(CV_CAP_PROP_POS_FRAMES, current_frame)

	def set_horizon(self, h):
		# used to set horizon line after initialization
		print 'Currently performing: TV set_horizon'
		self.horizon = h

	def set_blur_sigma(self, s):
		'''
		set the x and y sigma value for the blur,
		or set to 0 for no blur
		'''
		print 'Currently performing: TV set_blur_sigma'
		self.blur_sigma = s

	def get_raw_frame(self):
		# gets latest read value and unmodified frame
		print 'Currently performing: TV get_raw_frame'
		return self.ret, self.raw_frame

	def get_top_mask(self):
		'''
		returns the thresholded mask of the last
		read top view, by finding the largest contour in the image.
		'''
		print 'Currently performing: TV get_top_mask'
		# to catch condition with empty or none array
		try:
			# create mask from greyscale version of top frame
			mask = cv2.cvtColor(self.top, cv2.COLOR_BGR2GRAY)
			bg = self.fgbg.apply(mask)
			mask[np.where(bg == 0)] = 255
			mask = cv2.blur(mask, (self.blur_top, self.blur_top))

			# bring up everything above threshold
			mask[np.where(mask >= self.side_thresh_val)] = 255

			# bring everything else down
			mask[np.where(mask < self.side_thresh_val)] = 0

			return mask
		# return empty array
		except: 
			return np.zeros(0)

	def get_top_mat(self):
		# returns the top half of the raw matrix
		print 'Currently performing: TV get_top_mat'
		return self.top

	def get_bottom_mask(self):
		'''
		returns the thresholded mask of the last
		read bottom view
		'''
		print 'Currently performing: TV get_bottom_mask'
		# to catch condition with empty or none array
		try:
			# create mask from greyscale version of bottom frame
			mask = cv2.cvtColor(self.bot, cv2.COLOR_BGR2GRAY)
			bg = self.fgbg.apply(mask)
			mask[np.where(bg == 0)] = 255
			mask = cv2.blur(mask,(self.blur_bot, self.blur_bot))

			# bring up everything above threshold
			mask[np.where(mask >= self.bot_thresh_val)] = 255

			# bring everything else down
			mask[np.where(mask < self.bot_thresh_val)] = 0

			return mask
		# return empty array
		except: 
			return np.zeros(0)

	def get(self, prop):
		'''
		used to retrieve properties of this trial
		or properties of the cv2.VideoCaputre instance
		'''
		print 'Currently performing: TV get'
		if prop == TRIAL_HORIZON:
			return self.horizon
		if prop == TRIAL_SIDE_THRESH:
			# return self.top_thresh_percent
			return self.side_thresh_val
		if prop == TRIAL_BOT_THRESH:
			# return self.bot_thresh_percent
			return self.bot_thresh_val
		if prop == BLUR_SIGMA:
			return self.blur_sigma
		if prop == BLUR_TOP:
			return self.blur_top
		if prop == BLUR_BOT:
			return self.blur_bot
		if prop == RET:
			return self.ret

		# return property of video capture
		return self.video_capture.get(prop)

	def set(self, prop, value):
		print 'Currently performing: TV set'
		# used to set property values
		if prop == CV_CAP_PROP_POS_FRAMES:
			self.video_capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,value)
		if prop == TRIAL_HORIZON:
			self.horizon = value
		if prop == TRIAL_SIDE_THRESH:
			self.side_thresh_val = value
		if prop == TRIAL_BOT_THRESH:
			self.bot_thresh_val = value
		if prop == BLUR_SIGMA:
			self.blur_sigma = value
		if prop == BLUR_TOP:
			self.blur_top = value
		if prop == BLUR_BOT:
			self.blur_bot = value

	def release(self):
		# closes all open files
		print 'Currently performing: TV release'
		self.video_capture.release()

# tests beyond this point
def nothing(*k):
	# GIVEN ANYTHING EVER DOES ABSOLUTELY NOTHING
	pass

def debug(vid):
	import cv2
	
	cv2.namedWindow('test')
	cv2.namedWindow('bottom mask')

	# trackbars
	cv2.createTrackbar('horizon','test',1,719,nothing)
	cv2.createTrackbar('top thresh','test',0,255,nothing)
	cv2.createTrackbar('bot thresh','test',0,255,nothing)
	cv2.createTrackbar('blur sigma','test',0,30,nothing)

	trial = trial_video(vid, horizon=None, side_thresh=None, bot_thresh=None )

	while(1):
		h = cv2.getTrackbarPos('horizon','test')
		t = cv2.getTrackbarPos('top thresh','test')
		b = cv2.getTrackbarPos('bot thresh','test')
		s = cv2.getTrackbarPos('blur sigma','test')

		ret, top, bot = trial.read()
		if not ret:# start over
			# cheating
			# python does not believe in private properties
			# python is a left wing anarchist
			trial.video_capture.set(CV_CAP_PROP_POS_FRAMES,0)
			print 'Resetting video'

		else:
			ret, frame = trial.get_raw_frame()
			if trial.get(BLUR_SIGMA) != s:# make a new instance
				print 'creating new instance with blur sigma ' + str(s)
				trial.set_blur_sigma(s)

			if trial.get(TRIAL_SIDE_THRESH) != t or trial.get(TRIAL_BOT_THRESH) != b or trial.get(TRIAL_HORIZON) != h:
					trial.set_thresh_vals(t, b, use_percentile=False)
					trial.set_horizon(h)

			cv2.line(frame, (0, h), (2000, h), (0, 255, 0))
			cv2.imshow('test', frame)
			cv2.imshow('bottom mask', trial.get_bottom_mask())
			cv2.imshow('bottom', bot)
			top_mask = trial.get_top_mask()
			print 'Top mask: {}'.format(top_mask.shape)
			
			if top_mask.any():
				cv2.imshow('top mask', trial.get_top_mask())
				cv2.imshow('top', top)
			
			if cv2.waitKey(60) & 0xFF == ord('q'):
				break

	trial.release()
	cv2.destroyAllWindows()

	return trial_video(vid, horizon=h, side_thresh=t, bot_thresh=b, blur=s)

if __name__ == '__main__':

		import sys
		debug(sys.argv[1])