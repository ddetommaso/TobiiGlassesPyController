## the computational in this script are made in seconds (s) since
## pyav provides us the time of the frame in second

## press q when yuo want stop the script (be aware to be on the window showing the live video)

import time 
import av
import cv2
import threading
from tobiiglassesctrl import TobiiGlassesController
from queue import Queue
import csv
import sys

class BufferSynch:
    def __init__(self, size):
        self.GP = Queue(size)
        self.FrameTS = 0
        self.FramePTS = 0   # for plotting data
        self.GPts = 0       # for plotting data
        self.GPused = 0     # for plotting data
        self.PTSts = 0      # for plotting data
        self.PTSpts = 0     # for plotting data
        self.OffsetTS = 0
        self.OffsetFRAME = 0 #offset between package pts and frame pts
        self.running = True

## THREADS ##

def read_data(tobiiglasses, buffer, kind, tout):
    print("thread %s started" % (kind))
    old_ts = 0
    while buffer.running:
        data = tobiiglasses.get_data()[kind]
        # continue only if the data is updated
        if (kind in data) and (old_ts < data['ts']) :
            if kind == 'pts':
                if not buffer.OffsetFRAME:
                    buffer.OffsetFRAME = buffer.FrameTS - data['pts']/90000
                buffer.OffsetTS = data['ts']/1000000 - data['pts']/90000
                #buffer.PTSts = data['ts']      # for plotting data
                #buffer.PTSpts = data['pts']    # for plotting data
            elif kind == 'gp':
                # save gaze data into a buffer without the offset
                data_no = {'ts': data['ts']/1000000 - buffer.OffsetTS, 'gp': data['gp']}
                buffer.GP.put(data_no)
                #buffer.GPts = data['ts']       # for plotting data
            old_ts = data['ts']
        time.sleep(tout)


def show_video(video, buffer):
    print("thread video started")
    for packet in video.demux():
        for frame in packet.decode():
            if isinstance(frame, av.video.frame.VideoFrame):
                buffer.FrameTS = frame.time
                # buffer.FramePTS = frame.pts           # for plotting data
                img = frame.to_ndarray(format='bgr24')
                height, width = img.shape[:2]
                data_gp = synch_data_video(buffer) 
                if data_gp:
                    cv2.circle(img,(int(data_gp['gp'][0]*width),int(data_gp['gp'][1]*height)), 60, (0,0,255), 6)
                cv2.imshow('Tobii Pro Glasses 2 - Live Scene',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            buffer.running = False
            cv2.destroyAllWindows()
            break

def plot_data(buffer, tout, t0):
    print("thread saving data started")
    while buffer.running:
        t = time.time() - t0
        print("time: ", round(t,3),"    frame pts: ", buffer.FramePTS, "          frame ts: ", round(buffer.FrameTS,5), "        pts: ", buffer.PTSpts, "           pts ts: ", buffer.PTSts, "          gp ts: ", buffer.GPts, "            gp used: ", buffer.GPused)
        time.sleep(tout)


## FUNCTION ##

# synchronization data and video
def synch_data_video(buffer):
    nextData = []
    if buffer.GP.empty():
        print("not gp data available")
    else:
        firstData = buffer.GP.get()
        timeData = firstData['ts']
        # check gaze data time to synch with frame time
        if timeData < (buffer.FrameTS - buffer.OffsetFRAME):
            # flush data into buffer
            while timeData <= (buffer.FrameTS - buffer.OffsetFRAME) and not buffer.GP.empty():
                nextData = buffer.GP.get()
                timeData = nextData['ts']
        else:
            nextData = buffer.GP.get()
        #if nextData:                           # for plotting data
        #    buffer.GPused = nextData['ts']     # for plotting data
        return nextData


def main ():

    ## DEFINE ##
    ipv4_address = "192.168.100.10"
    #ipv4_address = "192.168.71.50"     # with WiFi
    video = av.open("rtsp://%s:8554/live/scene" % ipv4_address, "r")
    timeout = 0.01
    t0 = time.time()

    ## INIZIALIZE ##
    tobiiglasses = TobiiGlassesController(ipv4_address, video_scene=True)
    buffer = BufferSynch(0)

    ## STARTING PROCESSES ##
    # Starting comunication with tobiiglasses
    tobiiglasses.start_streaming()
    # stop if it was recording
    if tobiiglasses.is_recording():
    	rec_id = tobiiglasses.get_current_recording_id()
    	tobiiglasses.stop_recording(rec_id)
    # Reading gaze data 
    gp = threading.Timer(0, read_data, [tobiiglasses, buffer, 'gp', timeout])
    gp.start()
    # Reading pts synch data
    pts = threading.Timer(0, read_data, [tobiiglasses, buffer, 'pts', timeout])
    pts.start()
    # Show Video
    sv = threading.Timer(0, show_video, [video, buffer])
    sv.start()
    # Plot data
    #pd = threading.Timer(0, plot_data, [buffer, timeout, t0])
    #pd.start()

    # Wait for process to end
    gp.join()
    pts.join()
    sv.join()
    #pd.join()

    # Ending comunication with tobiiglasses
    tobiiglasses.stop_streaming()
    tobiiglasses.close()

if __name__ == '__main__':
    main()