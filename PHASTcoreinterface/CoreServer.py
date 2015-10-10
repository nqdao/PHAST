__author__ = 'Nhat-Quang'
import socket
import json
from pprint import pprint
import uuid
import RoutingThread

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

    def __init__(self):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind((HOST, PORT))
        self.listen_socket.listen(1)
        print 'Serving HTTP on port {}...'.format(PORT)

        self.run()

    def run(self):

        while True:            

            client_connection, client_address = self.listen_socket.accept()
            request = json.loads(client_connection.recv(1024))
            print request
            # print request
            # data = load_jason_file('testData.json')
            # http_response = """\
            # HTTP/1.1 200 OK
            # Hello, World!    """
            # http_response = json.dumps(data)
            self.new_routing(request, uuid.uuid4())
            client_connection.sendall("thanks")
            client_connection.close()


    def new_routing(self,locations,user_id):
        thread = RoutingThread.RoutingThread(user_id,locations)
        thread.start()


def main():
    test = CoreServer()


def load_jason_file(file_name):
    with open(file_name) as data_file:
            data = json.load(data_file)
    return data


if __name__ == '__main__':
    main()


