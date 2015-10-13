__author__ = 'Daniel'
import socket
import json

HOST, PORT = '', 6633

#Only ever receives a connection when the route has been updated, 
#otherwise all communication done by userclient and processing usercomm server
#responses
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
    if parsed_json['action'] == 'new_route':
			print "Route No. | Confidence | Steps " #to be formatted pretty later
			 for option in options:
				 opt_json = json.loads(option)
				 steps = opt_json['steps']	    	
				 print "%d | %d" % (opt_num, opt_json['confidence'])    	    	  
				 for step in steps:
					details = json.loads(step)
				 	#parsed details of the step.. content tbd
	 response['selection'] = 'ack'
   	
    return response

