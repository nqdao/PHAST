__author__ = 'Daniel'
import socket
import json
import math

HOST, PORT, CORE = '', 6633, '10.12.8.3'

class UserCommServer:	 	 
	
	routes, location, dest_bixi, new_route, send_new_route = '', '','', '', False
	  	
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
		if received_json['action'] == 'new_trip':
			#forward to core, await reply, return routes metadata
			reply = coreComm(received_json)
			json_resp = {}
			json_resp['action'] = 'routes'

			if reply['action'] == 'routes':
				routes = reply['details']	
				new_options = reply['details']	 
				for option in new_options:
					del option['distance']
					del option['steps']
				json_resp['details'] = new_options
			#else invalid	

		elif received_json['action'] == 'selection':
			#forward to core, await ack, send route_info to user			
			reply = coreComm(received_json)
			json_resp = {}
			json_resp['action'] = 'route_info'
			rte_selected = routes[received_json['selection']]
			steps = rte_selected['steps']		
			json_resp['details'] = 	steps
			last_bike_step = steps[steps.length-1]
			dest_bixi = last_bike_step['end_location']

		elif received_json['action'] == 'location':
			json_resp = {}
			location = received_json['location']
			if checkDone():
				json_resp['action'] = 'done'
				json_resp['details'] = ''				
				reply = coreComm(json_resp)
			elif send_new_route:
				json_resp['action'] = 'new_route'
				json_resp['details'] = new_route
				send_new_route = False				
			else:
				json_resp['action']  = 'ack'
				json_resp['details'] = ''

		elif received_json['action'] == 'new_route':
			#store new route details, forward to user at next location update
			send_new_route = True
			new_route = received_json['options']			

		elif received_json['action'] == 'get_location':
			#send location to core
			json_resp['action'] = 'location'
			json_resp['details'] = location
		#else ack or invalid 

		return json_resp

	def checkDone():
		latlong_dist = math.sqrt( (location["lat"] - dest_bixi["lat"]) ** 2 + (location["lng"] - dest_bixi["lng"]) ** 2 )
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


