#from tobiiglassesctrl import TobiiGlassesController

import cv2 as cv
import numpy as np
import caffe
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

def detection(image, net, CLASSES, COLORS): 
    """    
    net.blobs['data'].reshape(50,        # batch size
                          3,         # 3-channel (BGR) images
                          227, 227)  # image size is 227x227
    #image = caffe.io.load_image(caffe_root + 'examples/images/cat.jpg')
    transformed_image = transformer.preprocess('data', image)
    #plt.imshow(image)
    # copy the image data into the memory allocated for the net
    net.blobs['data'].data[...] = transformed_image

    # perform classification
    output = net.forward()

    output_prob = output['prob'][0]  # the output probability vector for the first image in the batch

    print 'predicted class is:', output_prob #.argmax()

    """

    blob = cv.dnn.blobFromImage(image, 1.0, (227, 227))

    net.setInput(blob)
    detections = net.forward()    

    print len(detections[0])
    """
    
    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]
     
        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > args["confidence"]:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
     
            # display the prediction
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            print("[INFO] {}".format(label))
            cv2.rectangle(image, (startX, startY), (endX, endY),
                COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv.putText(image, label, (startX, y),
                cv.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
    """

# get recorded video and eyetracking data 
vcap = cv.VideoCapture("recording_tests/Jairo_2/fullstream.mp4")
etfile = 'recording_tests/Jairo_2/livedata.json'
#save video output
out = cv.VideoWriter('output.avi', cv.VideoWriter_fourcc(*'MJPG'), 20.0, (int(vcap.get(3)),int(vcap.get(4))))

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

# get classifier model trained with Caffe
print "loading model"
model_def = 'prototxt_files/deploy.prototxt'
model_weights = 'prototxt_files/caffenet_train/solver_iter_10.caffemodel'
# classes to detect
CLASSES = ["iCub_face", "bottle"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3)) 
# loading model
net = cv.dnn.readNetFromCaffe(model_def, model_weights)
"""
caffe.set_mode_cpu()

net = caffe.Net(model_def,      # defines the structure of the model
                model_weights,  # contains the trained weights
                caffe.TEST)     # use test mode (e.g., don't perform dropout)

blob = caffe.proto.caffe_pb2.BlobProto()
pbfile = open( 'prototxt_files/database_mean.binaryproto' , 'rb' ).read()
blob.ParseFromString(pbfile)
arr = np.array( caffe.io.blobproto_to_array(blob) )
pbout = arr[0]
np.save( 'prototxt_files/database_mean.npy' , pbout )
mu = np.load('prototxt_files/database_mean.npy')
mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values

transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))  # move image channels to outermost dimension
transformer.set_mean('data', mu)            # subtract the dataset-mean value in each channel
transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
transformer.set_channel_swap('data', (2,1,0))  # swap channels from RGB to BGR
"""

# Synchronisation of the video and gp timestamps
# video keyframe at vts = 0
gp_x, gp_y = synchronize_gp_with_video(gp_list, gp_ts_list, timestamps, vts_ts_list[0])

print "drawing video "
vcap2 = cv.VideoCapture("recording_tests/Jairo_2/fullstream.mp4")
while(True):
    if vcap2.isOpened() is True:
        ret, frame = vcap2.read()
        
        if ret:
            
            height, width = frame.shape[:2]
            timestamps_2 = int(round(vcap2.get(0)*1000))
            for ii in range(len(timestamps)): 
                if timestamps[ii] == timestamps_2: 
                    cv.circle(frame,(int(gp_x[ii]*width),int(gp_y[ii]*height)), 10, (0,0,255), -1)
            
            # object detection            
            detection(frame, net, CLASSES, COLORS)
            
            #out.write(frame)                    
            #cv.imshow('SCENE', frame)
    else:
        print "no video captured"
    cv.waitKey(1)

vcap2.release()
out.release()

