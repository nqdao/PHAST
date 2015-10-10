__author__ = 'Nhat-Quang'
import socket
import json
from pprint import pprint

HOST, PORT = '', 6633


def main():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(1)
    print 'Serving HTTP on port %s ...' % PORT
    while True:
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        print "Hello world here!"
        print request
        data = load_jason_file('testData.json')
        # http_response = """\
        # HTTP/1.1 200 OK
        # Hello, World!    """
        http_response = json.dumps(data)
        pprint(data)

        client_connection.sendall(http_response)
        client_connection.close()


def load_jason_file(file_name):
    with open(file_name) as data_file:
            data = json.load(data_file)
    return data


if __name__ == '__main__':
    main()


