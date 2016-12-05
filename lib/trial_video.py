from random import sample
import cv2
import numpy as np
from cv2.cv import CV_CAP_PROP_FRAME_HEIGHT, CV_CAP_PROP_FRAME_WIDTH
from cv2.cv import CV_CAP_PROP_POS_FRAMES, CV_CAP_PROP_FRAME_COUNT

# get/set attribute values
TRIAL_HORIZON = 19
TRIAL_TOP_THRESH = 20
TRIAL_BOT_THRESH = 21
BLUR_SIGMA = 22
BLUR_TOP = 1023
BLUR_BOT = 1024
RET = 1025
CROP_UP = 1005
CROP_DOWN = 1006
TOP_CROP_RIGHT = 1007
TOP_CROP_LEFT = 1008
BOT_CROP_RIGHT = 1009
BOT_CROP_LEFT = 1010

class trial_video():
	'''
	represents an instance of a gait tracking trial
	from a given video stream
	'''
	def __init__(self, video_stream, horizon=None, top_thresh=100, bot_thresh=100, blur=1, tblur=1, bblur=1):
		'''
		Initialize with a video stream (filename or device number),
		and a 'horizon line' tuple

		top and bottom thresholds are percentile brightness thresholds
		'''
		# to store last read value and unmodified video frame
		self.ret = None
		self.raw_frame = None

		# last read top and bottom views
		self.top = None
		self.bot = None

		self.fgbg = cv2.BackgroundSubtractorMOG2()

		# initialize capture with video_stream (filename or device number)
		self.video_capture = cv2.VideoCapture(video_stream)

		# values
		self.blur_sigma = blur
		self.blur_top = tblur
		self.blur_bot = bblur
		self.crop_up = 1
		self.crop_down = 1
		self.top_crop_left = 1
		self.top_crop_right = 1
		self.bot_crop_left = 1
		self.bot_crop_right = 1

		# if no horizon, horizon = height/2
		self.horizon = horizon
		if not horizon:
			self.horizon = self.video_capture.get(CV_CAP_PROP_FRAME_HEIGHT) / 2

		if top_thresh and bot_thresh:
			# set brightness threshold based on random samples
			self.set_thresh_vals(top_thresh, bot_thresh)

		else:
			# just use 0 (pure black) caller wants to set thresh later
			self.top_thresh_val = 0
			self.bot_thresh_val = 0
			self.top_thresh_percent = 100
			self.bot_thresh_percent = 100

	def resize_frame(self, frame, pixel=None):
		# resize the frame to specified pixel area or 1000 if no pixel value specified
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
		# read the next frame
		ret, frame = self.video_capture.read()

		self.ret = ret
		# nothing to read, end of file or error
		if not ret:
			return ret, None, None

		# blur image to reduce noise
		if self.blur_sigma:
			frame = cv2.blur(frame, (self.blur_sigma, self.blur_sigma))

		# frame and read status after blur
		self.raw_frame = frame

		# remove background
		bg = self.fgbg.apply(frame)
		frame[np.where(bg == 0)] = (0,0,0)

		# get width and height
		height = self.video_capture.get(CV_CAP_PROP_FRAME_HEIGHT)
		width = self.video_capture.get(CV_CAP_PROP_FRAME_WIDTH)	

		# check crop values
		self.crop_val_check()

		# update last read frames
		self.top = self.crop_top(frame, height, width)
		self.bot = self.crop_bot(frame, height, width)

		return ret, self.top, self.bot

	def set_thresh_vals(self, top_thresh_percent, bot_thresh_percent, n=None, use_percentile=False):
		'''
		sets the value of the top and bottom threshold values based on
		given percentiles, using a random sample of video frames

		calling this function resets the video capture to frame zero

		n specifies sample size (frames),
		default size is 8% of total frame count
		custom n-value is used for testing
		'''
		if not use_percentile:
			'''
			in this case thresh_percent arguments represent
			explicit brightness values
			'''

			self.top_thresh_val = top_thresh_percent
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
		self.top_thresh_val = int(np.mean(top_vals))
		self.bot_thresh_val = int(np.mean(bot_vals))

		# 'rewind' video
		self.video_capture.set(CV_CAP_PROP_POS_FRAMES, current_frame)

	def set_horizon(self, h):
		# used to set horizon line after initialization
		self.horizon = h

	def set_blur_sigma(self, s):
		'''
		set the x and y sigma value for the blur,
		or set to 0 for no blur
		'''
		self.blur_sigma = s

	def get_raw_frame(self):
		# gets latest read value and unmodified frame
		return self.ret, self.raw_frame

	def get_top_mask(self):
		'''
		returns the thresholded mask of the last
		read top view, by finding the largest contour in the image.
		'''
		# to catch condition with empty or none array
		try:
			# create mask from gray scale version of top frame
			mask = cv2.cvtColor(self.top, cv2.COLOR_BGR2GRAY)
			bg = self.fgbg.apply(mask)
			mask[np.where(bg == 0)] = 255
			mask = cv2.blur(mask, (self.blur_top, self.blur_top))

			# bring up everything above threshold
			mask[np.where(mask >= self.top_thresh_val)] = 255

			# bring everything else down
			mask[np.where(mask < self.top_thresh_val)] = 0

			return mask
		# return empty array
		except: 
			return np.zeros(0)

	def get_top_mat(self):
		# returns the top half of the raw matrix
		return self.top

	def get_bottom_mask(self):
		'''
		returns the thresholded mask of the last
		read bottom view
		'''
		# to catch condition with empty or none array
		try:
			# create mask from gray scale version of bottom frame
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

	def crop_val_check(self):
		# check if crop values will work
		if self.crop_up < 1 or self.crop_up > 100:
			self.crop_up = 1

		if self.crop_down < 1 or self.crop_down > 100:
			self.crop_down = 1

		if self.top_crop_left < 1 or self.top_crop_left > 100:
			self.top_crop_left = 1

		if self.top_crop_right < 1 or self.top_crop_right > 100:
			self.top_crop_right = 1

		if self.bot_crop_left < 1 or self.bot_crop_left > 100:
			self.bot_crop_left = 1

		if self.bot_crop_right < 1 or self.bot_crop_right > 100:
			self.bot_crop_right = 1

	def crop_top(self, frame, height, width):
		# calculate crop up
		upCrop = round((self.crop_up*self.horizon)/100)

		# calculate crop left/right
		meridian = round((width/2))
		leftCrop = round((self.top_crop_left*meridian)/100)
		rightCrop = round((self.top_crop_right*meridian)/100)
		rightCrop = width - rightCrop

		# top half of image
		top_mat = frame.copy()[upCrop:self.horizon, leftCrop:rightCrop]
		if self.blur_top:
			top_mat = cv2.blur(top_mat, (self.blur_top, self.blur_top))

		return top_mat

	def crop_bot(self, frame, height, width):
		# calculate crop down
		diff = height - self.horizon
		downCrop = round((self.crop_down*diff)/100)
		downCrop = height - downCrop

		# calculate crop left/right
		meridian = round((width/2))
		leftCrop = round((self.bot_crop_left*meridian)/100)
		rightCrop = round((self.bot_crop_right*meridian)/100)
		rightCrop = width - rightCrop

		# bottom half of image
		bottom_mat = frame.copy()[self.horizon:downCrop, leftCrop:rightCrop]
		if self.blur_bot:
			bottom_mat = cv2.blur(bottom_mat, (self.blur_bot, self.blur_bot))

		return bottom_mat

	def get(self, prop):
		'''
		used to retrieve properties of this trial
		or properties of the cv2.VideoCaputre instance
		'''
		if prop == TRIAL_HORIZON:
			return self.horizon
		if prop == TRIAL_TOP_THRESH:
			return self.top_thresh_val
		if prop == TRIAL_BOT_THRESH:
			return self.bot_thresh_val
		if prop == BLUR_SIGMA:
			return self.blur_sigma
		if prop == BLUR_TOP:
			return self.blur_top
		if prop == BLUR_BOT:
			return self.blur_bot
		if prop == RET:
			return self.ret
		if prop == CROP_UP:
			return self.crop_up
		if prop == CROP_DOWN:
			return self.crop_down
		if prop == TOP_CROP_LEFT:
			return self.top_crop_left
		if prop == TOP_CROP_RIGHT:
			return self.top_crop_right
		if prop == BOT_CROP_LEFT:
			return self.bot_crop_left
		if prop == BOT_CROP_RIGHT:
			return self.bot_crop_right

		# return property of video capture
		return self.video_capture.get(prop)

	def set(self, prop, value):
		# used to set property values
		if prop == CV_CAP_PROP_POS_FRAMES:
			self.video_capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, value)
		if prop == TRIAL_HORIZON:
			self.horizon = value
		if prop == TRIAL_TOP_THRESH:
			self.top_thresh_val = value
		if prop == TRIAL_BOT_THRESH:
			self.bot_thresh_val = value
		if prop == BLUR_SIGMA:
			self.blur_sigma = value
		if prop == BLUR_TOP:
			self.blur_top = value
		if prop == BLUR_BOT:
			self.blur_bot = value
		if prop == CROP_UP:
			self.crop_up = value
		if prop == CROP_DOWN:
			self.crop_down = value
		if prop == TOP_CROP_LEFT:
			self.top_crop_left = value
		if prop == TOP_CROP_RIGHT:
			self.top_crop_right = value
		if prop == BOT_CROP_LEFT:
			self.bot_crop_left = value
		if prop == BOT_CROP_RIGHT:
			self.bot_crop_right = value

	def release(self):
		# closes all open files
		#print 'Currently performing: TV release'
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

	trial = trial_video(vid, horizon=None, top_thresh=None, bot_thresh=None )

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

			if trial.get(TRIAL_TOP_THRESH) != t or trial.get(TRIAL_BOT_THRESH) != b or trial.get(TRIAL_HORIZON) != h:
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

	return trial_video(vid, horizon=h, top_thresh=t, bot_thresh=b, blur=s)

if __name__ == '__main__':
	import sys
	debug(sys.argv[1])