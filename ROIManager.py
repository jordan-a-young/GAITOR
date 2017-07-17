import cv2
from cv2.cv import CV_WINDOW_NORMAL
import numpy as np

# Colors for drawing
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

"""
ROI setup. User clicks 4 times to select the boundary of the ROI.
Takes in the first frame of a video in its constructor.
Opencv drawing permanently alters the image, it displays a copy of that, curr_bg.
When set_roi is called, it is displayed. The user clicking left sets the top and bottom 
of the roi. Right clicks set the left and right of the roi. If all of the points are set,
the roi is drawn as a rectangle on the image. It is automatically updated by
the continuous while loop. If the user presses z, the values and image are reset and the image
returns to the original one. Pressing d draws the roi. Esc breaks out of the while loop,
ending the set up. The roi is returned by set_roi as a list of four points.
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
			cv2.imshow('Set ROI', self.frame_copy)
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


