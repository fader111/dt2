#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import io
import threading
import cv2
import picamera
from picamera.array import PiRGBArray
import numpy as np

class Camera(object):
    thread = None  # background thread that reads frames from camera
    thread2 = None  # background thread that reads frames from camera
    frame = 1  # current frame is stored here by background thread
    frameCV2 = None # same, but as a numpy array
    frameCV2_cut = None
    last_access = 0  # time of last client access to the camera

    def __init__(cls):
        #print ("Init!!!")
        pass#cls.video = cv2.VideoCapture("http://188.187.119.130:8080/hls/6176/5a2d33233089738ea8ff/playlist.m3u8?tcp")

    def initialize(self):
        if Camera.thread is None:
            # print(' INIT!!')
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frameCV2 is None:
                #print('frameCV2',self.frameCV2)
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        #self.frame = cv2.imencode('.jpg', self.frameCV2)[1].tobytes()
        return self.frame

    def get_frame_for_internal_proc(self): # store frame for cv2 
        Camera.last_access = time.time()
        self.initialize()
        #self.frameCV2 = cv2.imread('dt2/1.jpg')
        return self.frameCV2
        # return self.frameCV2_cut

    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (400,300)#(320, 240) # 480x360
            #####camera.framerate=15
            print('camera.resolution ',camera.resolution )
            camera.hflip = True
            camera.vflip = True
            # let camera warm up
            time.sleep(2)
            rawCapture = PiRGBArray(camera, size=camera.resolution)
            for foo in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
                cls.frameCV2 = foo.array
                cls.frame = cv2.imencode('.jpg', cls.frameCV2)[1].tobytes()
                rawCapture.truncate(0)
                #cls.frameCV2_cut = cv2.cvtColor(cls.frameCV2, cv2.COLOR_BGR2GRAY)
                if time.time() - cls.last_access > 30:
                    print('!BREAK!!')
                    break

        cls.thread = None
