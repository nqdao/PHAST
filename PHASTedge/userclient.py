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
print json.dumps(datain)
s.close()	
