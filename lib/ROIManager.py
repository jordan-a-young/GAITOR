import cv2
from cv2.cv import CV_WINDOW_NORMAL
import numpy as np

# Colors for drawing
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

"""
ROI (Region of interest) setup. Allows the user to select a rectangular area
for the analyzer to focus on.

This class is initialized with the first frame of the video. The user
then selects the region they wish to focus upon. This is done by clicking
the left mousebutton 4 times. The order used to select the region is
top, bottom, left, right. Once a region is selected the user can use
'd', to draw an outline of the region. 'z' is used to reset, and 'f'
when the user is satisfied with the region they have selected.
"""
class ROIManager():
	def __init__(self, frame):
		print 'ROIManager class initialized.'
		self.first_frame = frame
		self.frame_copy = self.first_frame.copy()
		self.left_clicks = 0

		# 0 = left, 1 = top, 2 = right, 3 = bottom
		self.roi = [0, 0, 0, 0]

	def get_roi(self):
		return self.roi

	def set_roi(self):
		# Create window and set mouse callback
		cv2.namedWindow('Set ROI', CV_WINDOW_NORMAL)
		cv2.setMouseCallback('Set ROI', self.mouse_click)

		while True:
			# Display frame
			img = cv2.imshow('Set ROI', self.frame_copy)
			key = cv2.waitKey(1) & 0xFF

			# If z is pressed, reset
			if key == ord('z') or key == ord('Z'):
				self.frame_copy = self.first_frame.copy()
				self.left_clicks = 0
				self.roi = [0, 0, 0, 0]
			
			# If n is pressed, user is finished
			elif key == ord('d') or key == ord('d'):
				if 0 not in self.roi:
					cv2.rectangle(self.frame_copy, (self.roi[0], self.roi[1]), 
								(self.roi[2], self.roi[3]), BLUE, thickness=3)

			elif key == ord('f') or key == ord('F'):
				cv2.destroyAllWindows()
				break

			elif key == 27:
				cv2.destroyAllWindows()
				return [0, 0, 0, 0]

		print "ROI selection finished"
		return self.roi

	def mouse_click(self, event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN and self.left_clicks == 0:
			print 'Top: %d' % y
			self.roi[1] = y
			self.left_clicks += 1
		
		elif event == cv2.EVENT_LBUTTONDOWN and self.left_clicks == 1:
			print 'Bottom: %d' % y 
			self.roi[3] = y
			self.left_clicks += 1
		
		elif event == cv2.EVENT_LBUTTONDOWN and self.left_clicks == 2:
			print 'Left: %d' % x
			self.roi[0] = x
			self.left_clicks += 1
		
		elif event == cv2.EVENT_LBUTTONDOWN and self.left_clicks == 3:
			print 'Right: %d' % x
			self.roi[2] = x
			self.left_clicks += 1


