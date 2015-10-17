__author__ = 'Daniel'
import socket
import json
import math
import User
import sys

HOST = ''
MYPORT = 6644
CORE = ''
COREPORT = 6633

class UserCommServer:
	 	
	def __init__(self):	
		self.userlist = [None]*20
		self.routes = [None]*20
		self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.listen_socket.bind((HOST, MYPORT))
		self.listen_socket.listen(1)
		print 'Serving HTTP on port {}...'.format(MYPORT)
		self.run()

	def run(self):
		while True:        
			client_connection, client_address = self.listen_socket.accept()
			received_json = json.loads(client_connection.recv(10000))
			print_json(received_json)
			result = self.process_incoming(received_json)	
			print_json(result)	
			client_connection.sendall(json.dumps(result))
			client_connection.close()

	def process_incoming(self,received_json):
		json_resp = {}
		details = received_json['details']
		user_id = details['user_id']
		if received_json['action'] == 'new_trip':
			#forward to core, await reply, return routes metadata
			reply = self.coreComm(received_json)
			json_resp = {}
			json_resp['action'] = 'routes'
			if reply['action'] == 'routes':
				reply_details = reply['details']
				user_id = reply_details['user_id']
				# print "routes:\n"
				print_json(reply_details['routes'])
				# sys.exit(1)
				self.userlist[user_id] = User.User(reply_details['routes'])			
				new_options = [] 
				for option in reply_details['routes']:
					new_option = {}
					for key in option:
						if (key != 'distance') and (key != 'steps'):
							new_option[key] = option[key]
					new_options.append(new_option)
				json_resp['details'] = { 'user_id' : user_id, 'routes': new_options }
			#else invalid	

		elif received_json['action'] == 'selection':
			#forward to core, await ack, send route_info to user			
			reply = self.coreComm(received_json)
			json_resp = {}
			json_resp['action'] = 'route_info'
			rte_selected = self.userlist[user_id].routes[details['selection']]
			json_resp['details'] = { 'user_id' : user_id, 'route': rte_selected }
			if rte_selected['type'] == 'BIXI':
				# full_route = self.userlist[user_id].routes[]
				# print "route info:\n"
				print_json(rte_selected)	
				total_steps = len(rte_selected["steps"])		
				for i in range(total_steps):
					if rte_selected["steps"][i]["travel_mode"] == "BICYCLING":
						for i in range(i+1,total_steps):
							if rte_selected["steps"][i+1]["travel_mode"] == "WALKING":
								last_bike_step = rte_selected["steps"][i]
								break
						break
				print "last bike step:\n"
				print_json(last_bike_step)
				self.userlist[user_id].dest_bixi = last_bike_step['end_location']

			#else we are done and Core should drop the user and re-use user ID

		elif (received_json['action'] == 'location'):
			json_resp = {}
			self.userlist[user_id].location = received_json["details"]['location']
			if self.checkDone(user_id) and (not self.userlist[user_id].done):
				json_resp['action'] = 'done'
				json_resp['details'] = {"user_id": user_id}	
				self.userlist[user_id].done = True
				reply = self.coreComm(json_resp)
			elif self.userlist[user_id].send_new_route:
				json_resp['action'] = 'new_route'
				json_resp['details'] = { 'user_id' : user_id, 'newroute': self.userlist[user_id].new_route }
				self.userlist[user_id].send_new_route = False				
			else:
				json_resp['action']  = 'ack'
				json_resp['details'] = ''

		elif received_json['action'] == 'new_route':
			#store new route details, forward to user at next location update
			self.userlist[user_id].send_new_route = True
			self.userlist[user_id].new_route = received_json['details']["route"]
			json_resp['action']  = 'ack'
			json_resp['details'] = ''			

		elif received_json['action'] == 'get_location':
			#send location to core
			json_resp['action'] = 'location'
			json_resp['details'] = { 'user_id' : user_id, 'location': self.userlist[user_id].location }
		#else ack or invalid 

		return json_resp

	def checkDone(self,user_id):
		latlong_dist = math.sqrt( (self.userlist[user_id].location["lat"] - self.userlist[user_id].dest_bixi["lat"]) ** 2 
			+ (self.userlist[user_id].location["lng"] - self.userlist[user_id].dest_bixi["lng"]) ** 2 )
		#0.00045 decimal degrees ~50m, assuming flat earth approximation for very small distances
		return latlong_dist < 0.00045 
		

	def coreComm(self, message):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((CORE, COREPORT))	
		print_json(message)
		s.sendall(json.dumps(message))
		datain = s.recv(24000)
		s.close()
		multimessage_test = datain.split()
		if multimessage_test[0] == "fragments":
			datain = self.reassemble_fragments()
		print_json(json.loads(datain))
		return json.loads(datain)

	def reassemble_fragments(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((CORE, COREPORT))
		s.sendall("ack")
		datain = s.recv(1024)
		s.close()
		for i in range(int(multimessage_test[1])-1):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((CORE, COREPORT))	
			print_json(message)
			s.sendall(json.dumps(message))
			datain = s.recv(1024)
			s.close()
		
def main():
    test = UserCommServer()

def print_json(json_object):
    print json.dumps(json_object, indent=4, sort_keys=True)
    print "\n"  



if __name__ == '__main__':
    main()


