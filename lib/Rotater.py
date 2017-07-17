import cv2
from cv2.cv import CV_WINDOW_NORMAL
import numpy as np

BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

"""
Similar to ROIManager, but handles rotation instead. The user clicks at two
points along the line of the apparatus to establish what should become a
straight line. The left point must be designated using the left click button,
and the right one using the right button. The image is then rotated and
3 lines are displayed to allow the user to double check that the rotation
corrected properly.
"""
class Rotater():
	def __init__(self, background):
		self.orig_bg = background
		self.curr_bg = self.orig_bg.copy()
		self.pt_one = None
		self.pt_two = None
		self.matrix = None

	def rotate_image(self):
		# Create window and set mouse click
		cv2.namedWindow('Set Rotation', CV_WINDOW_NORMAL)
		cv2.setMouseCallback('Set Rotation', self.mouse_click)
		
		while True:
			# Display background
			cv2.imshow('Set Rotation', self.curr_bg)
			key = cv2.waitKey(1) & 0xFF

			# Reset if z is pressed
			if key == ord('z') or key == ord('Z'):
				self.curr_bg = self.orig_bg.copy()
				self.pt_one = None
				self.pt_two = None

			# Press n if finished
			elif key == ord('n') or key == ord('N'):
				if self.pt_one != None and self.pt_two != None:
					cv2.destroyAllWindows()
					break

		print 'rotation finished'
		return self.matrix

	def mouse_click(self, event, x, y, flags, param):
		# Set left point on left click
		if event == cv2.EVENT_LBUTTONDOWN:
			self.pt_one = (x,y)
			self.rotate()

		# Set right point on right click
		elif event == cv2.EVENT_RBUTTONDOWN:
			self.pt_two = (x,y)
			self.rotate()

	def rotate(self):
		# Check if both points are set
		if self.pt_one != None and self.pt_two != None:
			cv2.line(self.curr_bg, self.pt_one, self.pt_two, GREEN)

			# Calculate delta y and delta x
			deltay = (max(self.pt_one[1], self.pt_two[1]) - min(self.pt_one[1], self.pt_two[1]))
			deltax = (max(self.pt_one[0], self.pt_two[0]) - min(self.pt_one[0], self.pt_two[0]))
			
			# Calculate angle using arctan
			tanval = deltay/float(deltax)
			angle = math.degrees(np.arctan(tanval))
			print angle
			rows, cols = self.orig_bg.shape

			# If the left is higher than the right rotate ccw
			if self.pt_one[1] < self.pt_two[1]:
				self.matrix= cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
			else:
				self.matrix= cv2.getRotationMatrix2D((cols/2, rows/2), -angle, 1)
			
			# Set background to newly rotated image
			self.curr_bg = cv2.warpAffine(self.curr_bg, self.matrix, (cols, rows))

			# Draw lines to let users check rotation is sufficient
			cv2.line(self.curr_bg, (0, self.pt_one[1]), (cols, self.pt_one[1]), GREEN)
			cv2.line(self.curr_bg, (0, self.pt_two[1]), (cols, self.pt_two[1]), GREEN)
			cv2.line(self.curr_bg, (0, self.pt_one[1]+10), (cols, self.pt_one[1]+10), GREEN)
