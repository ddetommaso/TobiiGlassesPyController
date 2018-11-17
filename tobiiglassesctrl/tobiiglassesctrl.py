# tobiiglassescontroller.py: A Python controller for Tobii Pro Glasses 2
#
# Copyright (C) 2018  Davide De Tommaso
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

import urllib
import json
import time
import datetime
import threading
import socket
import uuid
import logging as log
import struct
import sys
import netifaces
import select
import IN

socket.IPPROTO_IPV6 = 41

log.basicConfig(format='[%(levelname)s]: %(message)s', level=log.DEBUG)


class TobiiGlassesController():

	def __init__(self, address = None, video_scene = False):
		self.timeout = 1
		self.streaming = False
		self.video_scene = video_scene
		self.udpport = 49152
		self.address = address
		self.iface_name = None

		self.data = {}
		nd = {'ts': -1}
		self.data['mems'] = { 'ac': nd, 'gy': nd }
		self.data['right_eye'] = { 'pc': nd, 'pd': nd, 'gd': nd}
		self.data['left_eye'] = { 'pc': nd, 'pd': nd, 'gd': nd}
		self.data['gp'] = nd
		self.data['gp3'] = nd
		self.data['pts'] = nd

		self.project_id = str(uuid.uuid4())
		self.project_name = "TobiiProGlasses PyController"
		self.project_creation_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		self.recn = 0

		self.KA_DATA_MSG = "{\"type\": \"live.data.unicast\", \"key\": \""+ str(uuid.uuid4()) +"\", \"op\": \"start\"}"
		self.KA_VIDEO_MSG = "{\"type\": \"live.video.unicast\",\"key\": \""+ str(uuid.uuid4()) +"_video\",  \"op\": \"start\"}"

		if self.address is None:
			data, address = self.__discover_device__()
			if address is None:
				quit()
			else:
				try:
					self.address = data["ipv4"]
				except:
					self.address = address
		if "%" in self.address:
			if sys.platform == "win32":
				self.address = self.address.split("%")[0]
			self.iface_name = self.address.split("%")[1]
		self.__set_URL__(self.udpport, self.address)
		if self.__connect__() is False:
			quit()


	def __set_URL__(self, udpport, address):
		if ':' in address:
			self.base_url = 'http://[%s]' % address
		else:
			self.base_url = 'http://' + address
		self.peer = (address, udpport)


	def __del__(self):
		self.close()


	def __mksock__(self):
		iptype = socket.AF_INET
		if ':' in self.peer[0]:
			iptype = socket.AF_INET6
		res = socket.getaddrinfo(self.peer[0], self.peer[1], socket.AF_UNSPEC, socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
		sock = socket.socket(res[0][0], res[0][1], res[0][2])
		try:
			if iptype == socket.AF_INET6 and sys.platform == "linux2":
				sock.setsockopt(socket.SOL_SOCKET, IN.SO_BINDTODEVICE, self.iface_name+'\0')
		except socket.error as e:
			if e.errno == 1:
				log.warning("Binding to a network interface is permitted only for root users.")
				log.warning("Data streaming might not work properly, unless you run the script as root.")
		return sock


	def __send_keepalive_msg__(self, sock, msg):
		while self.streaming:
			sock.sendto(msg, self.peer)
			time.sleep(self.timeout)


	def __grab_data__(self, socket):
		time.sleep(1)
		while self.streaming:
			data, address = socket.recvfrom(1024)
			jdata = json.loads(data)
			self.__refresh_data__(jdata)



	def __refresh_data__(self, jsondata):
		try:
			gy = jsondata['gy']
			ts = jsondata['ts']
			if( (self.data['mems']['gy']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data['mems']['gy'] = jsondata
		except:
			pass

		try:
			ac = jsondata['ac']
			ts = jsondata['ts']
			if( (self.data['mems']['ac']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data['mems']['ac'] = jsondata
		except:
			pass

		try:
			pc = jsondata['pc']
			ts = jsondata['ts']
			eye = jsondata['eye']
			if( (self.data[eye + '_eye']['pc']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data[eye + '_eye']['pc'] = jsondata
		except:
			pass

		try:
			pd = jsondata['pd']
			ts = jsondata['ts']
			eye = jsondata['eye']
			if( (self.data[eye + '_eye']['pd']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data[eye + '_eye']['pd'] = jsondata
		except:
			pass

		try:
			gd = jsondata['gd']
			ts = jsondata['ts']
			eye = jsondata['eye']
			if( (self.data[eye + '_eye']['gd']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data[eye + '_eye']['gd'] = jsondata
		except:
			pass

		try:
			gp = jsondata['gp']
			ts = jsondata['ts']
			if( (self.data['gp']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data['gp'] = jsondata

		except:
			pass

		try:
			gp3 = jsondata['gp3']
			ts = jsondata['ts']
			if( (self.data['gp3']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data['gp3'] = jsondata
		except:
			pass

		try:
			pts = jsondata['pts']
			ts = jsondata['ts']
			if( (self.data['pts']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data['pts'] = jsondata
		except:
			pass

		try:
			pv = jsondata['pv']
			ts = jsondata['ts']
			if( (self.data['pv']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data['pv'] = jsondata
		except:
			pass


	def __start_streaming__(self):
		try:
			self.streaming = True
			self.td = threading.Timer(0, self.__send_keepalive_msg__, [self.data_socket, self.KA_DATA_MSG])
			self.tg = threading.Timer(0, self.__grab_data__, [self.data_socket])
			if self.video_scene:
				self.tv = threading.Timer(0, self.__send_keepalive_msg__, [self.video_socket, self.KA_VIDEO_MSG])
				self.tv.start()
				log.debug("Video streaming started...")
			self.td.start()
			self.tg.start()
			log.debug("Data streaming started...")
		except:
			self.streaming = False
			log.error("An error occurs trying to create the threads for data streaming")


	def __post_request__(self, api_action, data=None):
		url = self.base_url + api_action
		req = urllib2.Request(url)
		req.add_header('Content-Type', 'application/json')
		data = json.dumps(data)
		log.debug("Sending JSON: " + str(data))
		response = urllib2.urlopen(req, data)
		res = response.read()
		log.debug("Response: " + str(res))
		try:
			res = json.loads(res)
		except:
			pass
		return res

	def __get_request__(self, api_action):
		url = self.base_url + api_action
		res = urllib2.urlopen(url)
		data = json.load(res)
		return data

	def __discover_device__(self):
		log.debug("Looking for a Tobii Pro Glasses 2 device ...")
		MULTICAST_ADDR = 'ff02::1'
		PORT = 13006

		for i in netifaces.interfaces():
			if netifaces.ifaddresses(i).has_key(netifaces.AF_INET6):
				if "%" in netifaces.ifaddresses(i)[netifaces.AF_INET6][0]['addr']:
					if_name = netifaces.ifaddresses(i)[netifaces.AF_INET6][0]['addr'].split("%")[1]
					if_idx = socket.getaddrinfo(MULTICAST_ADDR + "%" + if_name, PORT, socket.AF_INET6, socket.SOCK_DGRAM)[0][4][3]
					s6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
					s6.settimeout(8.0)
					s6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_IF, if_idx)
					s6.bind(('::', PORT))
					PORT_OUT = PORT if sys.platform == 'win32' else PORT + 1
					try:
						s6.sendto('{"type":"discover"}', (MULTICAST_ADDR, PORT_OUT))
						log.debug("Discover request sent to %s on interface %s " % ( str((MULTICAST_ADDR, PORT_OUT)),if_name) )
						log.debug("Waiting response from a device ...")
						data, address = s6.recvfrom(1024)
						jdata = json.loads(data)
						log.debug("From: " + address[0] + " " + data)
						log.debug("Tobii Pro Glasses found with address: [%s]" % address[0])
						return (jdata, address[0])
					except:
						log.debug("No device found on interface %s" % if_name)

		log.debug("No device found!")
		return (None, None)

	def __connect__(self):
		log.debug("Connecting to the Tobii Pro Glasses 2 ...")
		self.data_socket = self.__mksock__()
		if self.video_scene:
			self.video_socket = self.__mksock__()
		res = self.wait_until_status_is_ok()
		if res is True:
			log.debug("Tobii Pro Glasses 2 successful connected!")
		else:
			log.error("An error occurs trying to connect to the Tobii Pro Glasses")

		return res

	def __disconnect__(self):
		log.debug("Disconnecting to the Tobii Pro Glasses 2")
		self.data_socket.close()
		if self.video_scene:
			self.video_socket.close()
		log.debug("Tobii Pro Glasses 2 successful disconnected!")
		return True

	def close(self):
		if self.address is not None:
			if self.streaming:
				self.stop_streaming()
			self.__disconnect__()

	def start_streaming(self):
		log.debug("Start streaming ...")
		try:
			self.__start_streaming__()
			log.debug("Data streaming successful started!")
		except:
			log.error("An error occurs trying to connect to the Tobii Pro Glasses")


	def stop_streaming(self):
		log.debug("Stop data streaming ...")
		try:
			if self.streaming:
				self.streaming = False
				self.td.join()
				self.tg.join()
				if self.video_scene:
					self.tv.join()
			log.debug("Data streaming successful stopped!")
		except:
			log.error("An error occurs trying to stop data streaming")

	def wait_until_status_is_ok(self):
		status = self.wait_for_status('/api/system/status', 'sys_status', ['ok'])

		if status == 'ok':
			return True
		else:
			return False

	def is_streaming(self):
		return self.streaming

	def wait_for_status(self, api_action, key, values):
		url = self.base_url + api_action
		running = True
		while running:
			try:
				req = urllib2.Request(url)
				req.add_header('Content-Type', 'application/json')
				response = urllib2.urlopen(req, None)
				data = response.read()
				json_data = json.loads(data)
				if json_data[key] in values:
					running = False
				time.sleep(1)
			except urllib2.URLError as e:
				log.error(e)
				return -1
		return json_data[key]

	def get_project_id(self, project_name):
		project_id = None
		projects = self.__get_request__('/api/projects')
		for project in projects:
			if project['pr_info']['Name'] == project_name:
				project_id = project['pr_id']
		return project_id

	def get_participant_id(self, participant_name):
		participant_id = None
		participants = self.__get_request__('/api/participants')
		for participant in participants:
			if participant['pa_info']['Name'] == participant_name:
				participant_id = participant['pa_id']
		return participant_id

	def get_status(self):
		return self.__get_request__('/api/system/status')

	def get_battery_status(self):
		return self.get_status()['sys_battery']

	def get_battery_level(self):
		return self.get_battery_status()['level']

	def get_battery_remaining_time(self):
		return self.get_battery_status()['remaining_time']

	def get_battery_info(self):
		return ( "Battery info = [ Level: %.2f %% - Remaining Time: %.2f s ]" % (float(self.get_battery_level()), float(self.get_battery_remaining_time())) )

	def get_storage_status(self):
		return self.get_status()['sys_storage']

	def get_storage_remaining_time(self):
		return self.get_storage_status()['remaining_time']

	def get_storage_info(self):
		return ( "Storage info = [ Remaining Time: %.2f s ]" % float(self.get_battery_remaining_time()) )

	def get_recording_status(self):
		return self.get_status()['sys_recording']

	def is_recording(self):
		rec_status = self.get_recording_status()
		if rec_status != {}:
			if rec_status['rec_state'] == "recording":
				return True
		return False

	def get_current_recording_id(self):
		return self.get_recording_status()['rec_id']

	def create_project(self, projectname = "DefaultProjectName"):
		project_id = self.get_project_id(projectname)

		if project_id is None:
			data = {'pr_info' : {'CreationDate': self.project_creation_date, 'EagleId':  str(uuid.uuid5(uuid.NAMESPACE_DNS, projectname.encode('utf-8'))), 'Name': projectname}}
			json_data = self.__post_request__('/api/projects', data)
			log.debug("Project %s created!" % json_data['pr_id'])
			return json_data['pr_id']
		else:
			log.debug("Project %s already exists ..." % project_id)
			return project_id

	def create_participant(self, project_id, participant_name = "DefaultUser", participant_notes = ""):
		participant_id = self.get_participant_id(participant_name)
		self.participant_name = participant_name

		if participant_id is None:
			data = {'pa_project': project_id, 'pa_info': {'EagleId': str(uuid.uuid5(uuid.NAMESPACE_DNS, self.participant_name.encode('utf-8'))), 'Name': self.participant_name, 'Notes': participant_notes}}
			json_data = self.__post_request__('/api/participants', data)
			log.debug("Participant " + json_data['pa_id'] + " created! Project " + project_id)
			return json_data['pa_id']
		else:
			log.debug("Participant %s already exists ..." % participant_id)
			return participant_id

	def create_calibration(self, project_id, participant_id):
		data = {'ca_project': project_id, 'ca_type': 'default', 'ca_participant': participant_id}
		json_data = self.__post_request__('/api/calibrations', data)
		log.debug("Calibration " + json_data['ca_id'] + "created! Project: " + project_id + ", Participant: " + participant_id)
		return json_data['ca_id']

	def wait_until_calibration_is_done(self, calibration_id):
		while True:
			status = self.wait_for_status('/api/calibrations/' + calibration_id + '/status', 'ca_state', ['calibrating', 'calibrated', 'stale', 'uncalibrated', 'failed'])
			log.debug("Calibration status %s" % status)
			if status == 'uncalibrated' or status == 'stale' or status == 'failed':
				log.debug("Calibration %s failed " % calibration_id)
				return False
			elif status == 'calibrated':
				log.debug("Calibration %s successful " % calibration_id)
				return True

	def start_calibration(self, calibration_id):
		self.__post_request__('/api/calibrations/' + calibration_id + '/start')

	def create_recording(self, participant_id, recording_notes = ""):
		self.recn = self.recn + 1
		recording_name = "Recording" + str(self.recn)
		data = {'rec_participant': participant_id, 'rec_info': {'EagleId': str(uuid.uuid5(uuid.NAMESPACE_DNS, self.participant_name.encode('utf-8'))), 'Name': recording_name, 'Notes': recording_notes}}
		json_data = self.__post_request__('/api/recordings', data)
		return json_data['rec_id']

	def wait_for_recording_status(self, recording_id, status_array = ['init', 'starting',
	'recording', 'pausing', 'paused', 'stopping', 'stopped', 'done', 'stale', 'failed']):
		return self.wait_for_status('/api/recordings/' + recording_id + '/status', 'rec_state', status_array)

	def start_recording(self, recording_id):
		self.__post_request__('/api/recordings/' + recording_id + '/start')
		if self.wait_for_recording_status(recording_id, ['recording']) == "recording":
			self.send_recording_info()
			return True
		return False

	def stop_recording(self, recording_id):
		self.__post_request__('/api/recordings/' + recording_id + '/stop')
		return self.wait_for_recording_status(recording_id, ['done']) == "done"

	def pause_recording(self, recording_id):
		self.__post_request__('/api/recordings/' + recording_id + '/pause')
		return self.wait_for_recording_status(recording_id, ['paused']) == "paused"

	def send_event(self, event_type, event_tag = '', wait_until_status_is_ok = False):
		data = {'type': event_type, 'tag': event_tag}
		self.__post_request__('/api/events', data)
		if wait_until_status_is_ok:
			return self.wait_until_status_is_ok()

	def send_variable(self, variable, tag):
		self.send_event('#%s#' % variable, tag)

	def send_recording_info(self):
		config_tags = ''
		config_tags += 'recording_id=%s,' % self.recording_name
		config_tags += 'project_name=%s,' % self.project_name
		config_tags += 'participant_name=%s,' % self.participant_name
		config_tags += 'sd_path=projects/%s/recordings/%s,' % (self.project_id, self.recording_id)
		self.send_variable('recording_config', config_tags)

	def get_data(self):
		return self.data

	def get_address(self):
		return self.address

	def get_configuration(self):
		return self.__get_request__('/api/system/conf')

	def get_video_freq(self):
		return self.get_configuration()['sys_sc_fps']

	def set_video_freq_25(self):
		data = {'sys_sc_fps': 25}
		json_data = self.__post_request__('/api/system/conf/', data)

	def set_video_freq_50(self):
		data = {'sys_sc_fps': 50}
		json_data = self.__post_request__('/api/system/conf/', data)
