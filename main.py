from lib.ROIManager import ROIManager
from lib.Manager import Manager
from lib.Tracker import Tracker
from lib.Analyzer import Analyzer
import cv2

cap = cv2.VideoCapture('videos/VellumWalk0616_04.mp4')
ret, frame = cap.read()

roiManager = ROIManager(frame)
