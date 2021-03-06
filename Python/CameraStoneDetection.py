#!/usr/bin/env python


#     #############################
#     # GO stone camera detection #
#     #############################
#
#     Licensed under MIT License (MIT)
#
#     Copyright (c) 2018 Daniel Springwald | daniel@springwald.de
#
#     Permission is hereby granted, free of charge, to any person obtaining
#     a copy of this software and associated documentation files (the
#     "Software"), to deal in the Software without restriction, including
#     without limitation the rights to use, copy, modify, merge, publish,
#     distribute, sublicense, and/or sell copies of the Software, and to permit
#     persons to whom the Software is furnished to do so, subject to
#     the following conditions:
#
#     The above copyright notice and this permission notice shall be
#     included in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#     THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#     DEALINGS IN THE SOFTWARE.

import os, sys
from multiprocessing import Process, Manager, Value, Array
from multiprocessing import Pool, Array, Process
from threading import Thread

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/libs" )
sys.path.insert(0,my_path + "/libs/opencv" )

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

class CameraStoneDetection():

	_showImage					= True
	
	_camera						= None
	_rawCapture					= None
	_stream						= None
	
	_cascadeBlack				= None
	_cascadeWhite				= None
	
	_useGrayscale				 = True;
	
	__cameraResolutionX 		= 640*2
	__cameraResolutionY 		= 480*2
	
	_windowName 				= "iGoBot camera";
	
	RectsBlack					= [];
	RectsWhite					= [];
	
	_counter					= 0;

	_process					= None

	_released					= False
	
	# define settings of brightness and contrast
	_settings					= [[50,50],[50,30],[50,80],[60,30],[60,50],[60,80],[70,50]];

	def __init__(self):
		print("camera init")
		
		self.posXFace = -1
		self.posYFace = -1
		self.InitCamera()
		
		#thread = Thread(target=self._update, args=())
		#thread.nice = -20 # -20 high prio, 20 low prio
		#thread.start()
		#thread.nice = -20
		
	def SetCameraSettings(self, settingsNo):
		if (settingsNo >= len(self._settings)):
			return False;
		self._camera.brightness = self._settings[settingsNo][0];
		self._camera.contrast = self._settings[settingsNo][0];
		return True;

	def detect(self, img, cascade):
		rects = cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=3, minSize=(int(self.__cameraResolutionX / 30), int( self.__cameraResolutionY / 30)), flags=cv2.CASCADE_SCALE_IMAGE)
		if len(rects) == 0:
			return []
		#rects[:,2:] += rects[:,:2] # convert from [[x,y,h,b]] to [[x1,y1,x2,y2]]
		return rects

	def draw_rects(self, img, rects, color):
		for x, y, b, h in rects:
			cv2.rectangle(img, (x, y), (x+b, y+h), color, 4)
			
	def InitCamera(self):
		print("camera start")

		cv2.destroyAllWindows()
		cv2.namedWindow(self._windowName, cv2.WINDOW_NORMAL)
		cv2.resizeWindow(self._windowName, 400,300)
		
		# initialize the camera and grab a reference to the raw camera capture
		self._camera = PiCamera()
		self._camera.resolution = (self.__cameraResolutionX, self.__cameraResolutionY)
		self.SetCameraSettings(settingsNo=0);
		#self._camera.contrast = 50;
		#self._camera.brightness = 50;
		self._camera.framerate = 12
		self._rawCapture = PiRGBArray(self._camera, size=(self.__cameraResolutionX, self.__cameraResolutionY))
		#self._stream = self._camera.capture_continuous(self._rawCapture, format="bgr", use_video_port=True)
		
		# allow the camera to warmup
		time.sleep(0.2)
		
		if (self._useGrayscale):
			cascade_black_fn =  "stoneDetection/black-cascade-grayscale.xml"
			cascade_white_fn =  "stoneDetection/white-cascade-grayscale.xml"
		else:
			cascade_black_fn =  "stoneDetection/black-cascade.xml"
			cascade_white_fn =  "stoneDetection/white-cascade.xml"
		self._cascadeBlack = cv2.CascadeClassifier(cascade_black_fn)
		self._cascadeWhite = cv2.CascadeClassifier(cascade_white_fn)

		print("camera start done")
		
	def Update(self):
				
		#global ftimestamp, getFPS
		# keep looping infinitely until the thread is stopped
		#print ("<<<" , self._stream);
	#	for f in self._stream:
		if (True):
			self._camera.capture(self._rawCapture, format="bgr")
			#image = rawCapture.array
			
			self._counter = self._counter+1;
			#print (self._counter);
			if (self._counter > 100):
				self._counter = 0;
			
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			#image = f.array
			image = self._rawCapture.array
			rawImage = image
			if (self._useGrayscale):
				image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			#self_actualFrame = image
			self._rawCapture.truncate(0)
			
			self.RectsBlack = self.detect(image, self._cascadeBlack)
			self.RectsWhite = self.detect(image, self._cascadeWhite)

			if (self._showImage==True):
				key = cv2.waitKey(1) & 0xFF
				self.draw_rects(rawImage, self.RectsBlack, (0, 0, 0))
				self.draw_rects(rawImage, self.RectsWhite, (255, 255, 255))
				cv2.putText(rawImage, str(self._counter), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
				cv2.imshow(self._windowName, rawImage)

			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			#if (self._released == True):
				#self._stream.close()
				#self._rawCapture.close()
				#self._camera.close()
				#return
				
			#time.sleep(0.01) 
			#return;

	def Release(self):
		if (self._released == False):
			self._released = True
			time.sleep(0.5)
			print ("shutting down camera")
			#self._stream.close()
			self._rawCapture.close()
			self._camera.close()

	def __del__(self):
			self.Release()

import atexit
		
def exit_handler():
	testCamera.Release()

if __name__ == '__main__':

	from hardware.Light import Light;
	light = Light();
	light.On();

	testCamera = CameraStoneDetection();
	setting = 0;
	for c in range(0,1000):
		testCamera.Update();
		setting = setting+1;
		if (testCamera.SetCameraSettings(setting)==False):
			setting = 0;
			testCamera.SetCameraSettings(setting);
		time.sleep(1)
	testCamera.Release()

