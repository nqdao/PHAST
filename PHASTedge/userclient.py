__author__ = 'Daniel'
import socket
import json
import sys

""" USAGE: python client.py <hostname> <port> <JSON>
"""

HOST = str(sys.argv[1])    # The remote host
PORT = int(sys.argv[2])    # The same port as used by the server

trip = str(sys.argv[3])		# The trip details as { "origin":"","destination":""}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))	

s.sendall(json.dumps(trip))

data = s.recv(1024)
s.close()
print 'Received', repr(data)
print (json.loads(data))
