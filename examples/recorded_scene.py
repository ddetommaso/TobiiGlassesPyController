#from tobiiglassesctrl import TobiiGlassesController

import cv2 as cv
#import numpy as np

#import sys
import time
import json

# get recorded video 
vcap = cv.VideoCapture("test_recording/fullstream.mp4")
etfile = 'test_recording/livedata.json'

timestamps = [vcap.get(cv.CAP_PROP_POS_MSEC)]
calc_timestamps = [0.0]

while(vcap.isOpened()):
    frame_exists, curr_frame = vcap.read()
    if frame_exists:
        timestamps.append(vcap.get(cv.CAP_PROP_POS_MSEC))
    else:
        break

vcap.release()

print timestamps

"""
# get eyetracker data from json file
data = []
with open(etfile) as f:
    for line in f:
        data.append(json.loads(line))

"""
		
		
"""
while(True):
	if vcap.isOpened() is True:
		ret, frame = vcap.read()
		cv.imshow('SCENE', frame)
	else:
		print "no video captured"
	cv.waitKey(1)
"""

