#!/usr/bin/python
'''
  Author: Ismael Benito Altamirano 
  
  A Simple mjpg stream http server for the Raspberry Pi Camera
  inspired by https://gist.github.com/n3wtron/4624820
  by Igor Maculan - n3wtron@gmail.com
'''

# Imports
import SimpleHTTPServer
import SocketServer
import io
import time
import picamera
import cgi
import logging
import RPi.GPIO as GPIO
from os import curdir, sep 


camera=None

class CamHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			stream=io.BytesIO()
			try:
				start=time.time()
				for foo in camera.capture_continuous(stream,'jpeg'):
					self.wfile.write("--jpgboundary")
					self.send_header('Content-type','image/jpeg')
					self.send_header('Content-length',len(stream.getvalue()))
					self.end_headers()
					self.wfile.write(stream.getvalue())
					stream.seek(0)
					stream.truncate()
					time.sleep(.5)
			except KeyboardInterrupt:
				pass 
			return
		
			
		else:
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			try:
				htmlPage = open(curdir + sep + self.path)
				self.wfile.write(htmlPage.read())
			except IOError:
				errorPage = open(curdir + sep + '404.html')
				#self.wfile.write(errorPage.read())
				self.send_error(404)
			return
	
		
	def do_POST(self):
		logging.warning("======= POST STARTED =======")
		logging.warning(self.headers)
		form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
					 'CONTENT_TYPE':self.headers['Content-Type'],
					 })
		logging.warning("======= POST VALUES =======")
		for item in form.list:
			logging.warning(item)
		logging.warning("\n")
		
		if '1' in form.getlist("led"):
			
			GPIO.output(CAMLED,True) 
		
		elif '2' in form.getlist("led"):
			
			GPIO.output(CAMLED,False)
		
		
		
		
		SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
					

def main():
  global camera
  camera = picamera.PiCamera()
  #camera.resolution = (1280, 960)
  camera.resolution = (640, 480)
  camera.framerate = 24
  
  GPIO.setmode(GPIO.BCM)
  global CAMLED 
  CAMLED = 32
  GPIO.setup(CAMLED, GPIO.OUT, initial=False)   
  
  global img
  
  Handler = CamHandler
  
  try:
    server = SocketServer.TCPServer(('localhost', 8090), Handler)
    print "server started"
    server.serve_forever()
  except KeyboardInterrupt:
    camera.close()
    server.socket.close()
 
if __name__ == '__main__':
  main()
