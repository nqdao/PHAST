__author__ = 'Daniel'
import socket
import json
import sys
import time

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

	print_json(route_options)

	selection = int(raw_input("Make selection from above list [1,4]: ")) - 1

	selected_route = select_route(route_options, user_id, selection)

	move_on_path(selected_route,0.5,user_id)

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

	# print_json(parsed_json)	

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

	# print_json(parsed_json)	

	return parsed_json

def move_on_path(selected_route,timing, user_id):

	tell_server = True
	for step in selected_route["details"]["route"]["steps"]:
		print "{0} from {1} to {2}".format(step["travel_mode"], step["start_location"],step["end_location"])

		if tell_server:
			
			message = {	
							"action": "location",
							"details": {
								"user_id" : user_id,		
								"location": step["end_location"]
							}
						}

			dataout = json.dumps(message)

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST, PORT))	

			s.sendall(dataout)

			datain = s.recv(8192)
			s.close()
			parsed_json = json.loads(datain)

			# {	
			# 	"action": "new_route",
			# 	"details": {
			# 		"user_id" : "",
			# 		"route" :{	
			# 			"summary" : "",	
			# 			"distance": "",
			# 			"duration": "",
			# 			"confidence": "",
			# 			"steps" : [...],
			# 		}
			# 	}
			# }	

			if parsed_json["action"] == "new_route":
				print "{}problem with origin destination, moving to new route{}".format("*"*20+"\n")
				move_on_new_path(timing, user_id)
				break

			if parsed_json["action"] == "done":
				print "finished biking"

		time.sleep(timing)
	

def move_on_new_path():
	pass

def print_json(json_object):
    print json.dumps(json_object, indent=4, sort_keys=True)
    print "\n"

if __name__=="__main__":
	main()