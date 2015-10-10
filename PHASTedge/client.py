__author__ = 'Nhat-Quang'
import socket
import json

HOST = 'localhost'    # The remote host
PORT = 6633              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall('Hello, world')
data = s.recv(1024)
s.close()
print 'Received', repr(data)
print(json.loads(data))
