import cv2
import numpy as np

class Tracker():
	def __init__(self, file_name, roi):
		print 'Tracker class'
		self.file_name = file_name
		self.frames = []
		self.roi = roi
		
		self.create_trackbars()

	def read_video(self):
		cap = cv2.VideoCapture(self.file_name)
		empty_frame = None
		
		while True:
			# Start reading video
			ret, frame = cap.read()

			# Check if file could be opened
			if not ret:
				print 'Error occurred opening video.'
				break

			# Check whether presets need to be Saved/Loaded
			self.preset_check()

			# Check if we have an empty frame
			if empty_frame is None:
				empty_frame = frame

			# Get trackbar values
			median_val, blur_val, thresh_val, r_val = self.get_trackbar_values()

			# Configure and merge frames
			configured_frames = self.configure(frame, empty_frame, median_val, blur_val, thresh_val)
			merged = self.merge(configured_frames)

			# Reset video
			if r_val == 1:
				cap.set(1, 1)
				r_val = cv2.setTrackbarPos('Reset', 'Track', 0)

			# Display
			cv2.imshow('Track')

			# Pauses video after each frame, esc exits
			key = cv2.waitKey(0) & 0xFF
			if key == 27:
				break

	def get_trackbar_values(self):
		m_val = cv2.getTrackbarPos('Median', 'Track')
		b_val = cv2.getTrackbarPos('Blur', 'Track')
		t_val = cv2.getTrackbarPos('Thresh', 'Track')
		reset = cv2.getTrackbarPos('Reset', 'Track')

		return m_val, b_val, t_val, reset

	def set_trackbar_values(self, m_val, b_val, t_val):
		if b_val%2 == 0: 
			median_value = cv2.setTrackbarPos('Median', 'Track', m_val)
			blur_value = cv2.setTrackbarPos('Blur', 'Track', b_val)
			thresh_value = cv2.setTrackbarPos('Thresh', 'Track', t_val)
		else:
			median_value = cv2.setTrackbarPos('Median', 'Track', m_val)
			thresh_value = cv2.setTrackbarPos('Thresh', 'Track', t_val)
			print 'Error: Blur value must be an odd number.'

	def nothing(self, x):
		# Filler for trackbars
		pass

	def create_trackbars(self):
		self.trackbar_window = cv2.namedWindow("Track")
		cv2.createTrackbar('Median', 'Track', 0, 255, self.nothing)
		cv2.createTrackbar('Blur', 'Track', 1, 99, self.nothing)
		cv2.createTrackbar('Thresh', 'Track', 0, 255, self.nothing)
		cv2.createTrackbar('Save', 'Track', 0, 1, self.nothing)
		cv2.createTrackbar('Load', 'Track', 0, 1, self.nothing)
		cv2.createTrackbar('Reset', 'Track', 0, 1, self.nothing)

		self.default_values()

	def merge(self, frames):
		filler = frames['track'].copy()
		filler[:] = 155
		merged = np.vstack((frames['track'], filler, frames['bw'], filler, frames['final']))

		return merged
		
	def default_values(self):
		# Set default values
		median_value = cv2.setTrackbarPos('Median', 'Track', 100)
		blur_value = cv2.setTrackbarPos('Blur', 'Track', 1)
		thresh_value = cv2.setTrackbarPos('Thresh', 'Track', 25)

	def load_preset(self):
		# Open file to read from
		with open('presets.txt') as f:
			values = f.read().splitlines()

		self.set_trackbar_values(int(values[0]), int(values[1]), int(values[2]))
		
	def save_preset(self):
		median, blur, thresh, r = self.get_trackbar_values()
		
		# Open file and clear
		target = open('presets.txt', 'w')
		target.truncate()

		# Write to file
		target.write(str(median))
		target.write('\n')

		target.write(str(blur))
		target.write('\n')

		target.write(str(thresh))

		# Close File
		target.close()

	def preset_check(self):
		load = cv2.getTrackbarPos('Load', 'Track')
		save = cv2.getTrackbarPos('Save', 'Track')

		if load == 1:
			self.load_preset()
			load = cv2.setTrackbarPos('Load', 'Track', 0)

		if save == 1:
			self.save_preset()
			save = cv2.setTrackbarPos('Save', 'Track', 0)
			
	def configure(self, frame, empty, m_val, b_val, t_val):
		frame_delta = cv2.absdiff(empty, frame)					# Frame Delta
		gray = cv2.cvtColor(frame_delta, cv2.COLOR_BGR2GRAY)	# Grayscale
		track = gray.copy()[self.roi['top']:self.roi['bottom'], 
							self.roi['left']:self.roi['right']			# Grab track
		
		bw = np.asarray(track).copy() 							# Convert to array
		bw[bw < m_val] = 0										# White
		bw[bw >= m_val] = 255									# Black
		
		blur = cv2.GaussianBlur(bw, (b_val, b_val), 0)						# Blur
		thresh = cv2.threshold(blur, t_val, 255, cv2.THRESH_BINARY)[1] 		# Threshold
		
		kernel = np.ones((5, 5), np.uint8)									# Create Kernel
		dilation = cv2.dilate(thresh, kernel, iterations=1)
		erosion = cv2.erode(dilation, kernel, iterations=1)
		
		kernel = np.ones((11, 11), np.uint8)								# Create Kernel
		final = cv2.morphologyEx(erosion, cv2.MORPH_OPEN, kernel)			# Encloses shapes

		myDict = {'gray': gray, 'track': track, 'bw': bw, 'blur':blur, 'thresh': thresh, 'final':final}
		return myDict