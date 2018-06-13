from tobiiglassesctrl import TobiiGlassesController

import cv2 as cv
import numpy as np

import sys
import time
import json


address = "192.168.71.50"
tobiiglasses = TobiiGlassesController(address)

# getting livestream video with opencv
address_rtsp = "rtsp://" + address + ":8554/live/scene"
vcap = cv.VideoCapture(address_rtsp)

#save video output
out = cv.VideoWriter('output.avi', cv.cv.CV_FOURCC(*'MJPG'), 20.0, (int(vcap.get(3)),int(vcap.get(4))))

# calibration 
if tobiiglasses.is_recording():
	rec_id = tobiiglasses.get_current_recording_id()
	tobiiglasses.stop_recording(rec_id)

project_name = raw_input("Please insert the project's name: ")
project_id = tobiiglasses.create_project(project_name)

participant_name = raw_input("Please insert the participant's name: ")
participant_id = tobiiglasses.create_participant(project_id, participant_name)

calibration_id = tobiiglasses.create_calibration(project_id, participant_id)
raw_input("Put the calibration marker in front of the user, then press enter to calibrate")
tobiiglasses.start_calibration(calibration_id)

res = tobiiglasses.wait_until_calibration_is_done(calibration_id)

if res is False:
	print("Calibration failed!")
	exit(1)

# starting the data streaming 
tobiiglasses.start_streaming()



# loop grabbing the video and the data 
gp_ts = 0
try : 
	while True:
		if vcap.isOpened() is True:
			ret, frame = vcap.read()
			if ret :
			
				height, width = frame.shape[:2]			
				cv_ts = int(round(vcap.get(0)*1000))

				data_gp  = tobiiglasses.get_data()['gp']
				data_pts = tobiiglasses.get_data()['pts']	
		
				if gp_ts < data_gp['ts']:
					gp_ts = data_gp['ts']
					gp_x = data_gp['gp'][0]
					gp_y = data_gp['gp'][1]
			
					cv.circle(frame,(int(gp_x*width),int(gp_y*height)), 10, (0,0,255), -1)
			
				out.write(frame)
				#cv.imshow('SCENE', frame)
				
		cv.waitKey(1)
except KeyboardInterrupt:
    print('interrupted!')

tobiiglasses.stop_streaming()
vcap.release()
out.release()

