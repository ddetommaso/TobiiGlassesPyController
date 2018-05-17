from tobiiglassesctrl import TobiiGlassesController

import cv2 as cv
import numpy as np

import sys
import time
import json



#tobiiglasses = TobiiGlassesController()
#address = "rtsp://" + tobiiglasses.address + ":8554/live/scene"
#print address

vcap = cv.VideoCapture("rtsp://192.168.71.50:8554/live/scene")



while(True):
	if vcap.isOpened() is True:
		ret, frame = vcap.read()
		cv.imshow('SCENE', frame)
	cv.waitKey(1)


