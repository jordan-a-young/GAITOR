import cv2

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
		self.first_frame = frame
		self.frame_copy = self.first_frame.copy()
		self.roi = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
		self.left_clicks = 0

	def get_roi(self):
		return self.roi

	"""
	Purpose: Displays the first frame of the video and automatically updates it via a while loop
	that is only broken out of when the user presses n to update. Sets mouse
	clicks to call the mouse_click method. Pressing z resets instance variables
	to their inital values.
	Output: A list of the form [left x, top y, right x, bottom y]
	"""
	def set_roi(self):
		cv2.namedWindow('Set ROI')
		cv2.setMouseCallback('Set ROI', self.mouse_click)

		while True:
			cv2.imshow('Set ROI', self.frame_copy)
			key = cv2.waitKey(1) & 0xFF

			if key == ord('z') or key == ord('Z'):
				self.frame_copy = self.first_frame.copy()
				self.left_clicks = 0
				self.roi.update({'left': 0, 'right': 0, 'top': 0, 'bottom': 0})
			
			elif key == ord('d') or key == ord('D'):
				if 0 not in self.roi:
					cv2.rectangle(self.frame_copy, (self.roi['left'], self.roi['top']), 
								(self.roi['right'], self.roi['bottom']), (0,0,255), thickness=3)

			elif key == 27:
				cv2.destroyAllWindows()
				break

		print "ROI selection finished"
		return self.roi

	"""
	Purpose: Responds to user clicks by setting the bounds of the roi. 
	"""
	def mouse_click(self, event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN and self.left_clicks == 0:
			print 'Top: %d' % y
			self.roi['top'] = y
			self.left_clicks += 1
		
		elif event == cv2.EVENT_LBUTTONDOWN and self.left_clicks == 1:
			print 'Bottom: %d' % y 
			self.roi['bottom'] = y
			self.left_clicks += 1
		
		elif event == cv2.EVENT_LBUTTONDOWN and self.left_clicks == 2:
			print 'Left: %d' % x
			self.roi['left'] = x
			self.left_clicks += 1
		
		elif event == cv2.EVENT_LBUTTONDOWN and self.left_clicks == 3:
			print 'Right: %d' % x
			self.roi['right'] = x
			self.left_clicks += 1


