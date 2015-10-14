__author__ = 'Daniel'
import socket
import json

HOST, PORT, CORE = '', 6633, '10.12.8.3'

class UserCommServer:
	 	 
	
    routes, location, new_route, send_new_route = '','', False
	  	
    def __init__(self):
		  send_new_route
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
            
            client_connection.sendall(result)
            client_connection.close()

   def process_incoming(self,received_json):
		json_resp	
		parsed_json = json.loads(received_json)
		if parsed_json['action'] == 'new_trip':
			#forward to core, await reply, return routes metadata
			routes = coreComm(received_json)
			parse_json = json.loads(routes)
			response = {}
			response['action'] = 'routes'
			if parsed_json['action'] == 'routes':
				options = parsed_json['options']
				for option in options:
					
			#else invalid	
		elif parsed_json['action'] == 'selection':
			#forward to core, await ack, send route_info to user
			json_resp = coreComm(received_json)
		elif parsed_json['action'] == 'location':
			#store, send ack to user

		elif parsed_json['action'] == 'new_route':
			#store new route details, forward to user at next location update

		elif parsed_json['action'] == 'get_location':
			#send location to core
		#else ack or invalid 
		return json_resp
	
	def coreComm(self, message)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((CORE, PORT))	
		s.sendall(json.dumps(message))
		datain = s.recv(1024)
		s.close()
		return datain		
		
def main():
    test = UserCommServer()



if __name__ == '__main__':
    main()


