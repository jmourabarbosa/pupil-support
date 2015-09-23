
from random import randrange,choice,shuffle
from pickle import dump
import zmq
import numpy as np
from multiprocessing import Process, Value,Array
from time import sleep,time
from TrialHandler2 import TrialHandler2


class Pupil(object):

	def __init__(self,port=5000,ip="tcp://127.0.0.1",v_tr=0.5,subject_name="subject"):
		
		#Pupil network setup
		self.port = str(port)
		self.ip=ip

		self.detect = Value('i',0)
		self.fixated = Value('i',1)
		self.finish  = Value('i',1)

		self.v_tr = Value('d',v_tr)
		self.pupil_data=[]
		self.gaze_data=[]

		self.record=Process(target=self.read_pupil,args=(subject_name,))
		self.detector=Process(target=self.detect_sacc)

	def record_start(self):
		self.finish.value=False
		self.record.start()

	def record_stop(self):
		self.finish.value=True

	def test_pupil(self):

		def test_pupil_aux():

			context = zmq.Context()	
			socket = context.socket(zmq.SUB)
			socket.connect(self.ip+":"+self.port)
			socket.setsockopt(zmq.SUBSCRIBE, 'Gaze')

			msg = socket.recv()
			print msg

		p=Process(target=test_pupil_aux)
		p.start()
		sleep(0.1)


		if p.is_alive():
			p.terminate()
			return False

		return True

	def read_pupil(self,log_name="subject"):

		context = zmq.Context()
		socket = context.socket(zmq.SUB)
		socket.connect(self.ip+":"+self.port)
		socket.setsockopt(zmq.SUBSCRIBE, '')
		n_frame=0

		while not self.finish.value:
			msg = socket.recv()
			items = msg.split("\n") 
			msg_type = items.pop(0)   
			if msg_type == 'Pupil':
			    self.pupil_data+=items
	
			else:
				self.gaze_data+=items

		self.write_log(log_name)

	def write_log(self,log_name="subject"):

		if self.record.is_alive:
			self.record_stop()

		p_fid = open(log_name+'_pupil.pickle','w')
		g_fid = open(log_name+'_gaze.pickle','w')

		dump(self.pupil_data,p_fid)
		dump(self.pupil_data,g_fid) 

		p_fid.close()
		g_fid.close()  

	def get_frame(self,socket):

		msg = socket.recv()
		items = msg.split("\n")
		msg_type = items.pop(0)

		msg = socket.recv()
		items = msg.split("\n")
		msg_type = items.pop(0)

		return items

	def detect_sacc(self):

		context = zmq.Context()
		socket = context.socket(zmq.SUB)
		socket.connect(self.ip+":"+self.port)
		socket.setsockopt(zmq.SUBSCRIBE, 'Gaze')

		vel=[]
		n_sacc=0
		while self.detect.value:
			n = 0
			times=[0,0]
			points = [0,0]
			while n<2:
				items = self.get_frame(socket)
				times[n]=float(items[-2].split(":")[1])
				point = items[0].split(":")
				x=point[1].split(",")[0][1:]
				y=point[1].split(",")[1][:-1]
				points[n]=(float(x),float(y))
				n+=1
	    
			(x1,y1) = points[0]
			(x2,y2) = points[1]
			v = np.sqrt((x2-x1)**2 + (y2-y1)**2)/(times[1]-times[0])
			#print v, self.v_tr
	    
			if v > self.v_tr.value:
				n_sacc+=1
				print "saccade: ",n_sacc,v
				self.fixated.value=0
				vel.append(v)

	def detect_sacc_start(self):
		self.detect.value=1
		self.detector.start() 

	def detect_sacc_stop(self):
		self.detect.value=0
		self.detector.terminate()
		self.detector = Process(target=self.detect_sacc)
		self.fixated.value=1

if __name__ == "__main__":

	pupil = Pupil(subject_name="joao")
	p = pupil.test_pupil()

	ti = time()
	tf = time()
	if p:
		pupil.record_start()
		pupil.detect_sacc_start()
		while tf-ti < 2:
			tf = time()

		pupil.record_stop()
		pupil.detect_sacc_stop()