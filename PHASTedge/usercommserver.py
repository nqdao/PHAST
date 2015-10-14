__author__ = 'Daniel'
import socket
import json
import math
import User

HOST, PORT, CORE = '', 6633, '10.12.8.3'

class UserCommServer:	 	 
	
	userlist = [None]*20
	 	
	def __init__(self):
		self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.listen_socket.bind((HOST, PORT))
		self.listen_socket.listen(1)
		print 'Serving HTTP on port {}...'.format(PORT)
		self.run()

	def run(self):
		while True:        
			client_connection, client_address = self.listen_socket.accept()
			received_json = json.loads(client_connection.recv(1024))
			result = self.process_incoming(received_json)		
			client_connection.sendall(json.dumps(result))
			client_connection.close()

	def process_incoming(self,received_json):
		json_resp			
		details = received_json['details']
		user_id = details['user_id']
		if received_json['action'] == 'new_trip':
			#forward to core, await reply, return routes metadata
			reply = coreComm(received_json)
			json_resp = {}
			json_resp['action'] = 'routes'
			if reply['action'] == 'routes':
				reply_details = reply['details']
				user_id = reply_details['user_id']
				userlist[user_id] = User.User(reply_details['routes'])				
				new_options = reply_details['routes'] 
				for option in new_options:
					del option['distance']
					del option['steps']
				json_resp['details'] = { 'user_id' : user_id, 'routes': new_options }
			#else invalid	

		elif received_json['action'] == 'selection':
			#forward to core, await ack, send route_info to user			
			reply = coreComm(received_json)
			json_resp = {}
			json_resp['action'] = 'route_info'
			rte_selected = userlist[user_id].routes[details['selection']]
			json_resp['details'] = { 'user_id' : user_id, 'route': rte_selected }
			last_bike_step = steps[steps.length-1]
			userlist[user_id].dest_bixi = last_bike_step['end_location']

		elif received_json['action'] == 'location':
			json_resp = {}
			userlist[user_id].location = received_json['location']
			if checkDone(user_id):
				json_resp['action'] = 'done'
				json_resp['details'] = ''				
				reply = coreComm(json_resp)
			elif send_new_route:
				json_resp['action'] = 'new_route'
				json_resp['details'] = { 'user_id' : user_id, 'newroute': userlist[user_id].new_route }
				userlist[user_id].send_new_route = False				
			else:
				json_resp['action']  = 'ack'
				json_resp['details'] = ''

		elif received_json['action'] == 'new_route':
			#store new route details, forward to user at next location update
			userlist[user_id].send_new_route = True
			userlist[user_id].new_route = received_json['options']			

		elif received_json['action'] == 'get_location':
			#send location to core
			json_resp['action'] = 'location'
			json_resp['details'] = { 'user_id' : user_id, 'location': userlist[user_id].location }
		#else ack or invalid 

		return json_resp

	def checkDone(self,userid):
		latlong_dist = math.sqrt( (userlist[user_id].location["lat"] - userlist[user_id].dest_bixi["lat"]) ** 2 + (userlist[user_id].location["lng"] - userlist[user_id].dest_bixi["lng"]) ** 2 )
		#0.00045 decimal degrees ~50m, assuming flat earth approximation for very small distances
		return latlong_dist < 0.00045 
		

	def coreComm(self, message):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((CORE, PORT))	
		s.sendall(json.dumps(message))
		datain = s.recv(1024)
		s.close()
		return json.loads(datain)
		
def main():
    test = UserCommServer()



if __name__ == '__main__':
    main()


