__author__ = 'Daniel'
import socket
import json

HOST, PORT, CORE = '', 6633, '10.12.8.3'

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
            received_json = json.loads(client_connection.recv(1024))
            result = self.process_incoming(received_json)
            
            client_connection.sendall(result)
            client_connection.close()

    def process_incoming(self,received_json):
		""" Only processes  
				Incoming from user:  Process request for new trip	
						submit trip details to core, reply to user with route options
		""""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((CORE, PORT))	

		s.sendall(json.dumps(received_json))

		datain = s.recv(1024)
		s.close()
		return datain
		
def main():
    test = CoreServer()


def load_jason_file(file_name):
    with open(file_name) as data_file:
            data = json.load(data_file)
    return data


if __name__ == '__main__':
    main()


