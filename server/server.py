import socket
from connection import Connection
import threading


def main():
    port = 3369
    running = True
    connections = []

    server = socket.socket()
    server.bind(("localhost", port))
    server.listen(4)
    clients = []

    while running:
        client, address = server.accept()
        con = Connection(client)
        con.getName()
        print("New user called", con.getNames()[0])

    print("Listening on port", port)


if __name__ == '__main__':
    main()
