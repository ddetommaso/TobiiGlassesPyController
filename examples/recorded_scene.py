#from tobiiglassesctrl import TobiiGlassesController

import cv2 as cv
import numpy as np

#import sys
import time
import json

# function that searches for an eyetracker data element, return it and the corresponding ts 
def get_json_element(json_list, element):
	elem_list = []
	elem_ts_list = []
	for ii in range(0,len(json_list)):
		line = json_list[ii]
		
		if element in line:
			elem_list.append(line[element])
			elem_ts_list.append(line["ts"])

	return elem_list, elem_ts_list


# function that synchronize an eyetracker gp with its timestamps with the video one 
# all the data recorded between two frame are not kept 
def synchronize_gp_with_video(element, element_ts, video_ts, offset):
	gp_x = [0.0]		
	gp_y = [0.0]	

	for jj in range(1,len(video_ts)): 
		element_count = 0.0
		gp_x_buff = 0.0						
		gp_y_buff = 0.0	
		for ii in range(len(element_ts)):
			element_ts_offset = element_ts[ii] - offset
			
			if element_ts_offset > 0: 
				if element_ts_offset >= video_ts[jj-1] and element_ts_offset < video_ts[jj]:
					gp_x_buff += element[ii][0]				
					gp_y_buff += element[ii][1]	
					element_count +=1.0;

		if element_count != 0:
			gp_x.append(gp_x_buff/element_count)					
			gp_y.append(gp_y_buff/element_count)	
		else : 
			gp_x.append(0.0)					
			gp_y.append(0.0)
	return gp_x, gp_y



# get recorded video and eyetracking data 
vcap = cv.VideoCapture("recording_tests/Jairo_1/fullstream.mp4")
etfile = 'recording_tests/Jairo_1/livedata.json'
#save video output
out = cv.VideoWriter('output.avi', cv.cv.CV_FOURCC(*'MJPG'), 20.0, (int(vcap.get(3)),int(vcap.get(4))))

# loop to get timestamp from all frames
timestamps = [vcap.get(0)] #pts in ms of the video frames 
while(vcap.isOpened()):
    frame_exists, curr_frame = vcap.read()
    if frame_exists:
        timestamps.append(int(round(vcap.get(0)*1000))) # in microsecond to be consitent with et
    else:
        break
vcap.release()

# get eyetracker data from json file
data_et = []
with open(etfile) as f:
    for line in f:
        data_et.append(json.loads(line))
# get list of vts and gp and their corresponding ts from json data 
vts_list, vts_ts_list = get_json_element(data_et, "vts")
gp_list,  gp_ts_list  = get_json_element(data_et, "gp")


# Synchronisation of the video and gp timestamps
# video keyframe at vts = 0
gp_x, gp_y = synchronize_gp_with_video(gp_list, gp_ts_list, timestamps, vts_ts_list[0])

print "drawing video "
vcap2 = cv.VideoCapture("recording_tests/Jairo_1/fullstream.mp4")
while(True):
	if vcap2.isOpened() is True:
		ret, frame = vcap2.read()
		
		if ret:
			
			height, width = frame.shape[:2]
			timestamps_2 = int(round(vcap2.get(0)*1000))
			for ii in range(len(timestamps)): 
				if timestamps[ii] == timestamps_2: 
					cv.circle(frame,(int(gp_x[ii]*width),int(gp_y[ii]*height)), 10, (0,0,255), -1)
			out.write(frame)					
			cv.imshow('SCENE', frame)
	else:
		print "no video captured"
	cv.waitKey(1)

vcap2.release()
out.release()

