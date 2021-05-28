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

ipv4_address = "192.168.100.10"

tobiiglasses = TobiiGlassesController(ipv4_address)
video = av.open("rtsp://%s:8554/live/scene" % ipv4_address, "r")

tobiiglasses.start_streaming()

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
                cv2.imshow('Tobii Pro Glasses 2 - Live Scene',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    pass
cv2.destroyAllWindows()

tobiiglasses.stop_streaming()
tobiiglasses.close()
