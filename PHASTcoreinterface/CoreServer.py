__author__ = 'Nhat-Quang'
import socket
import json
from pprint import pprint
import Routing

HOST, PORT = '', 6633

"""
    The CoreServer class which will continually listen for information
    being sent by the client on the EDGE and handle the creation of Routing.py threads
    for the determination of routes for users

    inputs: 
    - user's location
    - user's destination

    outputs: 
    - UUID generated for user
    - routing thread spawned with above inputs

    conituing:
    - routing thread saved with UUID
    - passing of location updates from user to associated routing thread
    - removal of association upon thread completion
"""

class CoreServer:

    STATIONS_FILE = "stations.json"
    CLIENT_FILE = "coreclient.json"

    def __init__(self):

        self.outgoing_messages = []
        self.num_users = 0

        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind((HOST, PORT))
        self.listen_socket.listen(1)
        print 'Serving HTTP on port {}...'.format(PORT)

        self.run()


    def run(self):

        while True:
        """ either new user:    {
                                    "action":"new", 
                                    "details":  
                                                {
                                                    "location": {
                                                                    "origin":<origin>, 
                                                                    "destionation": <destination>
                                                                }
                                                }
                                }  

            or update:          {
                                    "action": "update",
                                    "details":  
                                                {
                                                    "user": <UUID>,
                                                    "location": <location>
                                                }
                                }  
        """       

            client_connection, client_address = self.listen_socket.accept()
            received_json = json.loads(client_connection.recv(1024))
            result = self.process_incoming(received_json)
            # print request
            # data = load_jason_file('testData.json')
            # http_response = """\
            # HTTP/1.1 200 OK
            # Hello, World!    """
            # http_response = json.dumps(data)
            client_connection.sendall(result)
            client_connection.close()


    def process_incoming(self,received_json):
        if received_json["action"] == "new":
            return new_routing(received_json["details"])
        else if received_json["action"] == "update":
            return update_routing(received_json["details"])
        else:
            print "Unknown action"

    def new_routing(self,locations):        
        user_id = self.new_user_id()
        processor = Routing.Routing(user_id,self.STATIONS_FILE,locations,self.CLIENT_FILE)
        return user_id

    def update_routing(self,details):
        return "updated"

    def add_outgoing_message(self,message):
        self.outgoing_messages.append(message)

    def new_user_id(self):
        self.num_users = self.num_users + 1
        return self.num_users - 1

def main():
    test = CoreServer()


def load_jason_file(file_name):
    with open(file_name) as data_file:
            data = json.load(data_file)
    return data


if __name__ == '__main__':
    main()


