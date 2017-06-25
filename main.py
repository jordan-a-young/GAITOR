from lib.ROIManager import ROIManager
from lib.Manager import Manager
from lib.Tracker import Tracker
from lib.Analyzer import Analyzer
import cv2

cap = cv2.VideoCapture('videos/VellumWalk0616_04.mp4')
frame = None

while True:
	ret, frame = cap.read()

	if not ret:
		print "video could not be loaded"
		break
	if frame.any():
		print "frame found"
		break

roiManager = ROIManager(frame)
roiManager.set_roi()

manager = Manager()
directory = manager.pick_folder()
print directory