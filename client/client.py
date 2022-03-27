import socket
from connection import Connection

def main():

    name = input("Input name: ")

    port = 3369
    ip = input("Input IP")
    running = True

    Connection.connect(ip, port)

    Connection.send(name.encode())
    print(Connection.recv(1024).decode())

if __name__ == '__main__':
    main()
