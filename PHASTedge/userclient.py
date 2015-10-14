__author__ = 'Daniel'
import socket
import json
import sys

# USAGE: python client.py <hostname> <port> <JSON>

HOST = str(sys.argv[1])    # The User Comm host
PORT = int(sys.argv[2])    # The User Comm port

dataout = str(sys.argv[3])	#JSON string containing the user command

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))	

s.sendall(json.dumps(dataout))

datain = s.recv(1024)
s.close()

parsed_json = json.loads(datain)

if parsed_json['action'] == 'routes':
	options = parsed_json['options']
	print "Route No. | Name | Time | Confidence" #to be formatted pretty later, possibly other fields
	for option in options:
		opt_json = json.loads(option)
		steps = opt_json['steps']	    	
		print "%d | %s | %s | %s" % (opt_num, opt_json['summary'], opt_json['duration'], opt_json['confidence'])    	    	  
		
elif parsed_json['action'] == 'route_info':
	#parsed details of the steps.. content tbd	

elif parsed_json['action'] == 'new_route':
	#parsed details of the steps.. content tbd	
# else assume ack or invalid and ignore
	
