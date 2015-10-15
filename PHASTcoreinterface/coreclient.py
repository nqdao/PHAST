__author__ = 'Daniel'
import socket
import json
import sys

# USAGE: python client.py <hostname> <port> <JSON>

HOST = str(sys.argv[1])    # The remote host
PORT = int(sys.argv[2])    # The same port as used by the server

""" The trip details as 
		{ 	"action": "new|select",
			"request" "origin":"",
			"destination":"", 
			"selection":""
		}
"""
dataout = str(sys.argv[3])		

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))	

s.sendall(json.dumps(dataout))

datain = s.recv(8192)
s.close()
parsed_json = json.loads(datain)
print parsed_json	
