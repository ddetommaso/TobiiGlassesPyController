# live_scene_and_gaze.py : A demo for video streaming and synchronized gaze
#
# Copyright (C) 2021  Davide De Tommaso
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import av
import cv2
import numpy as np
from tobiiglassesctrl import TobiiGlassesController

import queue
import threading
from ultralytics import YOLO


def frame_grabber(container, stream, frame_queue):
    """
    Grabs video frames from a stream and puts them into a queue.

    Parameters:
    - container: av.container.InputContainer, the container for the video stream.
    - stream: av.video.stream.VideoStream, the video stream from which frames are grabbed.
    - frame_queue: queue.Queue, the queue to hold the frames.
    """
    for frame in container.decode(stream):
        if not frame_queue.empty():
            try:
                frame_queue.get_nowait()  # Discard the previous frame if it's still in the queue
            except queue.Empty:
                pass
        frame_queue.put(frame)

def draw_label(frame, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, font_color=(0, 255, 0), font_thickness=2):
    """
    Draws a label on the video frame.

    Parameters:
    - frame: numpy array, video frame.
    - text: str, text to display.
    - pos: tuple, position (x, y) for the label.
    - font: cv2.FONT, font type (optional).
    - font_scale: float, font size (optional).
    - font_color: tuple, font color (optional).
    - font_thickness: int, font thickness (optional).
    """
    cv2.putText(frame, text, pos, font, font_scale, font_color, font_thickness)


def apply_bounding_boxes_YOLOv8(frame, gaze_pos, alpha, detections, classes, confidence_threshold=0.5):
    """
    Draw all the bounding boxes detected by YOLOv8 in red and the one corresponding to the gaze in green.

    Parameters:
    - frame: numpy array, video frame.
    - gaze_position: tuple, gaze position (gaze_x, gaze_y).
    - alpha: float, bounding boxes transparency (0.0 to 1.0).
    - detections: dict, it contains bounding boxes, class_ids and confidences for each bounding box.
    - classes: list, list of class names.
    - confidence_threshold: float, minimum confidence to accept a bounding box.

    Return:
    - frame: numpy array, frame with bounding boxes applied.
    """
    gaze_x, gaze_y = gaze_pos
    mask = frame.copy()
    max_confidence = 0
    best_box = None
    best_class_id = None
    best_confidence = None
    red_color = (0, 0, 255)
    green_color = (0, 255, 0)

    # Draw all detections in red and find the best detection for the gaze
    for detection in detections:
        cords = detection.xyxy[0].tolist()
        cords = [round(x) for x in cords]
        confidence = detection.conf[0].item()
        class_id = int(detection.cls[0].item())
        label = f'{classes[class_id]} ({confidence:.2f})'
        
        # Draw all the bounding boxes in red
        cv2.rectangle(mask, (cords[0], cords[1]), (cords[2], cords[3]), red_color, 2)
        draw_label(frame, label, (cords[0], cords[1] - 10), font_color=red_color)
        
        # Check if gaze is within the bounding box
        if cords[0] < gaze_x < cords[2] and cords[1] < gaze_y < cords[3] and confidence > max_confidence:
            max_confidence = confidence
            best_box = (cords[0], cords[1], cords[2], cords[3])
            best_class_id = class_id
            best_confidence = confidence

    # If there is a bounding box containing the gaze with greater confidence, paint it in green
    if best_box and max_confidence >= confidence_threshold:
        x, y, x_end, y_end = best_box
        cv2.rectangle(mask, (x, y), (x_end, y_end), green_color, 4)
        label = f'{classes[best_class_id]} ({best_confidence:.2f})'
        draw_label(frame, label, (x, y - 10), font_color=green_color)

    cv2.addWeighted(mask, alpha, frame, 1 - alpha, 0, frame)
    return frame

ipv4_address = "192.168.100.10"

# Variables used for extra processing (using YOLOv8)
model = YOLO("yolov8s.pt")
classes = model.names
alpha = 0.4  # Mask transparency
confidence_threshold = 0.3  # Minimum confidence for bounding boxes

tobiiglasses = TobiiGlassesController(ipv4_address)
video = av.open("rtsp://%s:8554/live/scene" % ipv4_address, "r")

tobiiglasses.start_streaming()

"""
# Discomment this block for using structure without queues
try:
    for packet in video.demux():
        for frame in packet.decode():
            if isinstance(frame,av.video.frame.VideoFrame):
                #print(frame.pts)
                img = frame.to_ndarray(format='bgr24')
                height, width = img.shape[:2]
                data_gp  = tobiiglasses.get_data()['gp']
                if data_gp['ts'] > 0:
                    cv2.circle(img,(int(data_gp['gp'][0]*width),int(data_gp['gp'][1]*height)), 60, (0,0,255), 6)
                    
                    # Extra processing here

                    # Detect objets using YOLOv8
                    results = model(img)
                    detections = results[0].boxes
                    img = apply_bounding_boxes_YOLOv8(img, (int(data_gp['gp'][0]*width),int(data_gp['gp'][1]*height)), alpha, detections, classes, confidence_threshold)

                    # End of extra processing

                cv2.imshow('Tobii Pro Glasses 2 - Live Scene',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    pass
"""

# Comment this block for using structure without queues
frame_queue = queue.Queue(maxsize=1)
stream = video.streams.video[0]
thread = threading.Thread(target=frame_grabber, args=(video, stream, frame_queue))
thread.start()
try:
    while True:
        try:
            frame = frame_queue.get(timeout=1)  # Wait for the next frame
        except queue.Empty:
            continue
        if isinstance(frame,av.video.frame.VideoFrame):
            #print(frame.pts)
            img = frame.to_ndarray(format='bgr24')
            height, width = img.shape[:2]
            data_gp  = tobiiglasses.get_data()['gp']
            if data_gp['ts'] > 0:
                cv2.circle(img,(int(data_gp['gp'][0]*width),int(data_gp['gp'][1]*height)), 60, (0,0,255), 6)

                # Extra processing here

                # Detect objets using YOLOv8
                results = model(img)
                detections = results[0].boxes
                img = apply_bounding_boxes_YOLOv8(img, (int(data_gp['gp'][0]*width),int(data_gp['gp'][1]*height)), alpha, detections, classes, confidence_threshold)

                # End of extra processing

            cv2.imshow('Tobii Pro Glasses 2 - Live Scene',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    pass


cv2.destroyAllWindows()

tobiiglasses.stop_streaming()
tobiiglasses.close()
