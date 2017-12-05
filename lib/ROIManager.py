import cv2
from cv2.cv import CV_WINDOW_NORMAL
import numpy as np
import time

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
    def __init__(self, frame, StackedWidget):
        print 'ROIManager class initialized.'
        self.first_frame = frame
        self.frame_copy = self.first_frame.copy()
        self.left_clicks = 0
        self.StackedWidget = StackedWidget
        # 0 = left, 1 = top, 2 = right, 3 = bottom
        self.roi = [0, 0, 0, 0]

        # self.t1 = Thread(target=self.countdown1)
        # self.t1.start()

    def get_roi(self):
        return self.roi

    def set_roi(self):
        # Create window and set mouse callback
        cv2.namedWindow('Set ROI', CV_WINDOW_NORMAL)
        cv2.setMouseCallback('Set ROI', self.mouse_click)
        
        # Display frame for choosing ROI. Lasts until key pressed.
        img = cv2.imshow('Set ROI', self.frame_copy)
        key = cv2.waitKey(0)
        cv2.destroyAllWindows()

        if 0 in self.roi:
            self.resetROI()
        else:
            self.StackedWidget.setCurrentIndex(3)
            # Display frame showing chosen ROI. Lasts until key pressed.
            cv2.namedWindow('Show ROI', CV_WINDOW_NORMAL)
            cv2.rectangle(self.frame_copy, (self.roi[0], self.roi[1]), 
                    (self.roi[2], self.roi[3]), BLUE, thickness=3)
            img2 = cv2.imshow('Show ROI', self.frame_copy)
            self.StackedWidget.resetButton.clicked.connect(lambda: self.resetROI())
            key2 = cv2.waitKey(0)
            cv2.destroyAllWindows()
            self.StackedWidget.setCurrentIndex(4)

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

    def resetROI(self):
        cv2.destroyAllWindows()
        self.frame_copy = self.first_frame.copy()
        self.left_clicks = 0
        self.roi = [0, 0, 0, 0]
        self.StackedWidget.setCurrentIndex(2)
        self.set_roi()