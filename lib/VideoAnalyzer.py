import cv2
from cv2.cv import CV_WINDOW_NORMAL
import numpy as np
import time
import os.path
import math
import csv
import random

BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLACK = (255, 255, 255)

"""
Object that runs and controls video analysis of given video.

This class is used to track the paw prints of the rat from
each video. It processes each frame, and marks the location
of each paw print. Currently this information is written to 
a csv for further analysis.
"""
class VideoAnalyzer():
	def __init__(self, filepath, should_rotate=False):
		# Opens video to retrieve first frame
		self.filepath = filepath
		self.should_rotate = should_rotate
		self.video = cv2.VideoCapture(self.filepath)
		ret, frame = self.video.read()

		if not ret:
			self.first_frame = None
			print 'Could not open video.'
		else:
			self.first_frame = frame

		# These will store the roi and rotation matrix set by the user.
		self.rot_matrix = None
		self.roi = None
	
	def get_ff(self):
		# Return first_frame
		return self.first_frame

	def set_rotation_matrix(self, matrix):
		# Sets rotation matrix
		self.rot_matrix = matrix

	def set_roi(self, roi):
		# Set internal roi
		self.roi = roi

	def analyze(self):
		start_time = time.time()

		# Create window
		win_name = os.path.split(self.filepath)[1]
		cv2.namedWindow(win_name, CV_WINDOW_NORMAL)
		cv2.namedWindow('Track', CV_WINDOW_NORMAL)
		
		# Stores unified contours, the frames they're from, centroid x + centroid y
		unified = [[],[],[],[]]
		
		# Stores the last frame accessed, so that it can be saved to an image.
		last_frame = None
		frame_numb = 1

		# Rotate and crop the first frame
		grayFF = cv2.cvtColor(self.first_frame, cv2.COLOR_BGR2GRAY)
		rows, cols = grayFF.shape
		
		if self.should_rotate:
			temp = cv2.warpAffine(grayFF, self.rot_matrix, (cols, rows))
			rotatedFF = temp[self.roi[1]:self.roi[3], self.roi[0]:self.roi[2]]
		else:
			rotatedFF = grayFF[self.roi[1]:self.roi[3], self.roi[0]:self.roi[2]]

		while True:
			while_start_time = time.time()

			# Save the firstframe after converting to grayscale
			ret, frame = self.video.read()

			# Break out of loop if vid is over
			if not ret:
				break
		
			if self.first_frame is None:
				self.first_frame = frame

			frame_numb += 1

			# Rotate if needed
			rotated = None
			if self.should_rotate:
				rotated = cv2.warpAffine(frame, self.rot_matrix, (cols, rows))
			else:
				rotated = frame
			
			# Crop, grayscale, background subtract
			gray = cv2.cvtColor(rotated.copy(), cv2.COLOR_BGR2GRAY)
			cropped = gray[self.roi[1]:self.roi[3], self.roi[0]:self.roi[2]]
			subtracted = cv2.absdiff(rotatedFF, cropped)

			# Blur and threshold
			b_val = 17
			t_val = 32
			blur = cv2.GaussianBlur(subtracted, (b_val, b_val), 0)
			thresh = cv2.threshold(blur, t_val, 255, cv2.THRESH_BINARY)[1]

			# Helps remove noise
			kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
			erosion = cv2.erode(thresh, kernel, iterations=1)
			dilation = cv2.dilate(thresh, kernel, iterations=1)
			
			kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
			final = cv2.morphologyEx(dilation, cv2.MORPH_OPEN, kernel)

			cv2.imshow('Track', thresh)
			
			# Do Canny edge detection and then find contours from those edges
			try:
				#edges = cv2.Canny(subtracted, 125, 255, True)
				#cv2.imshow('Edges', edges)
				contours, _ = cv2.findContours(final, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
				#cv2.drawContours(rotated, contours, -1, GREEN, 2, offset=(self.roi[0], self.roi[1]))
				print 'Contours: %d' % len(contours)

				time_manips = time.time()

				# This section of code combines nearby contours because toes were
				# often detected separately.
				# cloud tracks what 'cloud' the contour at the same index as the index
				# in cloud is. Each starts in their own cloud, if they are found to
				# be close with another contour they one is changed to have the
				# same cloud number as the leftmost one.
				cloud = np.linspace(1, len(contours), len(contours))
				if len(contours) > 0:
					for i, cnt1 in enumerate(contours):
						print 'Circumference: %d' % cv2.arcLength(cnt1, True)
						print 'Calculated area: %d' % (cv2.arcLength(cnt1, True)/(2*math.pi))**2
						print 'Contour area: %d' % cv2.contourArea(cnt1)
						x = i # Tracks index in the cloud array
						if i != len(contours) - 1:
							for cnt2 in contours[i + 1:]:
								x += 1
								# Don't compare if they're already the same
								if cloud[i] == cloud[x]:
									continue
								else:
									# !!!! Here is where it sets the max distance
									# contours can be apart and still be the same
									# paw - it's 25. And if any point on the two
									# is greater than 300 apart they're automatically
									# not the same. Of course this only applies to
									# two contours so if cnt1 is 15 away from cnt2
									# and 30 away from cnt3, but cnt3 is only 5
									# away from cnt2, they'll all be combined.
									close = self.find_if_close(cnt1, cnt2, 25, 100)
									if close:
										val2 = min(cloud[i], cloud[x])
										cloud[x] = cloud[i] = val2

					# Combine clouds to be the same contour
					cloud_numbers = np.unique(cloud)
					for i in cloud_numbers:
						pos = np.where(cloud == i)[0]
						
						if pos.size != 0:
							cont = np.vstack(contours[i] for i in pos)
							hull = cv2.convexHull(cont)
							#cv2.drawContours(rotated, [hull], 0, BLACK, 3,
											 #offset=(self.roi[0], self.roi[1]))

							# If the area is too small or two large, don't save them
							if (cv2.contourArea(hull) > 100 and cv2.contourArea(hull) < 1000):
								print 'Area of hull: %d' % cv2.contourArea(hull)
								# Add hull and frame_numb to unified
								unified[0].append(hull)
								unified[1].append(frame_numb)
								
								# Use moments to get center of contour
								M = cv2.moments(hull)
								unified[2].append(int(M['m10'] / M['m00']))
								unified[3].append(int(M['m01'] / M['m00']))

				time_combine = time.time()

				# Draw all accepted contours and their centroids
				if unified:
					if len(unified[0]) > 1:
						cv2.drawContours(rotated, unified[0], -1, BLACK, 2,
										 offset=(self.roi[0], self.roi[1]))
						
						for i in range(len(unified[0])):
							cv2.circle(rotated, (unified[2][i] + self.roi[0],
												 unified[3][i] + self.roi[1]),
												 5, RED)

				# Display frame, set last_frame to current
				cv2.imshow(win_name, rotated)
				last_frame = rotated

				# Calculate time
				time_draw = time.time()
				time_elapsed_ms = (time.time() - while_start_time) * 1000
				time_for_frame = int(1000/30 - time_elapsed_ms)
				
				if time_for_frame <= 1 or len(contours) == 0:
					time_for_frame = 2

			except:
				print "Something went wrong"

			# Set waitkey ie: q to quit
			#key = cv2.waitKey(int(time_for_frame))
			key = cv2.waitKey(1)
			if key == ord('q'):
				break

		print time.time() - start_time

		# Cleanup
		self.video.release()
		cv2.destroyAllWindows()
		
		# Process contours if we have more than one unified
		if unified:
			if len(unified[0]) > 1:
				print "Contours Sent for Processing Here."
				# self.process_contours(unified, last_frame, self.filepath, self.roi)

	"""
	Takes two contours for every x, y point in 1, and compares it to every
	point in 2.

	Inputs: 
		cnt1 and cnt2: two opencv contours to be compared
		close_dist: int that is the max cut off for being close
		far_dist: int that is the min cut off for being automatically considered far
	
	Output: boolean that's true if they are close, and false if not.
	"""
	def find_if_close(self, cnt1, cnt2, close_dist, far_dist):
		#start = time.time()
		row1, row2 = cnt1.shape[0], cnt2.shape[0]
		for i in xrange(row1):
			for j in xrange(row2):
				# Get pythagorean distance between two points
				dist = math.sqrt((cnt1[i][0][0] - cnt2[j][0][0])**2 +
								(cnt1[i][0][1] - cnt2[j][0][1])**2)
				if abs(dist) < close_dist:
					return True
				elif abs(dist) > far_dist:
					return False
		
		return False

	"""
	Takes unified contours, finds which are likely to be the same print and
	labels them with that print number. Stores them in the prints numpy
	structured array.
	"""
	def process_contours(self, cnts, last_frame, filename, roi):
		# Create array to store prints
		prints = np.array([(0, 0, 0, 0, 0)],
						  	dtype=[('centroidx', '>i4'), ('centroidy', '>i4'),
									("area",">i4"), ('frame','>i4'),
									('print_numb', '>i4')])

		# Identify areas that are likely to be the same print
		print_numb = 1
		for i in range(0, len(cnts[0])):
			this_print = None
			M = cv2.moments(cnts[0][i])

			# Check prev cnts to see if they belong to same foot
			if i != 0:
				frame_sep = 0
				j = 0
				
				# Go back until you find contours at different frames
				while frame_sep == 0 and j <= i:
					j += 1
					frame_sep = cnts[1][i] - cnts[1][i-j]

				# Only compare if they're separated by one frame
				while frame_sep == 1:
					dist = abs(math.hypot(cnts[2][i] - cnts[2][i-j],
										  cnts[3][i] - cnts[3][i-j]))
					if dist < 20:
						# Have to have +1 bc of the dumby row!
						this_print = prints['print_numb'][i-j+1];
						break
					
					# Check further down until frame_sep is too big
					j += 1
					frame_sep = cnts[1][i] - cnts[1][i-j]

			# If it doesn't match previous prints, give it a unique new name
			if this_print == None:
				this_print = print_numb
				print_numb += 1

			new = np.array([(cnts[2][i], cnts[3][i], M['m00'], cnts[1][i], this_print)],
							dtype=[('centroidx', '>i4'), ('centroidy', '>i4'),
									("area",">i4"), ('frame','>i4'),
									('print_numb', '>i4')])
			prints = np.vstack((prints, new))

		"""
		Then we go through and delete prints with only one representative, as they are likely
		not actually a true print. In the future maybe I can try to combine these with another print
		as this sometimes results from an intermediate frame where the contour was too small and was
		deleted.
		After doing this, draw the prints that have more than 1 representative
		EVENTUALLY: renumber prints so print numbering isn't so odd.
		"""
		maximum = int(prints['print_numb'].max())+1
		for i in xrange(maximum):
			# Generate a random color to draw with
			color = (random.randint(0, 255), random.randint(0, 255),
					 random.randint(0, 255))
			
			# Get all indices where the print_numb is i.
			pos = np.where(prints['print_numb'] == i)[0]

			# If it only occurs once, delete it
			if pos.size == 1:
				prints = np.delete(prints, pos[0], axis=0)

			if pos.size > 1:
				for z in pos:
					# Draw circle with the same area as the print, centered at the
					# centroid (plus the offset from the roi)
					cv2.circle(last_frame,
							   (prints['centroidx'][z] + roi[0],
								prints['centroidy'][z] + roi[1]),
							    int(math.sqrt(prints['area'][z]/3.14)), color)

		# Send it off for processing of each print as a whole
		self.write_file(prints, filename)
		self.advanced_processing(last_frame, prints, filename, roi)

	def write_file(self, prints, filename):
		# Delete dumby row and create filepath
		prints = np.delete(prints, 0, axis=0)
		newpath = self.make_file_path(filename, '.csv')

		# Open file to write to
		with open(newpath, 'wb') as f:
			writer = csv.writer(f)
			writer.writerow(['centroidx', 'centroidy', 'area', 'frame', 'print_numb'])
			
			for row in prints:
				writer.writerow([row['centroidx'][0], row['centroidy'][0],
								 row['area'][0], row['frame'][0], row['print_numb'][0]])

		print 'File written to: %s' % newpath

	"""
	This takes the full listing of things that were detected as prints and combines
	that data into more readable and shortened form - one line per print.
	"""
	def advanced_processing(self, last_frame, prints, filename, roi):
		# Check if processing is needed
		if prints.size == 0 or prints.size == 1:
			return

		"""
		col #0 = print #, col #1 = max area, col#2 = centroid of max area x,
		col#3 = centroid of max area y, col #4 first frame,
		col #5 last frame, #6 front/back, #7 left/right
		"""
		combo_prints = [[],[],[],[],[],[],[],[]]
		allNumbs = np.unique(prints['print_numb'])
		
		# Used to track if front paw
		currMinX = last_frame.shape[1]
		
		# Get the midline for right vs left based on the furthest separation
		maxY = prints['centroidy'].max()
		minY = prints['centroidy'].min()
		midline = (maxY-minY)/2 + minY

		# Go through and fill out the basic info
		for i in allNumbs:
			# Get full print
			pos = np.where(prints['print_numb'] == i)[0]
			allOfOnePrint = prints[pos]

			# Add print number and max area
			combo_prints[0].append(i)
			combo_prints[1].append(allOfOnePrint['area'].max())

			# Add centroid of max area for x and y
			indexMaxA = np.argmax(allOfOnePrint['area'], axis=0)
			combo_prints[2].append(allOfOnePrint['centroidx'][indexMaxA][0])
			combo_prints[3].append(allOfOnePrint['centroidy'][indexMaxA][0])

			# Add first frame and last frame
			combo_prints[4].append(allOfOnePrint['frame'].min())
			combo_prints[5].append(allOfOnePrint['frame'].max())

			# Check if its a front paw:
			if allOfOnePrint['centroidx'].min() < currMinX:
				currMinX = allOfOnePrint['centroidx'].min()
				combo_prints[6].append("f")
			else:
				combo_prints[6].append("b")

			# Check if right or left
			if allOfOnePrint['centroidy'].max() > midline:
				combo_prints[7].append("r")
			else:
				combo_prints[7].append("l")

		# Now we're going to check for double detection of the same pawprint.
		# !!! eventually maybe this should also re-add contours deleted for having
		# only a single instance, but that sounds real hard.
		for i in range(1, len(combo_prints[0])):
			for j in range(1, 3):
				if i-j < 0:
					continue
				
				if i >= len(combo_prints[6]):
					continue
				
				# If the one behind it is the same for front/back and left/right and
				# within three frames of each other
				if (combo_prints[6][i] == combo_prints[6][i-j] and
					combo_prints[7][i] == combo_prints[7][i-j] and
					(combo_prints[5][i-j]+4 > combo_prints[4][i] or
					combo_prints[5][i]+4 > combo_prints[4][i-j])):
					
					# And if they're within 3x the distance value for the initial check
					dist = abs(math.hypot(combo_prints[2][i] - combo_prints[2][i-j],
							   combo_prints[3][i] - combo_prints[3][i-j]))
					
					if dist < 60:
						# Combine them to the i row, setting centroid to the maxA
						if combo_prints[1][i-j] > combo_prints[1][i]:
							combo_prints[1][i] = combo_prints[1][i-j]
							combo_prints[2][i] = combo_prints[2][i-j]
							combo_prints[3][i] = combo_prints[3][i-j]
						
						combo_prints[4][i] = min(combo_prints[4][i-j],
												 combo_prints[4][i-j])
						
						combo_prints[5][i] = max(combo_prints[5][i-j],
												 combo_prints[5][i-j])

						# Delete using list comprehension and pop
						[col.pop(i-j) for col in combo_prints]

		# Create filepath for output
		newpath = self.make_file_path(filename, '.csv', 'analyzed')

		# Write to file
		with open(newpath, 'wb') as f:
			writer = csv.writer(f)
			
			# Write a header row for the csv
			writer.writerow(['print_numb', 'maxA', 'centroidx', 'centroidy',
							 'firstframe', 'lastframe', 'ForB', 'RorL'])
			
			for i in range(len(combo_prints[0])):
				# Eventually I should maybe do this in pandas so it isn't so
				# tediously specific, but for now this will work
				writer.writerow([combo_prints[0][i], combo_prints[1][i],
								 combo_prints[2][i][0], combo_prints[3][i][0],
								 combo_prints[4][i], combo_prints[5][i],
								 combo_prints[6][i], combo_prints[7][i]])
		
		print "File written to: %s" % newpath

		for i in range(0, len(combo_prints[0])):
			col = None
			if combo_prints[7][i] == 'r':
				if combo_prints[6][i] == 'f':
					col = (238, 238, 175)
				else:
					col = (255, 191, 0)
			else:
				if combo_prints[6][i] == 'f':
					col = (128, 128, 240)
				else:
					col = (0, 69, 255)

			# Draw circle for paw print
			cv2.circle(last_frame,
					   (combo_prints[2][i] + roi[0], combo_prints[3][i] + roi[1]),
					   int(math.sqrt(combo_prints[1][i]/3.14)), col,
					   thickness=3)

			# Write text to window
			cv2.putText(last_frame, str(combo_prints[0][i]),
						(combo_prints[2][i] + roi[0], combo_prints[3][i] + roi[1]),
						cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), thickness=2)

		# Create output for img and save
		imgpath = self.make_file_path(filename, '.png')
		cv2.imwrite(imgpath, last_frame)

	"""
	Uses string and path manipulations to create the output filenames for
	the different outputs of the program.

	Inputs: 
		inputfile: the full filepath of the video being analyzed
		filetype: the type of file being written
		add_text: any additional text, default = empty_string
	
	Output: a unique filepath for the output file to be written to.
	"""
	def make_file_path(self, input_file, file_type, add_text=''):
		# Add a space to additional text if it exists for formatting purposes
		if len(add_text) > 0:
			add_text = ' ' + add_text
		
		# Splits the filepath into directory + the files name
		splitpath = os.path.split(input_file)
		newpath = (splitpath[0] + '/' + splitpath[1].split('.')[0] +
				  ' automated scoring' + add_text + file_type)

		# If file already exists append numbers to its name until it doesn't exist
		counter = 1
		while os.path.exists(newpath):
			counter += 1
			newpath = (splitpath[0] + '/' + splitpath[1].split('.')[0] +
					  ' automated scoring' + add_text + ' (' + str(counter) + ')' +
					  file_type)

		return newpath


	"""
	Notes on labelling which paw a print is:
		First -- Group sets of paws: label with a unique id.
				 Do this by figuring out which ones
				 are within +/- lets say 30 of each other

		Next -- If no paw has been as far in the x as this one has,
				it's a front paw
				--> aka, if it's the minimum in the x direction of 0:i above it

		Next -- Take the y values, establish the middle of the two extremes
				(excluding outliers) and then divide up right and left based on that
	"""

