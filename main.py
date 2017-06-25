from lib.ROIManager import ROIManager
from lib.Manager import Manager
from lib.Tracker import Tracker
from lib.Analyzer import Analyzer
import cv2

manager = Manager()
file = manager.select_video()
print "File chosen: %s" % file

cap = cv2.VideoCapture(file)
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
