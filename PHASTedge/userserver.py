__author__ = 'Daniel'
import socket
import json

HOST, PORT = '', 6633

def main():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(1)
    print 'Serving HTTP on port %s ...' % PORT
    while True:
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)        
        print request
	response = self.process_incoming(request)
	       
        client_connection.sendall(response)
        client_connection.close()

main()

def process_incoming(self, received_json):
    response = {}
    parsed_json = json.loads(received_json)
#this all depends on the format of the contents of the json string
    if parsed_json['action'] == 'route_list':
	options = parsed_json['options']
	opt_num = 1
	print "Route No. | Confidence | Steps " #to be formatted pretty later
	for option in options:
	    opt_json = json.loads(option)
	    steps = opt_json['steps']	    	
	    print "%d | %d" % (opt_num, opt_json['confidence'])    	    	  
	    for step in steps:
		details = json.loads(step)
	 	#parsed details of the step.. content tbd

	user_input = raw_input("Select a route: ")	

	response['selection'] = user_input	
    elif: parsed_json['action'] == 'new_route':
	response['selection'] = 'ack'
    #else #error has occured
    return response

