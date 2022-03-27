import socket
from connection import Connection


def main():
    name = input("Input name: ")
    ip = input("Input IP: ")
    port = 3369
    running = True

    con = Connection(ip, port)
    con.connect()
    con.send(name)
    data = con.receive()
    print(data)


if __name__ == '__main__':
    main()
