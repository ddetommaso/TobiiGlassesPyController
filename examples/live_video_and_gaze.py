from tobiiglassesctrlupdate import TobiiGlassesController

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
#out = cv.VideoWriter('output.avi', fourcc, 20.0, (int(vcap.get(3)),int(vcap.get(4))))

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
		
				print data_gp
				if gp_ts < data_gp['ts']:
					gp_ts = data_gp['ts']
					gp_x = data_gp['gp'][0]
					gp_y = data_gp['gp'][1]
			
					cv.circle(frame,(int(gp_x*width),int(gp_y*height)), 10, (0,0,255), -1)
			
				#out.write(frame)
				cv.imshow('SCENE', frame)
				
		cv.waitKey(1)
except KeyboardInterrupt:
    print('interrupted!')

tobiiglasses.stop_streaming()
vcap.release()
#out.release()

