__author__ = 'Nhat-Quang'
import socket
import json

test_locs = {
			    "destination": '370 Queen St W, Toronto, ON',
			    "origin": {
			        "lat": 43.659865,
			        "lng": -79.396703
			    }
			}

HOST = 'localhost'    # The remote host
PORT = 6633              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall(json.dumps(test_locs))
# data = s.recv(1024)
s.close()
# print 'Received', repr(data)
# print(json.loads(data))
