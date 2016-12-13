import numpy as np
import cv2

def unit_vector(vec):
	print 'Currently performing: Arch unit_vector'
	# return the unit vector for a vector
	return vec / np.linalg.norm(vec)

def angle_between(front, hunch, rear):
	'''
	return the angel between the front
	back and rear of the rat
	'''
	print 'Currently performing: Arch angle_between'
	f = np.array(front)
	h = np.array(hunch)
	r = np.array(rear)

	v1 = np.array(f-h)
	v2 = np.array(h-r)

	v1_u = unit_vector(v1)
	v2_u = unit_vector(v2)

	angle = np.arccos(np.dot(v1_u,v2_u))

	if np.isnan(angle):
		if (v1_u == v2_u).all():
			return 0.0
		else:
			return np.pi
	return angle

def isolate_back(rear, feet, mask):
	'''
	given a front, rear, feet position and a top mask (rat profile)
	returns the isolated points along the curve of the rats back
	returns null if there is no data
	'''
	print 'Currently performing: Arch isolate_back'
	copy = mask.copy()

	if not rear:
		return

	try:
		# bound with rectangles
		cv2.rectangle(copy, feet, rear, 255, -1)

		# arch = edge
		cnts,h = cv2.findContours(copy,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

		cnts = sorted(cnts,key=cv2.contourArea,reverse=True)[:2]
		arch = cnts[0]
		
		for c in cnts:
			a = cv2.contourArea(c)
			a2 = cv2.contourArea(arch)

			if a < a2:
				arch = c
		return arch

	except:
		print 'couldnt create contour'

	return np.array([np.nan])

def get_arch_data(frame, mask):
	'''
	returns the angel of the arch of the back of the rat detected,
	given a frame object and a top mask, returns null if there is
	no data
	'''
	print 'Currently performing: Arch get_arch_data'
	try:
		# get front and rear
		rear = (frame.critical_points[0][0],frame.critical_points[1][0])
		feet = (frame.critical_points[0][2],frame.critical_points[1][2])
		hunch = (frame.critical_points[0][1],frame.critical_points[1][1])
		mid = (frame.critical_points[0][3],frame.critical_points[1][3])
	
	except Exception,e:
		print 'could not get crit values: ' + str(e)
		rear = (0,0)
		feet = (0,0)
		hunch = (1920/2,0)
		mid = hunch

	angle = angle_between(mid,hunch,rear)
	arch = isolate_back(rear,feet,mask)

	return angle,arch