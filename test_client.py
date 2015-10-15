__author__ = 'Daniel'
import socket
import json
import sys

# USAGE: python client.py <hostname> <port> <JSON>

HOST = ''  # The remote host
PORT = 6644    # The same port as used by the server

""" The trip details as 
		{ 	"action": "new|select",
			"request" "origin":"",
			"destination":"", 
			"selection":""
		}
"""
def main():
	route_options = get_routes()

	user_id = route_options["details"]["user_id"]

	selected_route = select_route(route_options, user_id, 2)

def get_routes():
	test_locs = {
	    "destination": '370 Queen St W, Toronto, ON',
	    "origin": {
	        "lat": 43.659865,
	        "lng": -79.396703
	    }
	}

	message = {	"action": "new_trip","details": {"user_id" : "","origin" : test_locs["origin"],
		"destination" : test_locs["destination"] }}

	dataout = json.dumps(message)	

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))	

	s.sendall(dataout)

	datain = s.recv(8192)
	s.close()
	parsed_json = json.loads(datain)

	print_json(parsed_json)	

	return parsed_json

def select_route(options,user_id,selection):
	message = {	
		"action": "selection",
		"details": {
			"user_id" : user_id,		
			"selection": selection	}}

	dataout = json.dumps(message)	

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))	

	s.sendall(dataout)

	datain = s.recv(8192)
	s.close()
	parsed_json = json.loads(datain)

	print_json(parsed_json)	

	return parsed_json



def print_json(json_object):
    print json.dumps(json_object, indent=4, sort_keys=True)
    print "\n"

if __name__=="__main__":
	main()