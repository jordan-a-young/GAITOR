import cv2
from cv2.cv import CV_WINDOW_NORMAL
import numpy as np
import math

BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

"""
My roi set up. It allows you to choose two points which serve as the bottom and
top of the roi rectangle.

Takes in background which is the the first frame of a video in its constructor.
Opencv drawing permanently alters the image, so it displays a copy of that, curr_bg.
When set_roi is called, it is displayed. The user clicking left sets the top of
the roi, which has its length preset to be the length of the video minus ten
pixels on each side to account for rotation chopping off some edges. Right
clicks set the bottom of the roi. If there has been both a right and a left click,
the roi is drawn as a rectangle on the image. It is automatically updated by
the continuous while loop. If the user presses z, the top and bottom of the roi
are reset and the image returns to the original one. Pressing n finalizes the
roi and breaks out of the while loop, ending the set up. The roi is returned by
set_roi as a list of four points.
"""
class RoiChooser():
	def __init__(self, background):
		self.orig_bg = background
		self.curr_bg = self.orig_bg.copy()
		self.top = None
		self.bottom = None

	def set_roi(self):
		# Create window and set mouse function
		roi = None
		cv2.namedWindow('Set ROI', CV_WINDOW_NORMAL)
		cv2.setMouseCallback('Set ROI', self.mouse_click)
		
		while True:
			# Display image
			cv2.imshow('Set ROI', self.curr_bg)
			key = cv2.waitKey(1) & 0xFF

			# If z is pressed, reset
			if key == ord('z') or key == ord('Z'):
				self.curr_bg = self.orig_bg.copy()
				self.top = None
				self.bottom = None

			# If n is pressed, user is finished selecting roi
			elif key == ord('n') or key == ord('N'):
				if self.top != None and self.bottom != None:
					roi = [10, self.top, self.orig_bg.shape[1]-10, self.bottom]
					cv2.destroyAllWindows()
					break

		print "roi finished"
		return roi

	def mouse_click(self, event, x, y, flags, param):
		# Set top bounds on left mouseclick
		if event == cv2.EVENT_LBUTTONDOWN:
			print y
			self.top = y
			
			# If both points have been set, draw rectangle
			if self.top != None and self.bottom != None:
				cv2.rectangle(self.curr_bg, (0, self.top),
							  (self.orig_bg.shape[1], self.bottom),
							  BLUE, thickness=2)
		
		# Set bottom bounds on right mouseclick
		elif event == cv2.EVENT_RBUTTONDOWN:
			print y
			self.bottom = y

			# If both points have been set, draw rectangle
			if self.top != None and self.bottom != None:
				cv2.rectangle(self.curr_bg, (0, self.top),
							  (self.orig_bg.shape[1], self.bottom),
							  BLUE, thickness=2)
