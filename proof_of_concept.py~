"""
Proof of Concept
"""

import cv2
import numpy as np
from lib.trial_video import trial_video
from scipy.cluster.vq import kmeans, whiten,vq

# Define the codec and create VideoWriter object
fourcc = cv2.cv.CV_FOURCC(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 30.0, (720,480))

#we straigt bootstrappin now yo

#change these three lines accoding to the video you use
trial = trial_video("flipped3.mp4")
trial.set_horizon(255)
trial.set_thresh_vals(98.1, 98.7)


width = trial.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)

#color coding for feet
color_code = dict()
color_code['front'] = dict()
color_code['rear'] = dict()
color_code['front']['left'] = (255,0,255)
color_code['front']['right'] = (0,255,255)
color_code['rear']['left'] = (255,255,0)
color_code['rear']['right'] = (0,255,0)

while(1):

        feet_geom = None #foot geometry for this frame

        ret, bot, top = trial.read()

        if not ret:
                trial.release()
                break

        #find contours of top image (not mask)
        imgray = cv2.cvtColor(top,cv2.COLOR_BGR2GRAY)
        contours,hierarchy = cv2.findContours(imgray, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
                pass
        else:
            #get the largest one
            largest = contours[0]
            for c in contours:
                    if len(c) > len(largest):
                            largest = c
            cv2.drawContours(top, [largest], -1, (0,255,0), 3)

            #find rightmost and topmost point
            rightmost = tuple(largest[largest[:,:,0].argmax()][0])
            topmost = tuple(largest[largest[:,:,1].argmin()][0])

            #ignore everything behind the hunch more than half the
            #distance to the nose, marked here with red line
            dist = int((rightmost[0] - topmost[0]) / 3.5)

            bot_mask = trial.get_bottom_mask()
            
            #is this a valid trial?
            valid = rightmost[0] < width - 10               #rightmost point must be at least 10 px in
            valid = valid and topmost[0] - dist > 10        #so must rear limit
            valid = valid and bot_mask.any()                #the mask must have some points above threshold

            if not valid: #put an x in the top right corner
                    cv2.putText(top, "X", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255))
                    cv2.putText(bot, "X", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255))

            else:   #we have a good frame

                    #blue line, front of rat
                    cv2.line(top, (rightmost[0], 0), (rightmost[0], 100), (255,0,0))
                    #green line, huntch
                    cv2.line(top, (topmost[0], 0), (topmost[0], 100), (0,255,0))
                    #red line, for rear limit
                    cv2.line(top, (topmost[0] - dist, 0), (topmost[0] - dist, 100), (0,0,255))

                    #ignore detected values behind rear line
                    cv2.rectangle(bot_mask, (0,0), (topmost[0] - dist, 1000), 0, -1)

                    #blur, to merge adjsent toes and footpads
                    bot_mask = cv2.blur(bot_mask, (10,10))

                    #get centroids of all contours and cluster them
                    contours,hierarchy = cv2.findContours(bot_mask, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                    center = lambda box: (box[0] + box[2]/2, box[1]+ box[3]/2)
                    centers = [center(cv2.boundingRect(cnt)) for cnt in contours]

                    #identify feet positions
                    dstk = np.dstack(centers)[0]
                    rear = np.min(dstk[0])          #rearmost x value
                    front = np.max(dstk[0])         #frontmost x value
                    left = np.min(dstk[1])          #leftmost y
                    right = np.max(dstk[1])         #rightmost y

                    #feet geometry dictionary
                    #feet_geom['front']['left'] ext
                    feet_geom = dict()
                    feet_geom['front'] = dict()
                    feet_geom['rear'] = dict()

                    for c in centers:
                            #distance to frontmost
                            front_dist = front - c[0]
                            #distance to rearmost
                            rear_dist = c[0] - rear

                            #distance to leftmost
                            left_dist = c[1] - left
                            #distance to rightmost foot
                            right_dist = right - c[1]

                            #is it closer to the front or the back?
                            if front_dist <= rear_dist:
                                    x = 'front'
                            else:
                                    x = 'rear'

                            #is it closer to the left or the right?
                            if left_dist <= right_dist:
                                    y = 'left'
                            else:
                                    y = 'right'

                            #store point in dictionary
                            feet_geom[x][y] = c

            #draw the color coded feet if a dictionary exists
            if feet_geom:
                    for x in feet_geom:
                            for y in feet_geom[x]:
                                    color = color_code[x][y]
                                    point = feet_geom[x][y]
                                    cv2.circle(bot, point, 8, color, 3)
        h1, w1 = top.shape[:2]
        h2, w2 = bot.shape[:2]

        print h1 + h2, w1
        #create empty matrix
        vis = np.zeros((h1 + h2, w1,3), np.uint8)

        #combine 2 images
        vis[:h1, :w1,:3] = top
        vis[h1:h1 + h2, :w1,:3] = bot

        out.write(vis)
        cv2.imshow('', vis)
        if cv2.waitKey(0) & 0xFF == ord('q'):
                        break

trial.release()
out.release()
cv2.destroyAllWindows()
